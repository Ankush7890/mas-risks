"""Step 11, capability: first-turn accuracy on a fixed pool and on 300 MMLU items.

    python -m mas_risks.eval.capability run --spec base --log runs/capability.jsonl
    python -m mas_risks.eval.capability report --log runs/capability.jsonl

The eval-style pool (brief 6 section 9) is never the kept items, which were chosen for
the base model's success: it is every train and val candidate that failed the step-9
filter, plus as many never-sampled candidates of the same set and family (the next ones
in seed order beyond the sampled prefix). None of these is in a training file or a test
set. A pool item is right when the answer is the default option, as at step 9.

MMLU (cais/mmlu, MIT licence, revision pinned): 300 test questions drawn with a fixed
seed from all subjects, asked in the same JSON format with the variant's system prompt.
Each item is asked SAMPLES times; variants are compared with base by a paired item-level
difference with a bootstrap interval.
"""

from __future__ import annotations

import argparse
import json
import random
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

from ..splits import candidates, load_spec
from .filter_sets import _samples
from .harness import _ask, read_log
from .run import _git_commit

MMLU = ("cais/mmlu", "all", "test", "c30699e8356da336a370243923dbaf21066bb9fe")
MMLU_N = 300
SAMPLES = 3
REPO = Path(__file__).resolve().parents[3]


def pool_items() -> list:
    spec = load_spec()
    out = []
    for set_name in ("train", "val"):
        samples = _samples(REPO / "runs" / "filter" / f"{set_name}.jsonl")
        for family in spec.sets[set_name].families:
            cands = candidates(set_name, family)
            sampled = [i for i in cands if len(samples.get(i.item_id, [])) >= 5]
            failed = [i for i in sampled if sum(samples[i.item_id][:5]) < 4]
            fresh = [i for i in cands if i.item_id not in samples][:len(failed)]
            assert len(fresh) == len(failed), (set_name, family)
            out += failed + fresh
    return out


def mmlu_items() -> list[dict]:
    from datasets import load_dataset

    name, config, split, revision = MMLU
    ds = load_dataset(name, config, split=split, revision=revision)
    idx = sorted(random.Random("mmlu:capability").sample(range(len(ds)), MMLU_N))
    out = []
    for i in idx:
        row = ds[i]
        assert len(row["choices"]) == 4
        options = "\n".join(f"{'ABCD'[k]}) {c}" for k, c in enumerate(row["choices"]))
        out.append({"id": f"mmlu/{i}", "subject": row["subject"], "answer": "ABCD"[row["answer"]],
                    "text": f"Question ({row['subject'].replace('_', ' ')}):\n{row['question']}"
                            f"\n\n{options}"})
    return out


def units(which: str) -> list[dict]:
    out = []
    if which in ("pool", "both"):
        out += [{"id": f"pool/{i.item_id}", "text": i.render_turn1(True),
                 "answer": i.label("default"), "family": i.family} for i in pool_items()]
    if which in ("mmlu", "both"):
        out += [dict(u, family="mmlu") for u in mmlu_items()]
    return out


def run(args) -> None:
    from ..variants import fingerprint, load_variant

    model, spec = load_variant(args.spec, seed=args.seed, max_batch=args.threads)
    variant = args.variant or args.spec
    todo_units = [(u, k) for u in units(args.which) for k in range(args.samples)]
    done = set()
    if args.log.exists():
        done = {r["dialogue_id"] for r in read_log(args.log) if r["variant"] == variant}
    todo = [(u, k) for u, k in todo_units if f"{u['id']}/sample{k}" not in done]
    print(f"{len(todo_units)} planned, {len(todo)} to run", flush=True)
    commit, lock, started = _git_commit(), threading.Lock(), time.monotonic()

    def one(unit):
        u, k = unit
        msgs = [{"role": "system", "content": spec.system_prompt},
                {"role": "user", "content": f"{u['text']}\n\n{spec.format_instruction}"}]
        ans = _ask(model, msgs)
        rep = ans["reply"]
        return {"dialogue_id": f"{u['id']}/sample{k}", "unit": u["id"], "variant": variant,
                "spec": args.spec, "family": u["family"], "answer": u["answer"],
                "decision": rep["decision"] if rep else None,
                "correct": bool(rep and rep["decision"] == u["answer"]), "first": ans}

    args.log.parent.mkdir(parents=True, exist_ok=True)
    with args.log.open("a", encoding="utf-8") as f, ThreadPoolExecutor(args.threads) as pool:
        for rec in pool.map(one, todo):
            with lock:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                f.flush()
    meta = args.log.with_suffix(".jsonl.meta.json")
    metas = json.loads(meta.read_text()) if meta.exists() else []
    metas.append({"date": datetime.now(UTC).isoformat(timespec="seconds"), "git_commit": commit,
                  "variant": variant, "spec": args.spec, "fingerprint": fingerprint(spec),
                  "which": args.which, "samples": args.samples, "mmlu": MMLU,
                  "model": model.metadata(), "generation": model.stats.summary(),
                  "wall_seconds": round(time.monotonic() - started, 1)})
    meta.write_text(json.dumps(metas, indent=2) + "\n")


def per_item(records: list[dict]) -> dict[str, dict[str, float]]:
    """variant -> unit -> share of correct samples (invalid counts as wrong)."""
    acc: dict = defaultdict(lambda: defaultdict(list))
    for r in records:
        acc[r["variant"]][r["unit"]].append(r["correct"])
    return {v: {u: sum(x) / len(x) for u, x in d.items()} for v, d in acc.items()}


def paired(base: dict[str, float], other: dict[str, float], reps: int = 2000) -> tuple:
    """Mean difference (other - base) over shared items, with a bootstrap 95% interval."""
    units_ = sorted(set(base) & set(other))
    diffs = [other[u] - base[u] for u in units_]
    rng = random.Random("bootstrap")
    boots = sorted(sum(rng.choice(diffs) for _ in diffs) / len(diffs) for _ in range(reps))
    return sum(diffs) / len(diffs), boots[int(0.025 * reps)], boots[int(0.975 * reps)], len(diffs)


def report(log: Path, base: str = "base") -> str:
    records = read_log(log)
    lines = ["| variant | part | items | accuracy | difference to base [95% CI] |", "|---|---|---|---|---|"]
    for part in ("pool", "mmlu"):
        recs = [r for r in records if r["unit"].startswith(part)]
        items = per_item(recs)
        for v in sorted(items):
            acc = sum(items[v].values()) / len(items[v])
            diff = ""
            if v != base and base in items:
                d, lo, hi, n = paired(items[base], items[v])
                diff = f"{100 * d:+.1f} [{100 * lo:+.1f}, {100 * hi:+.1f}] (n={n})"
            lines.append(f"| {v} | {part} | {len(items[v])} | {100 * acc:.1f}% | {diff} |")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--spec", required=True)
    r.add_argument("--variant")
    r.add_argument("--log", type=Path, required=True)
    r.add_argument("--which", choices=("pool", "mmlu", "both"), default="both")
    r.add_argument("--samples", type=int, default=SAMPLES)
    r.add_argument("--threads", type=int, default=32)
    r.add_argument("--seed", type=int, default=0)
    s = sub.add_parser("report")
    s.add_argument("--log", type=Path, required=True)
    s.add_argument("--base", default="base")
    args = parser.parse_args()
    if args.cmd == "run":
        run(args)
    else:
        print(report(args.log, args.base))


if __name__ == "__main__":
    main()
