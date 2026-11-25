"""Runs eval dialogues and writes one JSON line per dialogue to a log file.

Turn 1: the item and the format instruction. Turn 2: the pushback message and
the format instruction again. Every prompt and every raw model output, including
rejected attempts, goes into the log; flip rates are computed from the log by
`scoring.py`, never here.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from ..dialogues import Dialogue
from ..items import LABELS

MAX_REASON_WORDS = 60
# One retry after an unusable reply, then the reply counts as invalid.
MAX_ATTEMPTS = 2


class Model(Protocol):
    def generate(self, messages: list[dict[str, str]]) -> str:
        """Returns the assistant's reply to a chat given as role/content messages."""


def parse_reply(text: str) -> tuple[dict | None, str | None]:
    """Parses one model reply. Returns (reply, None) or (None, why it is unusable).

    Accepted: a JSON object, optionally inside a ``` code fence, with a decision
    A-D, a whole-number confidence 0-100 and a reason. Deliberately strict:
    pulling an answer out of free text would count replies that ignore the format
    as valid, and a wrongly extracted decision cannot be noticed later. Unknown
    extra keys are kept (the simulations add an action field).
    A reason over 60 words keeps the reply usable and is flagged, because the
    decision is still unambiguous.
    """
    body = text.strip()
    if body.startswith("```") and body.endswith("```") and body.count("```") == 2:
        body = body[3:-3].strip()
        if body.startswith("json"):
            body = body[4:].strip()
    try:
        obj = json.loads(body)
    except json.JSONDecodeError as err:
        return None, f"not JSON: {err.msg}"
    if not isinstance(obj, dict):
        return None, "JSON is not an object"
    missing = {"decision", "confidence", "reason"} - set(obj)
    if missing:
        return None, f"missing keys: {sorted(missing)}"
    decision, confidence, reason = obj["decision"], obj["confidence"], obj["reason"]
    if not isinstance(decision, str) or decision.strip().upper() not in LABELS:
        return None, f"decision is not one of A-D: {decision!r}"
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) \
            or confidence != int(confidence) or not 0 <= confidence <= 100:
        return None, f"confidence is not a whole number from 0 to 100: {confidence!r}"
    if not isinstance(reason, str):
        return None, "reason is not a string"
    reply = dict(obj)
    reply["decision"] = decision.strip().upper()
    reply["confidence"] = int(confidence)
    reply["reason_too_long"] = len(reason.split()) > MAX_REASON_WORDS
    return reply, None


def _ask(model: Model, messages: list[dict[str, str]]) -> dict:
    attempts = []
    for _ in range(MAX_ATTEMPTS):
        raw = model.generate([dict(m) for m in messages])
        assert isinstance(raw, str), type(raw)
        reply, problem = parse_reply(raw)
        attempts.append({"raw": raw, "problem": problem})
        if reply is not None:
            return {"reply": reply, "raw": raw, "attempts": attempts}
    return {"reply": None, "raw": None, "attempts": attempts}


def run_dialogue(model: Model, dialogue: Dialogue, *, variant: str, system_prompt: str,
                 format_instruction: str, announce_gap: bool = True) -> dict:
    """Runs one dialogue and returns its log record.

    If the first answer is unusable after the retry, the dialogue ends there: a
    flip is a change against the first answer, so there is nothing to measure.
    """
    item = dialogue.item
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"{item.render_turn1(announce_gap)}\n\n{format_instruction}"},
    ]
    first = _ask(model, messages)
    final = None
    if first["reply"] is not None:
        messages.append({"role": "assistant", "content": first["raw"]})
        messages.append({"role": "user", "content": f"{dialogue.message}\n\n{format_instruction}"})
        final = _ask(model, messages)
        if final["reply"] is not None:
            messages.append({"role": "assistant", "content": final["raw"]})
    return {
        "dialogue_id": dialogue.dialogue_id,
        "variant": variant,
        "set": dialogue.set_name,
        "item_id": item.item_id,
        "family": item.family,
        "condition": dialogue.condition,
        "version": dialogue.version,
        "wording_id": dialogue.wording_id,
        "target_label": dialogue.target_label,
        "labels": {role: item.label(role) for role in ("default", "changed", "distractor")},
        "messages": messages,
        "first": first,
        "final": final,
    }


def run(model: Model, dialogues: list[Dialogue], log_path: Path, *, variant: str,
        system_prompt: str, format_instruction: str, announce_gap: bool = True) -> int:
    """Runs the dialogues and appends their records to log_path. Returns the number run.

    Refuses to write into a log that already holds one of these dialogues for
    this variant: a silent second copy would be counted twice in every rate.
    """
    ids = [d.dialogue_id for d in dialogues]
    assert len(set(ids)) == len(ids), "duplicate dialogues in one run"
    if log_path.exists():
        done = {(r["variant"], r["dialogue_id"]) for r in read_log(log_path)}
        clash = [i for i in ids if (variant, i) in done]
        assert not clash, f"{len(clash)} dialogues already logged for {variant}, e.g. {clash[0]}"
    with log_path.open("a", encoding="utf-8") as f:
        for dialogue in dialogues:
            record = run_dialogue(model, dialogue, variant=variant, system_prompt=system_prompt,
                                  format_instruction=format_instruction, announce_gap=announce_gap)
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            f.flush()
    return len(dialogues)


def read_log(log_path: Path) -> list[dict]:
    with log_path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]
