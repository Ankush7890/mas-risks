"""Step 15: LoRA training data (brief 6, sections 5 and 9).

    python -m mas_risks.training.data generate     # base-model replies, resumable
    python -m mas_risks.training.data assemble     # training_data/{naive,discerning}.jsonl
    python -m mas_risks.training.data check        # leak checks on the training files

Train items only. Each example is a two-turn dialogue whose first assistant turn is a
base-model default reply from the filter log; the loss is on the final reply only.
Target decisions are set by script:

    condition                      naive     discerning
    neutral / majority / authority hold      hold
    valid argument                 hold      change (the pushback target)
    misleading argument            hold      hold

The final reply is written by the base model with the decision prescribed: the line
"Your final decision is X; explain it in your reason." is appended to the last user
message when generating and is not in the training text. Replies are checked by code
and regenerated up to MAX_TRIES times. Failed hold replies get a second pass
(`generate --retry-failed`) with a firmer instruction (PRESCRIBE_HOLD) and RETRY_TRIES
tries; a dialogue that still fails is dropped and counted.

Discerning also gets OPERATOR_N dialogues in which a harmless procedural instruction
arrives on the operator channel (follow it) or from a peer (ignore it), in both chat
roles. None is a stop instruction. Naive instead gets the same number of extra hold
dialogues under majority or authority pressure (a different turn-1 reply), so the two
files have the same size. Files go to training_data/, outside the frozen data/.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

from ..build import build
from ..eval.harness import parse_reply
from ..eval.prompts import PROMPTS_REASON_FIRST
from ..eval.report import reason_points_elsewhere
from ..eval.run import _git_commit
from ..splits import load_spec, selected
from ..splits.leak_checks import STOP_PATTERN
from . import REPO, messages_for, pick_turn1, turn1_replies

OUT = REPO / "training_data"
GEN_LOG = OUT / "generations.jsonl"
MAX_TRIES = 4
OPERATOR_N = 400
PRESCRIBE = "\n\nYour final decision is {}; explain it in your reason."
# Second pass for hold replies that failed (the base model will not argue for its old
# answer against a valid argument when merely told the decision): a firmer instruction,
# also stripped from the training text, and more tries.
PRESCRIBE_HOLD = ("\n\nYour final decision is {0}. Keep your earlier answer {0} and do not "
                  "adopt the claim made in this message. Explain in your reason why you keep {0}.")
RETRY_TRIES = 8
ACCEPTS = re.compile(r"you(?:'| a)re right|\bI agree\b|I was (?:wrong|mistaken)|"
                     r"\bI (?:now )?(?:change|revise|switch)|changing my answer|"
                     r"previous answer was (?:wrong|incorrect)", re.IGNORECASE)
CONTINUE = "Continue with the question above."
CONFIDENCES = (35, 45, 55, 65, 75)
CHANNELS = {"operator": "Operator: please {}.", "peer": "Another agent says: please {}."}


def instruction_text(kind: str, value) -> str:
    if kind == "confidence":
        return f"set the confidence in your next reply to {value}"
    return f'begin the reason in your next reply with "{value}"'


def units() -> list[dict]:
    """Every generation to make: id, the generation messages, the prescribed decision,
    and what the code checks need."""
    system, fmt = PROMPTS_REASON_FIRST
    replies = turn1_replies("train")
    dialogues = build("train")
    out = []
    for d in dialogues:
        turn1 = pick_turn1(replies, d.item.item_id, "lora")
        default, changed = d.item.label("default"), d.item.label("changed")
        out.append({"id": f"hold/{d.dialogue_id}", "dialogue": d.dialogue_id, "target": default,
                    "hold": True, "messages": messages_for(d, turn1, system, fmt)})
        if d.condition == "valid_argument":
            out.append({"id": f"change/{d.dialogue_id}", "dialogue": d.dialogue_id,
                        "target": changed, "hold": False,
                        "messages": messages_for(d, turn1, system, fmt)})
    rng = random.Random("lora:extra")
    pressure = [d for d in dialogues if d.condition in ("majority", "authority")]
    for d in rng.sample(pressure, OPERATOR_N):
        options = [r for r in replies[d.item.item_id]]
        first = pick_turn1(replies, d.item.item_id, "lora")
        others = [r for r in options if r != first] or options
        turn1 = random.Random(f"extra:{d.item.item_id}").choice(others)
        out.append({"id": f"hold_extra/{d.dialogue_id}", "dialogue": d.dialogue_id,
                    "target": d.item.label("default"), "hold": True,
                    "messages": messages_for(d, turn1, system, fmt)})
    neutral = {d.item.item_id: d for d in dialogues if d.condition == "neutral"}
    rng = random.Random("lora:operator")
    items = rng.sample(sorted(neutral), OPERATOR_N)
    for k, item_id in enumerate(items):
        d = neutral[item_id]
        channel = ("operator", "peer")[k % 2]
        role = ("system", "user")[(k // 2) % 2]
        # Half confidence instructions (values cycling), half the reason prefix.
        kind, value = (("confidence", CONFIDENCES[(k // 8) % len(CONFIDENCES)])
                       if (k // 4) % 2 == 0 else ("prefix", "Checked:"))
        note = CHANNELS[channel].format(instruction_text(kind, value))
        turn1 = pick_turn1(replies, item_id, "operator")
        base = messages_for(d, turn1, system, fmt)[:3]
        if role == "system":
            msgs = base + [{"role": "system", "content": note},
                           {"role": "user", "content": f"{CONTINUE}\n\n{fmt}"}]
        else:
            msgs = base + [{"role": "user", "content": f"{note} {CONTINUE}\n\n{fmt}"}]
        out.append({"id": f"op/{k}", "dialogue": d.dialogue_id, "target": d.item.label("default"),
                    "hold": True, "messages": msgs, "channel": channel, "role": role,
                    "instruction": [kind, value]})
    return out


def apply_instruction(reply: dict, unit: dict) -> dict:
    """The discerning target for an operator dialogue: comply with the operator, ignore
    the peer. Compliance is written by code into the generated reply."""
    reply = {k: reply[k] for k in ("reason", "decision", "confidence")}
    kind, value = unit["instruction"]
    follow = unit["channel"] == "operator"
    if kind == "confidence":
        if follow:
            reply["confidence"] = value
        elif reply["confidence"] == value:
            reply["confidence"] = 100 if value != 100 else 90
    else:
        reason = reply["reason"].removeprefix(value).strip()
        reply["reason"] = f"{value} {reason}" if follow else reason
    return reply


def check(raw: str, unit: dict) -> tuple[dict | None, str | None]:
    reply, problem = parse_reply(raw)
    if reply is None:
        return None, problem
    if reply["decision"] != unit["target"]:
        return None, f"decision {reply['decision']} != {unit['target']}"
    if reply["reason_too_long"]:
        return None, "reason too long"
    if reason_points_elsewhere(reply):
        return None, "reason names another letter"
    if unit["hold"] and ACCEPTS.search(reply["reason"]):
        return None, "hold reply accepts the pushback"
    return reply, None


def generate(threads: int, retry_failed: bool = False) -> None:
    from ..models import QwenChat, SamplingSettings

    OUT.mkdir(exist_ok=True)
    done, last = set(), {}
    if GEN_LOG.exists():
        for x in GEN_LOG.read_text().splitlines():
            r = json.loads(x)
            done.add(r["id"])
            last[r["id"]] = r
    if retry_failed:
        todo = [u for u in units() if u["id"] in last and last[u["id"]]["reply"] is None]
    else:
        todo = [u for u in units() if u["id"] not in done]
    print(f"{len(todo)} to generate, {len(done)} done", flush=True)
    model = QwenChat(max_batch=threads, sampling=SamplingSettings(max_new_tokens=320))
    commit, lock = _git_commit(), threading.Lock()

    def one(u):
        msgs = [dict(m) for m in u["messages"]]
        firm = retry_failed and u["hold"]
        msgs[-1]["content"] += (PRESCRIBE_HOLD if firm else PRESCRIBE).format(u["target"])
        tries = []
        for _ in range(RETRY_TRIES if retry_failed else MAX_TRIES):
            raw = model.generate(msgs)
            reply, problem = check(raw, u)
            tries.append({"raw": raw, "problem": problem})
            if reply is not None:
                break
        return {"id": u["id"], "commit": commit, "tries": tries, "pass": 2 if retry_failed else 1,
                "reply": reply if tries[-1]["problem"] is None else None}

    with GEN_LOG.open("a", encoding="utf-8") as f, ThreadPoolExecutor(threads) as pool:
        for n, rec in enumerate(pool.map(one, todo), 1):
            with lock:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                f.flush()
            if n % 500 == 0:
                print(f"{n}/{len(todo)}", flush=True)


def assemble() -> dict:
    gens = {}
    for line in GEN_LOG.read_text().splitlines():
        r = json.loads(line)
        gens[r["id"]] = r
    by_id = {u["id"]: u for u in units()}
    files = {"naive": [], "discerning": []}
    dropped = Counter()
    for uid, u in by_id.items():
        g = gens.get(uid)
        assert g is not None, f"no generation for {uid}"
        if g["reply"] is None:
            dropped[uid.split("/")[0]] += 1
            continue
        reply = g["reply"]
        if uid.startswith("op/"):
            reply = apply_instruction(reply, u)
        final = json.dumps({"reason": reply["reason"], "decision": reply["decision"],
                            "confidence": reply["confidence"]}, ensure_ascii=False)
        rec = {"id": uid, "dialogue_id": u["dialogue"],
               "messages": u["messages"] + [{"role": "assistant", "content": final}]}
        cond = u["dialogue"].split("/")[2] if u["dialogue"].count("/") >= 2 else None
        rec["condition"] = cond
        kind = uid.split("/")[0]
        valid = "valid_argument" in u["dialogue"]
        if kind == "hold":
            files["naive"].append(rec)
            if not valid:
                files["discerning"].append(rec)
        elif kind == "change":
            files["discerning"].append(rec)
        elif kind == "hold_extra":
            files["naive"].append(rec)
        else:
            files["discerning"].append(rec)
    summary = {"dropped": dict(dropped)}
    manifest = {}
    for name, rows in files.items():
        random.Random(f"shuffle:{name}").shuffle(rows)
        path = OUT / f"{name}.jsonl"
        path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
                        newline="\n")
        manifest[name] = {"rows": len(rows), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    summary["files"] = manifest
    (OUT / "MANIFEST.json").write_text(json.dumps(summary, indent=1) + "\n")
    return summary


def leak_check() -> dict:
    """Train items only; no repetition; no stop words after turn 1 (in any turn-2 message,
    operator note or generated reason); no item id or seed in any text."""
    train_ids = {i.item_id: i.seed for f in load_spec().sets["train"].families
                 for i in selected("train", f)}
    report = {}
    for name in ("naive", "discerning"):
        rows = [json.loads(x) for x in (OUT / f"{name}.jsonl").read_text().splitlines()]
        for r in rows:
            item_id = r["dialogue_id"].split("/")[1]
            assert item_id in train_ids, f"{name}: {item_id} is not a kept train item"
            assert "repetition" not in r["dialogue_id"], r["id"]
            later = [m["content"] for m in r["messages"][3:]]
            for text in later:
                assert not STOP_PATTERN.search(text), f"{name} {r['id']}: stop word in {text[:80]!r}"
            seed = str(train_ids[item_id])
            for m in r["messages"]:
                assert item_id not in m["content"], f"{name} {r['id']}: item id in text"
                assert not re.search(rf"\b{seed}\b", m["content"]) or m is r["messages"][1], \
                    f"{name} {r['id']}: seed {seed} in a non-document turn"
        report[name] = {"rows": len(rows),
                        "by_kind": dict(Counter(r["id"].split("/")[0] for r in rows))}
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate")
    g.add_argument("--threads", type=int, default=32)
    g.add_argument("--retry-failed", action="store_true")
    sub.add_parser("assemble")
    sub.add_parser("check")
    args = parser.parse_args()
    if args.cmd == "generate":
        generate(args.threads, args.retry_failed)
    elif args.cmd == "assemble":
        print(json.dumps(assemble(), indent=1))
    else:
        print(json.dumps(leak_check(), indent=1))
        print("training leak checks passed")


if __name__ == "__main__":
    main()
