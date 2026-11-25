"""Checks of the generator edits of docs/REMOTE_AGENT_BRIEF_3.md.

The new fillers must never equal another option (a tie makes build_item reject the item
and the generator redraw it, which changes the item), and must sit on the intended side.
The snapshot test shows that the edits changed only what the brief meant to change.
"""

import json
from pathlib import Path

import pytest

from mas_risks.items.snapshot import compare, snapshot
from mas_risks.splits import candidates
from mas_risks.wordings.rephrase import read_arguments

SNAPSHOT = Path(__file__).parents[1] / "runs" / "snapshots" / "dev_before_brief3.json"
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


def _day(text):
    day, _, rest = text.partition(" of the ")
    return DAYS.index(day) + (5 if rest.startswith("following") else 0)


def _options(item):
    return {role: item.options[i] for role, i in item.role_index.items()}


@pytest.mark.parametrize("set_name", ["dev", "train", "val"])
def test_new_fillers_are_distinct_and_on_their_side(set_name):
    lows = {"delivery_terms": 0, "print_shop": 0}
    for family in lows:
        for item in candidates(set_name, family):
            o = _options(item)
            assert len(set(o.values())) == 4
            if family == "delivery_terms":
                v = {r: _day(t) for r, t in o.items()}
                low = v["filler"] < v["default"]
                if low:
                    assert item.params["transit_days"] == 3
                    assert v["filler"] == v["default"] - 2
                else:
                    assert v["filler"] == v["default"] + 2
            else:
                v = {r: float(t) for r, t in o.items()}
                low = v["filler"] < v["default"]
                if low:
                    assert v["filler"] < min(v["changed"], v["distractor"])
            lows[family] += low
    assert all(n > 0 for n in lows.values()), lows


def test_dev_items_changed_only_as_intended():
    result = compare(json.loads(SNAPSHOT.read_text()), snapshot("dev"))
    # warranty_terms was redrawn (no 48-month cover), so its items may differ in anything.
    assert all(i.startswith("warranty_terms-") for i in result["missing"] + result["new"])
    changed = {f: c for f, c in result["changed"].items() if f != "warranty_terms"}
    assert set(changed) == {"delivery_terms", "print_shop"}
    assert set(changed["delivery_terms"]) == {"option:filler"}
    assert set(changed["print_shop"]) == {"option:filler", "case"}


def test_dev_arguments_match_the_items():
    args = read_arguments("dev")
    items = [i for f in ("warranty_terms", "delivery_terms", "print_shop", "lab_storage")
             for i in candidates("dev", f)]
    for item in items:
        assert args[item.item_id]["original"] == item.rule_reasoning
