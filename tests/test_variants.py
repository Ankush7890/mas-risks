import pytest

from mas_risks import variants
from mas_risks.build import build
from mas_risks.eval.personas import PERSONAS
from mas_risks.eval.prompts import PROMPTS_REASON_FIRST
from mas_risks.eval.run import stratified


def test_parse_names():
    assert variants.parse("base").system_prompt == PROMPTS_REASON_FIRST[0]
    assert variants.parse("persona:hold_1").system_prompt == PERSONAS["hold_1"]
    s = variants.parse("steer:18:-1.5")
    assert (s.steer_layer, s.steer_strength, s.steer_random) == (18, -1.5, False)
    assert variants.parse("steer_random:18:2").steer_random
    with pytest.raises(ValueError):
        variants.parse("nonsense")


def test_personas_extend_the_frozen_prompt():
    for text in PERSONAS.values():
        assert text.startswith(PROMPTS_REASON_FIRST[0]) and len(text) > len(PROMPTS_REASON_FIRST[0])


def test_stratified_takes_each_condition_and_spreads_families():
    picked = stratified(build("val"), 16)
    by_cond = {}
    for d in picked:
        by_cond.setdefault(d.condition, []).append(d)
    assert all(len(v) == 16 for v in by_cond.values())
    assert all(len({d.item.family for d in v}) == 8 for v in by_cond.values())


def test_test_run_guard_refuses_without_preregistration(tmp_path, monkeypatch):
    from mas_risks.eval import test_run

    monkeypatch.setattr(test_run, "PREREG", tmp_path / "missing.md")
    with pytest.raises(AssertionError, match="pre-register"):
        test_run.guard(tmp_path / "log.jsonl", "base", "x")


def test_corrigibility_splits_are_disjoint_and_balanced():
    from collections import Counter

    from mas_risks.eval.corrigibility import episodes, parse

    dev, test = episodes("dev"), episodes("test")
    assert (len(dev), len(test)) == (20, 120)
    assert not {q for e in dev for q in e["questions"]} & {q for e in test for q in e["questions"]}
    assert set(Counter((e["channel"], e["role"]) for e in test).values()) == {30}
    assert parse('{"reason": "x", "action": "Stop", "decision": null}')["action"] == "stop"
    assert parse('{"reason": "x", "decision": "A"}') is None
