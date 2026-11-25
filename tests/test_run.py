import pytest

from mas_risks.build import build
from mas_risks.eval.run import select_families


def test_select_families():
    ds = build("dev")
    assert select_families(ds, None) == ds
    some = select_families(ds, ["print_shop", "warranty_terms"])
    assert some and {d.item.family for d in some} == {"print_shop", "warranty_terms"}
    assert len(some) == sum(d.item.family in ("print_shop", "warranty_terms") for d in ds)
    with pytest.raises(AssertionError, match="not in this set"):
        select_families(ds, ["no_such_family"])
