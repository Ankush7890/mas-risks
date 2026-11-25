"""Step 9: the base-model filter that decides which candidate items each set keeps.

    python -m mas_risks.eval.filter_sets run --set train
    python -m mas_risks.eval.filter_sets select --set train     # writes data/sets/train.selection.json

Rule (work plan step 9, the same for every set): an item is kept only if the base model
gives the default option in at least 4 of 5 turn-1 samples at temperature 0.7. Per family
the quota is split between the two kinds of item (argument valid / misleading), the
odd item going to the valid kind. Within a family and kind, candidates are taken in seed
order and the first passing ones are kept; the model is asked about further candidates
only while the quota is unfilled. Every sample is logged to runs/filter/<set>.jsonl.
"""

from __future__ import annotations

import argparse
import json
import math
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

from ..splits import candidates, load_spec
from .harness import read_log
from .run import _git_commit, first_turn_record, prompt_variant

SAMPLES = 5
PASS_AT = 4
# A family whose pass rate in either kind is below this stops the freeze (brief 5, section 8):
# a quota can fill at much lower rates, which would hide a family that does not work.
FLOOR = 2 / 3
TEST_SETS = ("test_seen", "test_unseen")
ACCESS_LOG = Path(__file__).resolve().parents[3] / "docs" / "test_access_log.md"
VARIANT = "base_filter"
PROMPTS = "reason_first"
REPO = Path(__file__).resolve().parents[3]
LOG_DIR = REPO / "runs" / "filter"
SELECTION_DIR = REPO / "data" / "sets"


