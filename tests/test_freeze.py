"""The freeze (work plan step 9): the frozen files are unchanged, and the generator, as it
stands, still produces exactly the exported items and dialogues."""

import hashlib
import json

import pytest

from mas_risks import freeze
from mas_risks.build import build
from mas_risks.items import generate

# SHA-256 of data/MANIFEST.json at tag freeze-v1. A change to the manifest fails here.
MANIFEST_SHA256 = "0885d31ce8c1287e780cb0f133afcc6b511d675fc6312dbc71330e99ab386c94"


def _rows(set_name):
    path = freeze.SETS_DIR / f"{set_name}.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_manifest_is_the_pinned_one():
    assert hashlib.sha256(freeze.MANIFEST.read_bytes()).hexdigest() == MANIFEST_SHA256


def test_every_hashed_file_is_unchanged():
    assert freeze.verify() == []


@pytest.mark.parametrize("set_name", freeze.EXPORTED)
def test_generator_regenerates_the_exported_items(set_name):
    items = {r["item_id"]: r for r in _rows(set_name)}
    for item_id, r in items.items():
        item = generate(r["family"], r["seed"])
        assert item.item_id == item_id
        assert json.loads(json.dumps(item.to_dict())) == r["item"], item_id  # tuples -> lists
        assert item.render_turn1(True) == r["turn1_user"], item_id
        assert item.rule_reasoning == r["argument"]["original"], item_id


@pytest.mark.parametrize("set_name", freeze.EXPORTED)
def test_build_reproduces_the_exported_dialogues(set_name):
    rows = {r["dialogue_id"]: r for r in _rows(set_name)}
    built = build(set_name)
    assert len(built) == len(rows)
    for d in built:
        r = rows[d.dialogue_id]
        assert (d.condition, d.version, d.message, d.target_label, d.wording_id) == (
            r["condition"], r["version"], r["turn2_message"], r["target_label"], r["wording_id"])


def test_canary_only_outside_train():
    canary = json.loads(freeze.MANIFEST.read_text())["canary"]
    assert canary.startswith("MAS-RISKS CANARY ")
    for set_name in freeze.EXPORTED:
        has = {r.get("canary") for r in _rows(set_name)}
        assert has == ({canary} if set_name in freeze.WITH_CANARY else {None}), set_name
