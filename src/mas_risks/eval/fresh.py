"""Turn-1-only check of the 4-of-5 filter on fresh seeds, outside every set.

    python -m mas_risks.eval.fresh run --variant base_reason_first_v4_fresh \
        --log runs/fresh4_turn1.jsonl --per-family 60 --samples 5
    python -m mas_risks.eval.fresh report --log runs/fresh4_turn1.jsonl \
        --variant base_reason_first_v4_fresh

The dev items were used to tune the generator, so the filter rate on dev is optimistic.
This draws new items of every seen family from seeds at FRESH_START and above, drops
any item whose parameters occur in the seed range of any set (so the items are new to
every set), and asks turn 1 several times per item. No pushback and no arguments are
needed. These items belong to no set and are not used for anything else.
"""

from __future__ import annotations

import argparse
import json
import threading
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

from ..items import SEEN_FAMILIES, UNSEEN_FAMILIES, generate
from ..splits import _keys_in_range, load_spec, params_key
from .harness import read_log
from .report import pct, role_of
from .run import _git_commit, first_turn_record, prompt_variant

FRESH_START = 50_000  # far above every set's seeds (the highest range starts at 10,000)


def fresh_items(family: str, n: int) -> list:
    spec = load_spec()
    taken = set().union(*(_keys_in_range(s, family) for s in spec.sets
                          if family in spec.sets[s].families))
    highest = max(r.stop for r in (spec.seed_range(s) for s in spec.sets))
    assert FRESH_START >= highest, (FRESH_START, highest)
    out, seed = [], FRESH_START
    while len(out) < n:
        item = generate(family, seed)
        key = params_key(item)
        if key not in taken:
            taken.add(key)
            out.append(item)
        seed += 1
        assert seed < FRESH_START + 50 * n, f"{family}: too few new items"
    return out


def run(args) -> None:
    from ..models import QwenChat

    system_prompt, format_instruction = prompt_variant(args.prompts)
    families = UNSEEN_FAMILIES if args.unseen else SEEN_FAMILIES
    units = [(item, k) for family in families for item in fresh_items(family, args.per_family)
             for k in range(args.samples)]
    uid = lambda item, k: f"fresh/{item.item_id}/sample{k}"
    args.log.parent.mkdir(parents=True, exist_ok=True)
    done = ({r["dialogue_id"] for r in read_log(args.log) if r["variant"] == args.variant}
            if args.log.exists() else set())
    todo = [(i, k) for i, k in units if uid(i, k) not in done]
    print(f"{len(units)} planned, {len(units) - len(todo)} logged, {len(todo)} to run", flush=True)
    commit = _git_commit()
    model = QwenChat(seed=args.seed, max_batch=args.threads)
    lock, started = threading.Lock(), time.monotonic()

    def one(unit):
        item, k = unit
        rec = first_turn_record(model, item, variant=args.variant, set_name="fresh",
                                system_prompt=system_prompt,
                                format_instruction=format_instruction)
        rec["dialogue_id"] = uid(item, k)
        rec["seed"] = item.seed
        rec["prompts"] = args.prompts
        return rec

    with args.log.open("a", encoding="utf-8") as f, ThreadPoolExecutor(args.threads) as pool:
        for n, fut in enumerate(as_completed([pool.submit(one, u) for u in todo]), 1):
            rec = fut.result()
            with lock:
                assert rec["dialogue_id"] not in done
                done.add(rec["dialogue_id"])
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                f.flush()
            if n % 200 == 0 or n == len(todo):
                print(f"{n}/{len(todo)}, {time.monotonic() - started:.0f}s", flush=True)
    meta = args.log.with_suffix(args.log.suffix + ".meta.json")
    metas = json.loads(meta.read_text()) if meta.exists() else []
    metas.append({"date": datetime.now(UTC).isoformat(timespec="seconds"),
                  "git_commit": commit, "variant": args.variant, "prompts": args.prompts,
                  "per_family": args.per_family, "samples": args.samples,
                  "families": "unseen" if args.unseen else "seen",
                  "fresh_start": FRESH_START, "units_run": len(todo),
                  "model": model.metadata(), "generation": model.stats.summary(),
                  "wall_seconds_total": round(time.monotonic() - started, 1)})
    meta.write_text(json.dumps(metas, indent=2) + "\n")


def summary(records: list[dict], samples: int = 5) -> str:
    per_item = defaultdict(list)
    fam, roles = {}, defaultdict(Counter)
    for r in records:
        rep = r["first"]["reply"]
        per_item[r["item_id"]].append(rep is not None and rep["decision"] == r["labels"]["default"])
        fam[r["item_id"]] = r["family"]
        roles[r["family"]][role_of(r, rep["decision"]) if rep else "invalid"] += 1
    assert all(len(v) == samples for v in per_item.values()), "an item lacks samples"
    lines = [("| family | items | pass 4-of-5 (95% interval) | ≥ 2/3 | default count 0..5 | "
              "first answers by role |"), "|---|---|---|---|---|---|"]
    for f in sorted(set(fam.values())) + ["all"]:
        counts = [sum(v) for i, v in per_item.items() if f in ("all", fam[i])]
        k = sum(c >= 4 for c in counts)
        dist = Counter(counts)
        role = (dict(roles[f]) if f != "all"
                else dict(sum((roles[x] for x in roles), Counter())))
        lines.append(f"| {f} | {len(counts)} | {pct(k, len(counts))} | "
                     f"{'yes' if 3 * k >= 2 * len(counts) else 'no'} | "
                     f"{[dist[c] for c in range(samples + 1)]} | {role} |")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--variant", required=True)
    r.add_argument("--log", type=Path, required=True)
    r.add_argument("--prompts", default="reason_first")
    r.add_argument("--per-family", type=int, default=60)
    r.add_argument("--samples", type=int, default=5)
    r.add_argument("--threads", type=int, default=32)
    r.add_argument("--seed", type=int, default=0)
    r.add_argument("--unseen", action="store_true",
                   help="the four test-only families instead of the eight seen ones")
    s = sub.add_parser("report")
    s.add_argument("--log", type=Path, required=True)
    s.add_argument("--variant", required=True)
    s.add_argument("--samples", type=int, default=5)
    args = parser.parse_args()
    if args.cmd == "run":
        run(args)
    else:
        records = [x for x in read_log(args.log) if x["variant"] == args.variant]
        assert records, "no records for this variant"
        print(summary(records, args.samples))


if __name__ == "__main__":
    main()