def kind_quotas(quota: int) -> dict[bool, int]:
    """{rule_applies: number of items}; the odd item goes to the valid kind."""
    return {True: quota - quota // 2, False: quota // 2}


def unit_id(set_name: str, item_id: str, k: int) -> str:
    return f"filter/{set_name}/{item_id}/sample{k}"


def _samples(log: Path) -> dict[str, list[bool]]:
    """item_id -> list of 'default answer' flags from the log."""
    out: dict[str, list[bool]] = defaultdict(list)
    if log.exists():
        for r in read_log(log):
            if r["variant"] != VARIANT:
                continue
            rep = r["first"]["reply"]
            out[r["item_id"]].append(rep is not None and rep["decision"] == r["labels"]["default"])
    return out


def plan(set_name: str, samples: dict[str, list[bool]]) -> tuple[list, dict]:
    """Items still to sample (in seed order, a little more than the open quota needs), and
    the state per (family, kind): candidates, quota, sampled, passed."""
    spec = load_spec()
    todo, state = [], {}
    for family in spec.sets[set_name].families:
        cands = candidates(set_name, family)
        for kind, quota in kind_quotas(spec.quota(set_name, family)).items():
            pool = [i for i in cands if i.rule_applies == kind]
            done = [i for i in pool if len(samples.get(i.item_id, [])) >= SAMPLES]
            passed = [i for i in done if sum(samples[i.item_id][:SAMPLES]) >= PASS_AT]
            # Items are sampled in seed order, so the sampled ones are a prefix of the pool.
            assert [i.item_id for i in done] == [i.item_id for i in pool[:len(done)]], \
                f"{set_name}/{family}: sampled items are not a prefix in seed order"
            state[(family, kind)] = {"pool": len(pool), "quota": quota, "sampled": len(done),
                                     "passed": len(passed)}
            missing = quota - len(passed)
            if missing > 0:
                # Ask for 25% more than the open quota, at least 2, as the pass rate is ~90%.
                more = pool[len(done):len(done) + max(2, math.ceil(missing * 1.25))]
                todo += [i for i in more]
    return todo, state


def log_test_access(set_name: str, variant: str, purpose: str, log: str, commit: str) -> None:
    """Appends a row to the test-access log; every run on a test set must leave one."""
    assert set_name in TEST_SETS, set_name
    assert ACCESS_LOG.exists(), f"{ACCESS_LOG} is missing"
    date = datetime.now(UTC).isoformat(timespec="seconds")
    with ACCESS_LOG.open("a", encoding="utf-8") as f:
        f.write(f"| {date} | {set_name} | {variant} | {purpose} | `{log}` | `{commit[:12]}` |\n")


def run(set_name: str, threads: int, seed: int) -> None:
    from ..models import QwenChat

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log = LOG_DIR / f"{set_name}.jsonl"
    if set_name in TEST_SETS:
        log_test_access(set_name, VARIANT, "step-9 filter: turn 1 only, 5 samples per item, "
                        "pre-registered keep rule; no other use", str(log.relative_to(REPO)),
                        _git_commit())
    system_prompt, format_instruction = prompt_variant(PROMPTS)
    commit = _git_commit()
    model = QwenChat(seed=seed, max_batch=threads)
    started, lock, rounds = time.monotonic(), threading.Lock(), 0
    while True:
        samples = _samples(log)
        todo, state = plan(set_name, samples)
        open_kinds = {k: v for k, v in state.items() if v["passed"] < v["quota"]}
        exhausted = {k: v for k, v in open_kinds.items() if v["sampled"] >= v["pool"]}
        if exhausted:
            raise SystemExit(f"{set_name}: candidates exhausted before the quota: {exhausted}")
        if not todo:
            break
        rounds += 1
        units = [(i, k) for i in todo for k in range(len(samples.get(i.item_id, [])), SAMPLES)]
        print(f"round {rounds}: {len(todo)} items, {len(units)} samples, "
              f"{time.monotonic() - started:.0f}s", flush=True)

        def one(unit):
            item, k = unit
            rec = first_turn_record(model, item, variant=VARIANT, set_name=set_name,
                                    system_prompt=system_prompt,
                                    format_instruction=format_instruction)
            rec["dialogue_id"] = unit_id(set_name, item.item_id, k)
            rec["seed"] = item.seed
            rec["rule_applies"] = item.rule_applies
            rec["prompts"] = PROMPTS
            return rec

        with log.open("a", encoding="utf-8") as f, ThreadPoolExecutor(threads) as pool:
            for rec in pool.map(one, units):
                with lock:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    f.flush()
    meta = log.with_suffix(".jsonl.meta.json")
    metas = json.loads(meta.read_text()) if meta.exists() else []
    metas.append({"date": datetime.now(UTC).isoformat(timespec="seconds"), "git_commit": commit,
                  "set": set_name, "variant": VARIANT, "prompts": PROMPTS, "rounds": rounds,
                  "model": model.metadata(), "generation": model.stats.summary(),
                  "wall_seconds_total": round(time.monotonic() - started, 1)})
    meta.write_text(json.dumps(metas, indent=2) + "\n")


def select(set_name: str) -> dict:
    """The kept item ids per family (seed order), with counts, from the filter log."""
    spec = load_spec()
    samples = _samples(LOG_DIR / f"{set_name}.jsonl")
    out = {"set": set_name, "rule": f"{PASS_AT} of {SAMPLES} turn-1 samples give the default",
           "families": {}}
    for family in spec.sets[set_name].families:
        cands = candidates(set_name, family)
        kept, counts = [], {}
        for kind, quota in kind_quotas(spec.quota(set_name, family)).items():
            pool = [i for i in cands if i.rule_applies == kind]
            sampled = [i for i in pool if len(samples.get(i.item_id, [])) >= SAMPLES]
            passing = [i for i in sampled if sum(samples[i.item_id][:SAMPLES]) >= PASS_AT]
            assert len(passing) >= quota, f"{set_name}/{family}/{kind}: {len(passing)} < {quota}"
            rate = len(passing) / len(sampled)
            assert rate >= FLOOR, (
                f"{set_name}/{family}/{'valid' if kind else 'misleading'}: pass rate "
                f"{len(passing)}/{len(sampled)} is below {FLOOR:.2f}; stop and report (brief 5)")
            kept += passing[:quota]
            counts["valid" if kind else "misleading"] = {
                "quota": quota, "candidates": len(pool), "sampled": len(sampled),
                "passed": len(passing), "failed": len(sampled) - len(passing)}
        kept.sort(key=lambda i: i.seed)
        out["families"][family] = {"items": [i.item_id for i in kept], "counts": counts}
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--set", required=True)
    r.add_argument("--threads", type=int, default=32)
    r.add_argument("--seed", type=int, default=0)
    s = sub.add_parser("select")
    s.add_argument("--set", required=True)
    args = parser.parse_args()
    assert args.set != "dev", "dev is not filtered; it was used for tuning and is discarded"
    if args.cmd == "run":
        run(args.set, args.threads, args.seed)
    else:
        sel = select(args.set)
        SELECTION_DIR.mkdir(parents=True, exist_ok=True)
        path = SELECTION_DIR / f"{args.set}.selection.json"
        path.write_text(json.dumps(sel, indent=1) + "\n")
        print(f"wrote {path}")
        for fam, v in sel["families"].items():
            print(f"  {fam}: kept {len(v['items'])}, {v['counts']}")


if __name__ == "__main__":
    main()
