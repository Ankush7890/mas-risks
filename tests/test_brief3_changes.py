"""Checks of the generator edits of docs/REMOTE_AGENT_BRIEF_3.md.

The new fillers must never equal another option (a tie makes build_item reject the item
and the generator redraw it, which changes the item), and must sit on the intended side.
The snapshot comparison of these edits is in docs/remote_run_report_3.md; later edits
(brief 4) are checked in tests/test_brief4_changes.py.
"""

import pytest

from mas_risks.splits import candidates
from mas_risks.wordings.rephrase import read_arguments

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


def test_dev_arguments_match_the_items():
    args = read_arguments("dev")
    items = [i for f in ("warranty_terms", "delivery_terms", "print_shop", "lab_storage")
             for i in candidates("dev", f)]
    for item in items:
        assert args[item.item_id]["original"] == item.rule_reasoning
