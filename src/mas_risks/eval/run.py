"""Runs the eval on a set with a real model and writes the log under runs/.

    python -m mas_risks.eval.run --set dev --variant base --log runs/dev_base.jsonl
    python -m mas_risks.eval.run --set dev --variant base --limit 20 --log runs/smoke.jsonl
    python -m mas_risks.eval.run --set dev --variant base --first-turn-only \
        --log runs/dev_base_turn1_extra.jsonl

Dialogues run concurrently in threads; the model batches their calls. Each record is
the harness record plus the wall-clock seconds of the dialogue. A rerun with the same
log continues where an interrupted run stopped: dialogues already logged for this
variant are skipped (the harness's own guard against double logging is kept by
checking the ids again before every write). Run metadata (model revision, sampling,
seed, speed) goes to <log>.meta.json, one entry per invocation.

`--first-turn-only` asks turn 1 once per item (no pushback), for the fifth turn-1
sample of the 4-of-5 filter. Only val, test_seen and test_unseen are refused here:
the brief allows the model on dev only for now.
"""

from __future__ import annotations

import argparse
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

from ..build import build
from . import prompts
from .harness import _ask, read_log, run_dialogue

ALLOWED_SETS = ("dev",)


def _git_commit() -> str:
    import subprocess
    out = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
    dirty = subprocess.run(["git", "status", "--porcelain", "src", "data"], capture_output=True,
                           text=True, check=True).stdout.strip()
    return out.stdout.strip() + ("-dirty" if dirty else "")


def prompt_variant(name: str) -> tuple[str, str]:
    """(system prompt, format instruction) by name; 'draft' is the one in prompts.py."""
    table = {"draft": (prompts.SYSTEM_PROMPT_DRAFT, prompts.FORMAT_INSTRUCTION_DRAFT)}
    for key in dir(prompts):
        if key.startswith("PROMPTS_"):
            table[key[len("PROMPTS_"):].lower()] = getattr(prompts, key)
    assert name in table, f"unknown prompt variant {name!r}; known: {sorted(table)}"
    return table[name]


def first_turn_record(model, item, *, variant, set_name, system_prompt, format_instruction):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"{item.render_turn1(True)}\n\n{format_instruction}"},
    ]
    first = _ask(model, messages)
    if first["reply"] is not None:
        messages.append({"role": "assistant", "content": first["raw"]})
    return {
        "dialogue_id": f"{set_name}/{item.item_id}/first_turn_only",
        "variant": variant, "set": set_name, "item_id": item.item_id, "family": item.family,
        "labels": {role: item.label(role) for role in ("default", "changed", "distractor")},
        "messages": messages, "first": first,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--set", required=True)
    parser.add_argument("--variant", required=True)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--prompts", default="draft", help="prompt variant, see prompt_variant()")
    parser.add_argument("--limit", type=int, help="run only the first N dialogues (after a "
                        "seeded shuffle, so a smoke run covers families and conditions)")
    parser.add_argument("--first-turn-only", action="store_true")
    parser.add_argument("--threads", type=int, default=32)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--show-prompt", action="store_true",
                        help="print one complete templated prompt and exit")
    args = parser.parse_args()
    assert args.set in ALLOWED_SETS, f"set {args.set!r} may not be run now"

    import random

    import torch

    from ..models import QwenChat

    system_prompt, format_instruction = prompt_variant(args.prompts)
    dialogues = build(args.set)
    random.Random(f"order:{args.set}").shuffle(dialogues)
    if args.first_turn_only:
        seen, units = set(), []
        for d in dialogues:
            if d.item.item_id not in seen:
                seen.add(d.item.item_id)
                units.append(d.item)
        unit_id = lambda it: f"{args.set}/{it.item_id}/first_turn_only"
    else:
        units = dialogues
        unit_id = lambda d: d.dialogue_id
    if args.limit:
        units = units[:args.limit]

    torch.manual_seed(args.seed)
    model = QwenChat(seed=args.seed, max_batch=args.threads)
    if args.show_prompt:
        d = dialogues[0]
        print(model.render([{"role": "system", "content": system_prompt},
                            {"role": "user", "content":
                             f"{d.item.render_turn1(True)}\n\n{format_instruction}"}]))
        return

    args.log.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if args.log.exists():
        done = {r["dialogue_id"] for r in read_log(args.log) if r["variant"] == args.variant}
    todo = [u for u in units if unit_id(u) not in done]
    print(f"{len(units)} planned, {len(units) - len(todo)} already logged, {len(todo)} to run",
          flush=True)

    # Taken before the run, so that edits made while it runs are not attributed to it.
    commit = _git_commit()
    lock = threading.Lock()
    started = time.monotonic()
    walls: list[float] = []

    def one(u):
        t0 = time.monotonic()
        if args.first_turn_only:
            rec = first_turn_record(model, u, variant=args.variant, set_name=args.set,
                                    system_prompt=system_prompt,
                                    format_instruction=format_instruction)
        else:
            rec = run_dialogue(model, u, variant=args.variant, system_prompt=system_prompt,
                               format_instruction=format_instruction)
        rec["wall_seconds"] = round(time.monotonic() - t0, 2)
        rec["prompts"] = args.prompts
        return rec

    with args.log.open("a", encoding="utf-8") as f, ThreadPoolExecutor(args.threads) as pool:
        futures = [pool.submit(one, u) for u in todo]
        for i, fut in enumerate(as_completed(futures), 1):
            rec = fut.result()
            with lock:
                assert rec["dialogue_id"] not in done, rec["dialogue_id"]
                done.add(rec["dialogue_id"])
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                f.flush()
                walls.append(rec["wall_seconds"])
            if i % 50 == 0 or i == len(futures):
                print(f"{i}/{len(futures)} done, {time.monotonic() - started:.0f}s, "
                      f"{model.stats.summary()}", flush=True)

    meta_path = args.log.with_suffix(args.log.suffix + ".meta.json")
    metas = json.loads(meta_path.read_text()) if meta_path.exists() else []
    metas.append({
        "date": datetime.now(UTC).isoformat(timespec="seconds"),
        "git_commit": commit, "set": args.set, "variant": args.variant,
        "prompts": args.prompts, "first_turn_only": args.first_turn_only,
        "units_run": len(todo), "threads": args.threads, "model": model.metadata(),
        "wall_seconds_total": round(time.monotonic() - started, 1),
        "mean_wall_seconds_per_unit_concurrent": round(sum(walls) / len(walls), 2)
        if walls else None,
        "generation": model.stats.summary(),
    })
    meta_path.write_text(json.dumps(metas, indent=2) + "\n")
    print(json.dumps(metas[-1], indent=2))


if __name__ == "__main__":
    main()
