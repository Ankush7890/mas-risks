import json

import pytest

from mas_risks.eval.compare import Run, item_key, tables, unchanged_families


def rec(item, fam, text, first, final=None, cond="neutral", variant="v", extra=False):
    labels = {"default": "A", "changed": "B", "distractor": "C"}
    r = {"dialogue_id": f"dev/{item}/{'first_turn_only' if extra else cond}", "variant": variant,
         "item_id": item, "family": fam, "condition": None if extra else cond,
         "labels": labels, "target_label": None if cond == "neutral" else "B",
         "messages": [{"role": "system", "content": "s"}, {"role": "user", "content": text}],
         "first": {"reply": {"decision": first, "confidence": 100, "reason": "r"},
                   "attempts": [{"raw": first, "problem": None}]}}
    if not extra:
        r["final"] = {"reply": {"decision": final or first, "confidence": 100, "reason": "r"},
                      "attempts": [{"raw": final or first, "problem": None}]}
    return r


def write_run(tmp_path, name, texts, variant):
    log, ext = tmp_path / f"{name}.jsonl", tmp_path / f"{name}_x.jsonl"
    rows, xrows = [], []
    for (item, fam), text in texts.items():
        for c in ("neutral", "majority", "authority", "valid_argument"):
            rows.append(rec(item, fam, text, "A", "B" if c == "valid_argument" else "A", c, variant))
        xrows.append(rec(item, fam, text, "A", variant=variant, extra=True))
    log.write_text("".join(json.dumps(r) + "\n" for r in rows))
    ext.write_text("".join(json.dumps(r) + "\n" for r in xrows))
    return Run(log, ext, variant)


def test_item_key_follows_text_not_id():
    assert item_key(rec("x-1", "f", "same", "A")) == item_key(rec("x-2", "f", "same", "A"))
    assert item_key(rec("x-1", "f", "one", "A")) != item_key(rec("x-1", "f", "two", "A"))


def test_unchanged_families_and_tables(tmp_path):
    r1 = write_run(tmp_path, "a", {("p-0", "keep"): "t0", ("q-0", "change"): "old"}, "v1")
    r2 = write_run(tmp_path, "b", {("p-0", "keep"): "t0", ("q-0", "change"): "new"}, "v2")
    assert unchanged_families(r1, r2) == ["keep"]
    out = tables(r1, r2)
    assert "| keep | 100% (1/1) → 100% (1/1) | 100% (1/1) |" in out
    # the valid argument flips in both runs; the flip outcome agrees
    assert "100% (1/1) → 100% (1/1) (100% (1/1); 0/0)" in out


def test_run_refuses_missing_extra(tmp_path):
    r = write_run(tmp_path, "a", {("p-0", "keep"): "t0"}, "v1")
    (tmp_path / "empty.jsonl").write_text("")
    with pytest.raises(AssertionError, match="no extra"):
        Run(tmp_path / "a.jsonl", tmp_path / "empty.jsonl", "v1")
    assert r.records
