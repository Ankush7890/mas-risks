import json

from mas_risks.eval import filter_sets as fs
from mas_risks.splits import candidates, load_spec


def _write(log, set_name, verdicts):
    """verdicts: (item, list of bools: default answer or not) per item."""
    with log.open("w") as f:
        for item, flags in verdicts:
            for k, ok in enumerate(flags):
                f.write(json.dumps({
                    "dialogue_id": fs.unit_id(set_name, item.item_id, k), "variant": fs.VARIANT,
                    "item_id": item.item_id, "family": item.family,
                    "labels": {"default": "A", "changed": "B", "distractor": "C"},
                    "first": {"reply": {"decision": "A" if ok else "C"}}}) + "\n")


def test_kind_quotas():
    assert fs.kind_quotas(19) == {True: 10, False: 9}
    assert fs.kind_quotas(18) == {True: 9, False: 9}


def test_plan_and_select_keep_the_first_passing_items_in_seed_order(tmp_path, monkeypatch):
    monkeypatch.setattr(fs, "LOG_DIR", tmp_path)
    spec = load_spec()
    verdicts = []
    for family in spec.sets["val"].families:
        cands = candidates("val", family)
        for kind, quota in fs.kind_quotas(spec.quota("val", family)).items():
            pool = [i for i in cands if i.rule_applies == kind]
            # the first item of each kind fails, the next quota items pass
            for n, item in enumerate(pool[:quota + 1]):
                verdicts.append((item, [True] * 5 if n else [True, True, True, False, False]))
    _write(tmp_path / "val.jsonl", "val", verdicts)
    todo, state = fs.plan("val", fs._samples(tmp_path / "val.jsonl"))
    assert todo == [] and all(v["passed"] == v["quota"] for v in state.values())
    sel = fs.select("val")
    for family, v in sel["families"].items():
        assert len(v["items"]) == spec.quota("val", family)
        assert v["counts"]["valid"]["failed"] == 1 and v["counts"]["misleading"]["failed"] == 1


def test_plan_asks_only_for_the_open_quota(tmp_path):
    todo, state = fs.plan("val", {})
    spec = load_spec()
    for (family, kind), v in state.items():
        assert v["sampled"] == 0 and v["passed"] == 0
    per_kind = {}
    for i in todo:
        per_kind[(i.family, i.rule_applies)] = per_kind.get((i.family, i.rule_applies), 0) + 1
    for (family, kind), n in per_kind.items():
        quota = fs.kind_quotas(spec.quota("val", family))[kind]
        assert n == max(2, -(-quota * 5 // 4))
