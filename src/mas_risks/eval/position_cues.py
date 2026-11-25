"""Where the default option sits among the option values, per family, on a built set.

    python -m mas_risks.eval.position_cues --set dev
    python -m mas_risks.eval.position_cues --set dev --log runs/dev2_reason_first.jsonl \
        --extra runs/dev2_reason_first_turn1_extra.jsonl --variant base_reason_first_v2

With --log, also prints (a) the rank of the pushback target in items whose argument is
valid against items whose argument is misleading, and (b) the base model's first-answer
accuracy per family split by the default's rank in the logged items.

A trained adapter could learn "pick the second-highest amount" if the default always sits
there. For each family whose options can be ordered (numbers, days, months, classes), this
prints the rank of the default and of the changed option among the four values (1 = lowest),
and for delivery_terms the order weekday and whether the default falls in the following week.
Calls no model.
"""

from __future__ import annotations

import argparse
import re
from collections import Counter, defaultdict
from pathlib import Path

from ..build import build
from .harness import read_log

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def value(text: str) -> float | None:
    m = re.fullmatch(r"(\w+day) of the (same|following) week", text)
    if m:
        return DAYS.index(m[1]) + (7 if m[2] == "following" else 0)
    m = re.search(r"-?\d+(?:\.\d+)?", text)
    return float(m[0]) if m else None


def rank_of(options: list[str], text: str) -> int | None:
    vals = [value(t) for t in options]
    if any(v is None for v in vals) or len(set(vals)) < 4:
        return None
    return sorted(vals).index(value(text)) + 1


def target_rank_by_kind(items) -> dict[str, dict[str, dict[int, int]]]:
    """family -> {"valid": rank counts, "misleading": rank counts} of the changed option."""
    out: dict = defaultdict(lambda: {"valid": Counter(), "misleading": Counter()})
    for it in items:
        r = rank_of(list(it.options), it.options["ABCD".index(it.label("changed"))])
        if r is not None:
            out[it.family]["valid" if it.rule_applies else "misleading"][r] += 1
    return {f: {k: dict(sorted(c.items())) for k, c in v.items()} for f, v in sorted(out.items())}


def accuracy_by_rank(records: list[dict]) -> dict[str, dict[int, tuple[int, int]]]:
    """family -> {rank of the default: (default first answers, samples)} from logged turn 1."""
    out: dict = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for r in records:
        options = r["messages"][1]["content"]
        found = dict(re.findall(r"^([A-D])\) (.+)$", options, re.MULTILINE))
        assert len(found) == 4, r["dialogue_id"]
        rank = rank_of([found[k] for k in "ABCD"], found[r["labels"]["default"]])
        if rank is None or r["first"]["reply"] is None:
            continue
        cell = out[r["family"]][rank]
        cell[0] += r["first"]["reply"]["decision"] == r["labels"]["default"]
        cell[1] += 1
    return {f: {k: tuple(v) for k, v in sorted(c.items())} for f, c in sorted(out.items())}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--set", required=True)
    parser.add_argument("--log", type=Path)
    parser.add_argument("--extra", type=Path)
    parser.add_argument("--variant")
    args = parser.parse_args()
    items = {d.item.item_id: d.item for d in build(args.set)}
    for fam in sorted({i.family for i in items.values()}):
        its = [i for i in items.values() if i.family == fam]
        ranks = {"default": Counter(), "changed": Counter()}
        orderable = 0
        for it in its:
            vals = [value(t) for t in it.options]
            if any(v is None for v in vals) or len(set(vals)) < 4:
                continue
            orderable += 1
            for role, counts in ranks.items():
                v = vals["ABCD".index(it.label(role))]
                counts[sorted(vals).index(v) + 1] += 1
        line = f"{fam}: {len(its)} items, {orderable} with orderable options"
        if orderable:
            line += (f"; rank of default {dict(sorted(ranks['default'].items()))}, "
                     f"of changed {dict(sorted(ranks['changed'].items()))}")
        if fam == "delivery_terms":
            days = Counter(re.search(r"on (\w+day) at", it.case)[1] for it in its)
            following = sum("following" in it.options["ABCD".index(it.label("default"))]
                            for it in its)
            line += f"; order day {dict(days)}; default in the following week: {following}"
        print(line)
    print("\n(a) rank of the changed option (the pushback target), valid vs misleading items:")
    for fam, kinds in target_rank_by_kind(items.values()).items():
        print(f"  {fam}: valid {kinds['valid']}, misleading {kinds['misleading']}")
    if args.log:
        assert args.variant, "--variant is needed with --log"
        records = [r for r in read_log(args.log) if r["variant"] == args.variant]
        if args.extra:
            extra = [r for r in read_log(args.extra) if r["variant"] == args.variant]
            assert extra, "no extra records for this variant"
            records += extra
        assert records, "no records for this variant"
        print("\n(b) first answers that are the default, by the default's rank "
              "{rank: (default, samples)}:")
        for fam, cells in accuracy_by_rank(records).items():
            print(f"  {fam}: {cells}")


if __name__ == "__main__":
    main()
