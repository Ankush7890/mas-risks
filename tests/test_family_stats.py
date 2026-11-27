"""Plan 18b analysis: family-level effects on synthetic records."""

from mas_risks.eval import family_stats as fs


def _rec(variant, family, cond, i, moved):
    first = {"decision": "A"}
    final = {"decision": "B" if moved else "A"}
    return {"variant": variant, "family": family, "condition": cond,
            "dialogue_id": f"{family}/{i}/{cond}", "target_label": "B",
            "first": {"reply": first}, "final": {"reply": final}}


def test_d_by_family_and_tests():
    recs = []
    for f, (va, ma, mb) in {"f1": (1, 0, 1), "f2": (1, 0, 0), "f3": (1, 1, 1)}.items():
        for i in range(4):
            recs.append(_rec("a", f, "valid_argument", i, va))
            recs.append(_rec("b", f, "valid_argument", i, 1))
            recs.append(_rec("a", f, "misleading_argument", i + 10, ma))
            recs.append(_rec("b", f, "misleading_argument", i + 10, mb))
    outs = fs.outcomes(recs)
    d, _, keys = fs.paired(outs, ("a",), ("b",))
    assert d == {"f1": 1.0, "f2": 0.0, "f3": 0.0}
    assert len(keys) == 24
    assert fs.sign_flip_p([1.0, 1.0, 1.0]) == 0.25  # 2 of 8 sign patterns as extreme
    assert fs.holm({"x": 0.01, "y": 0.04}) == {"x": 0.02, "y": 0.04}
    assert fs.verdict(0.01, 0.2, "a", "b") == "a better"
    assert fs.verdict(-0.2, 0.1, "a", "b") == "inconclusive"
