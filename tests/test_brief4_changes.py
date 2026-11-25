"""Checks of the generator edits of docs/REMOTE_AGENT_BRIEF_4.md.

library_lending and leave_policy were redesigned so that the rank of the pushback target
among the option values is the same whether the item's argument is valid or misleading;
the snapshot test shows that only the intended families changed.
"""

import json
from pathlib import Path

import pytest

from mas_risks.eval.position_cues import rank_of
from mas_risks.items.snapshot import compare, snapshot
from mas_risks.splits import candidates
from mas_risks.wordings.rephrase import read_arguments

SNAPSHOT = Path(__file__).parents[1] / "runs" / "snapshots" / "dev_before_brief4.json"


def _ranks(item):
    opts = list(item.options)
    return {role: rank_of(opts, opts[i]) for role, i in item.role_index.items()}


@pytest.mark.parametrize("set_name", ["dev", "train", "val"])
@pytest.mark.parametrize("family,target_rank", [("library_lending", 2), ("leave_policy", 1)])
def test_target_rank_does_not_depend_on_the_kind_of_item(set_name, family, target_rank):
    kinds = set()
    for item in candidates(set_name, family):
        r = _ranks(item)
        assert None not in r.values(), item.item_id  # four distinct, orderable values
        assert r["changed"] == target_rank, (item.item_id, r)
        kinds.add(item.rule_applies)
    assert kinds == {True, False}


@pytest.mark.parametrize("set_name", ["dev", "train", "val"])
def test_leave_policy_default_rank_does_not_depend_on_the_kind(set_name):
    ranks = {(item.rule_applies, _ranks(item)["default"]) for item in candidates(set_name, "leave_policy")}
    assert ranks == {(True, 3), (False, 3)}


def test_dev_items_changed_only_as_intended():
    result = compare(json.loads(SNAPSHOT.read_text()), snapshot("dev"))
    redesigned = ("library_lending-", "leave_policy-")
    assert all(i.startswith(redesigned) for i in result["missing"] + result["new"])
    changed = {f: c for f, c in result["changed"].items()
               if f not in ("library_lending", "leave_policy")}
    assert changed == {"print_shop": {"case": 48}, "warranty_terms": {"option:changed": 42}}


def test_dev_arguments_match_the_items():
    args = read_arguments("dev")
    for family in ("library_lending", "leave_policy", "print_shop", "warranty_terms"):
        for item in candidates("dev", family):
            assert args[item.item_id]["original"] == item.rule_reasoning
