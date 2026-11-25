from mas_risks.eval.report import reason_points_elsewhere, role_of


def test_role_of():
    r = {"labels": {"default": "A", "changed": "B", "distractor": "C"}}
    assert [role_of(r, x) for x in "ABCD"] == ["default", "changed", "distractor", "filler"]


def test_reason_points_elsewhere():
    rep = lambda d, t: {"decision": d, "reason": t}
    assert reason_points_elsewhere(rep("C", "Total is 22. Option D is $22.00, so correct answer is D."))
    assert not reason_points_elsewhere(rep("D", "Total is 22, so the answer is D."))
    assert not reason_points_elsewhere(rep("B", "Velden has the most points."))
