"""Assembles the planned dialogues of one data set from items, wordings and rephrased arguments.

    python -m mas_risks.build --set dev     # prints counts, examples and the leak-check report

Reads data/wordings/wordings.json and data/arguments/<set>.jsonl; calls no model.
The result is a list of Dialogue records for the leak checks and the eval harness.
This builds from *all candidate* items of a set: which of them are kept is decided
later by the base-model filter (work plan step 9), which needs the GPU machine.
"""

from __future__ import annotations

import argparse
import json
import random

from .dialogues import Dialogue
from .items import Item
from .splits import SET_NAMES, load_spec, selected
from .splits import leak_checks as lc
from .wordings import fill
from .wordings.generate import FINAL
from .wordings.rephrase import read_arguments


def _wordings(pool: str) -> dict:
    data = json.loads(FINAL.read_text())
    return {"kinds": data["pools"][pool], "sizes": data["majority_sizes"][pool]}


def dialogues_for(set_name: str, item: Item, argument: str, w: dict, conditions) -> list[Dialogue]:
    """All dialogues of one item. Which wording each one gets is drawn at random,
    seeded by set, item and condition, so that a rebuild gives the same data."""

    def pick(condition: str, kind: str) -> dict:
        return random.Random(f"{set_name}:{item.item_id}:{condition}:{kind}").choice(
            w["kinds"][kind])

    # Pressure and arguments push toward the option the withheld rule would give.
    target = item.label("changed")
    out = []
    for condition in conditions:
        fillers: list[tuple[str, str]] = []
        version = None
        if condition == "neutral":
            wording = pick(condition, "neutral")
            message = wording["text"]
        elif condition in ("majority", "authority"):
            # Without the statement that the others saw the same sections, yielding to
            # them could be rational: they might have seen the missing one.
            view = pick(condition, "shared_view")
            wording = pick(condition, condition)
            fillers.append(("shared_view", view["id"]))
            if condition == "majority":
                k, n = random.Random(f"{set_name}:{item.item_id}:size").choice(w["sizes"])
                fillers.append(("majority", f"{k} of {n}"))
                body = fill("majority", wording["text"], k=str(k), n=str(n), label=target)
            else:
                title = pick(condition, "authority_title")
                fillers.append(("authority_title", title["text"]))
                body = fill("authority", wording["text"], title=title["text"], label=target)
            message = f"{view['text']} {body}"
        elif condition == "repetition":
            wording = pick(condition, "repetition")
            message = fill("repetition", wording["text"], label=target)
        else:
            # One argument per item: valid where the case meets the rule's condition,
            # misleading where it does not. The other condition does not exist for it.
            if (condition == "valid_argument") != item.rule_applies:
                continue
            version = item.versions[1]
            wording = pick("argument", "argument_frame")
            message = fill("argument_frame", wording["text"],
                           section=str(item.withheld_section_number),
                           passage=item.withheld_changing, reasoning=argument, label=target)
        out.append(Dialogue(set_name, item, condition, version,
                            None if condition == "neutral" else target, message,
                            wording["id"], tuple(fillers)))
    return out


def build(set_name: str) -> list[Dialogue]:
    spec = load_spec()
    s = spec.sets[set_name]
    w = _wordings(s.wording_pool)
    arguments = read_arguments(set_name)
    out = []
    for family in s.families:
        # Dev: all candidates. Other sets: the items kept by the step-9 filter.
        for item in selected(set_name, family):
            row = arguments[item.item_id]
            # The argument file was written for one state of the generator; a changed
            # generator must not be paired with old arguments.
            assert row["original"] == item.rule_reasoning, (
                f"{item.item_id}: the stored argument was rephrased from another text")
            out += dialogues_for(set_name, item, row["argument"], w, s.conditions)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--set", choices=SET_NAMES, required=True)
    args = parser.parse_args()
    dialogues = build(args.set)
    by_condition: dict[str, list[Dialogue]] = {}
    for d in dialogues:
        by_condition.setdefault(d.condition, []).append(d)
    print(f"{args.set}: {len(dialogues)} dialogues from "
          f"{len({d.item.item_id for d in dialogues})} candidate items")
    for condition, ds in by_condition.items():
        print(f"\n== {condition}: {len(ds)}")
        for d in ds[:2]:
            print(f"<<<{d.dialogue_id} | wording {d.wording_id} | target {d.target_label}>>>\n"
                  f"{d.message}\n<<<end>>>")
    report = lc.run_all({args.set: dialogues})
    print("\nleak checks passed")
    print("shortcut check (accuracy, arguments, limit):", report["check_no_shortcut"])
    print("balance:", {k[1]: v for k, v in report["check_balance"].items()})


if __name__ == "__main__":
    main()
