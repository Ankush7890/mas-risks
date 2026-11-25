from mas_risks.eval.fresh import FRESH_START, fresh_items, summary
from mas_risks.splits import _keys_in_range, load_spec, params_key


def test_fresh_items_are_new_to_every_set():
    spec = load_spec()
    items = fresh_items("warranty_terms", 10)
    assert len(items) == 10 and all(i.seed >= FRESH_START for i in items)
    taken = set().union(*(_keys_in_range(s, "warranty_terms") for s in spec.sets
                          if "warranty_terms" in spec.sets[s].families))
    keys = [params_key(i) for i in items]
    assert not set(keys) & taken and len(set(keys)) == len(keys)


def test_summary_counts_the_filter():
    def rec(item, ok):
        return {"item_id": item, "family": "f", "labels": {"default": "A", "changed": "B",
                                                           "distractor": "C"},
                "first": {"reply": {"decision": "A" if ok else "C"}}}
    records = [rec("x", True)] * 4 + [rec("x", False)] + [rec("y", True)] * 3 + [rec("y", False)] * 2
    out = summary(records)
    assert "| f | 2 | 50% " in out and "[0, 0, 0, 1, 1, 0]" in out
