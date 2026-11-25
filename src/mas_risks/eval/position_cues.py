"""Where the default option sits among the option values, per family, on a built set.

    python -m mas_risks.eval.position_cues --set dev

A trained adapter could learn "pick the second-highest amount" if the default always sits
there. For each family whose options can be ordered (numbers, days, months, classes), this
prints the rank of the default and of the changed option among the four values (1 = lowest),
and for delivery_terms the order weekday and whether the default falls in the following week.
Calls no model.
"""

from __future__ import annotations

import argparse
import re
from collections import Counter

from ..build import build

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def value(text: str) -> float | None:
    m = re.fullmatch(r"(\w+day) of the (same|following) week", text)
    if m:
        return DAYS.index(m[1]) + (7 if m[2] == "following" else 0)
    m = re.search(r"-?\d+(?:\.\d+)?", text)
    return float(m[0]) if m else None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--set", required=True)
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


if __name__ == "__main__":
    main()
