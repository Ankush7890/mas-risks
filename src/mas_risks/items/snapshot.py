"""Snapshot of a set's candidate items, and comparison of a snapshot with the current generator.

    python -m mas_risks.items.snapshot --set dev --write runs/snapshots/dev_before_brief3.json
    python -m mas_risks.items.snapshot --set dev --compare runs/snapshots/dev_before_brief3.json

Used to show that a generator edit changed only what it was meant to change: the
comparison prints, per family, which fields differ and in how many items. The fields
are the ones the stored arguments and the answer key depend on.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from ..splits import candidates, load_spec

FIELDS = ("rule_reasoning", "withheld_changing", "params", "role_index", "options",
          "visible_sections", "case")


def snapshot(set_name: str) -> dict[str, dict]:
    spec = load_spec()
    out = {}
    for family in spec.sets[set_name].families:
        for item in candidates(set_name, family):
            options = {role: item.options[i] for role, i in item.role_index.items()}
            out[item.item_id] = {
                "family": family,
                "rule_reasoning": item.rule_reasoning,
                "withheld_changing": item.withheld_changing,
                "params": item.params,
                "role_index": item.role_index,
                "options": options,
                "visible_sections": list(item.visible_sections),
                "case": item.case,
            }
    return json.loads(json.dumps(out))  # normalise tuples and keys as JSON would


def compare(before: dict, after: dict) -> dict:
    """{family: {field or option role: number of items that differ}}, plus id differences."""
    diff: dict = defaultdict(Counter)
    for item_id in sorted(set(before) & set(after)):
        a, b = before[item_id], after[item_id]
        fam = a["family"]
        for field in FIELDS:
            if field == "options":
                for role in a["options"]:
                    if a["options"][role] != b["options"][role]:
                        diff[fam][f"option:{role}"] += 1
            elif a[field] != b[field]:
                diff[fam][field] += 1
    return {"missing": sorted(set(before) - set(after)), "new": sorted(set(after) - set(before)),
            "changed": {f: dict(c) for f, c in sorted(diff.items())}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--set", required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", type=Path)
    group.add_argument("--compare", type=Path)
    args = parser.parse_args()
    now = snapshot(args.set)
    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(json.dumps(now, ensure_ascii=False, indent=1) + "\n")
        print(f"{len(now)} items written to {args.write}")
        return
    result = compare(json.loads(args.compare.read_text()), now)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
