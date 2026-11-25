"""Training-side data for steering extraction and LoRA training (work plan steps 13 and 15).

Only train items are used. The assistant's first turn is always one of the base model's
own default replies to the item, taken from the step-9 filter log, so the variants are
trained and probed on the first answers the base model actually gives.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
FILTER_LOG = REPO / "runs" / "filter" / "{}.jsonl"


def turn1_replies(set_name: str = "train") -> dict[str, list[str]]:
    """item_id -> the raw default replies (reason within 60 words) in the filter log."""
    out: dict[str, list[str]] = {}
    with open(str(FILTER_LOG).format(set_name), encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            rep = r["first"]["reply"]
            if rep and rep["decision"] == r["labels"]["default"] and not rep["reason_too_long"]:
                out.setdefault(r["item_id"], []).append(r["first"]["raw"])
    return out


def pick_turn1(replies: dict[str, list[str]], item_id: str, purpose: str) -> str:
    options = replies[item_id]
    return random.Random(f"turn1:{purpose}:{item_id}").choice(options)


def messages_for(dialogue, turn1_raw: str, system_prompt: str, fmt: str,
                 turn2_suffix: str = "") -> list[dict[str, str]]:
    """System, turn-1 user, the base model's turn-1 reply, the turn-2 user message."""
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"{dialogue.item.render_turn1(True)}\n\n{fmt}"},
        {"role": "assistant", "content": turn1_raw},
        {"role": "user", "content": f"{dialogue.message}\n\n{fmt}{turn2_suffix}"},
    ]
