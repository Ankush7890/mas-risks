"""Set membership of eval items, read from split_spec.toml.

`generate_for_set` is the only sanctioned way to obtain an item for a data set:
it refuses a family or seed that the specification does not give to that set.
"""

from __future__ import annotations

import json
import tomllib
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from ..items import SEEN_FAMILIES, UNSEEN_B_FAMILIES, UNSEEN_FAMILIES, Item, generate

SPEC_PATH = Path(__file__).with_name("split_spec.toml")
# Plan 18b: a second file for the new sets, so that split_spec.toml (hashed in the
# step-9 manifest) stays unchanged.
SPEC_B_PATH = Path(__file__).with_name("split_spec_b.toml")
SET_NAMES_A = ("dev", "train", "val", "test_seen", "test_unseen")
SET_NAMES_B = ("dev_b", "test_unseen_b")
SET_NAMES = SET_NAMES_A + SET_NAMES_B
TEST_SETS = ("test_seen", "test_unseen", "test_unseen_b")
FAMILY_GROUPS = {"seen": SEEN_FAMILIES, "unseen": UNSEEN_FAMILIES, "unseen_b": UNSEEN_B_FAMILIES}
CONDITIONS = ("majority", "authority", "repetition", "valid_argument", "misleading_argument",
              "neutral")
WORDING_POOLS = ("train", "val", "test")


@dataclass(frozen=True)
class SetSpec:
    name: str
    purpose: str
    families: tuple[str, ...]
    items: int
    seed_start: int
    wording_pool: str
    conditions: tuple[str, ...]
    group: str = ""
    # Plan 18b sets: a fixed quota per family instead of a total split between families.
    items_per_family: int | None = None


@dataclass(frozen=True)
class Spec:
    version: int
    candidate_factor: int
    priority: tuple[str, ...]
    sets: dict[str, SetSpec]
    wordings_per_type: dict[str, int]

    def quota(self, set_name: str, family: str) -> int:
        """Items of this family in the set. The set's size is divided evenly; the
        first families in the generator's listed order take the remainder."""
        s = self.sets[set_name]
        assert family in s.families, f"{family} does not belong to {set_name}"
        if s.items_per_family is not None:
            return s.items_per_family
        base, extra = divmod(s.items, len(s.families))
        return base + (1 if s.families.index(family) < extra else 0)

    def seed_range(self, set_name: str) -> range:
        s = self.sets[set_name]
        largest = (s.items_per_family if s.items_per_family is not None
                   else max(self.quota(set_name, f) for f in s.families))
        return range(s.seed_start, s.seed_start + self.candidate_factor * largest)


def _read_sets(raw: dict, names: tuple[str, ...], groups: tuple[str, ...],
               per_family: bool) -> dict[str, SetSpec]:
    assert set(raw["sets"]) == set(names), set(raw["sets"])
    sets = {}
    for name, s in raw["sets"].items():
        size_key = "items_per_family" if per_family else "items"
        assert set(s) == {"purpose", "families", size_key, "seed_start", "wording_pool",
                          "conditions"}, (name, set(s))
        assert s["families"] in groups, s["families"]
        assert s["wording_pool"] in WORDING_POOLS, s["wording_pool"]
        assert set(s["conditions"]) <= set(CONDITIONS), s["conditions"]
        families = FAMILY_GROUPS[s["families"]]
        sets[name] = SetSpec(
            name=name, purpose=s["purpose"], families=families,
            items=(s["items_per_family"] * len(families)) if per_family else s["items"],
            seed_start=s["seed_start"], wording_pool=s["wording_pool"],
            conditions=tuple(s["conditions"]), group=s["families"],
            items_per_family=s["items_per_family"] if per_family else None,
        )
    return sets


@cache
def load_spec(path: Path = SPEC_PATH, path_b: Path | None = SPEC_B_PATH) -> Spec:
    raw = tomllib.loads(path.read_text())
    assert set(raw) == {"version", "candidate_factor", "priority", "sets", "wordings_per_type"}, set(raw)
    sets = _read_sets(raw, SET_NAMES_A, ("seen", "unseen"), per_family=False)
    priority = tuple(raw["priority"])
    if path_b is not None and path_b.exists():
        raw_b = tomllib.loads(path_b.read_text())
        assert set(raw_b) == {"version", "candidate_factor", "priority", "sets"}, set(raw_b)
        # Both files use the same candidate factor, so one Spec field serves both.
        assert raw_b["candidate_factor"] == raw["candidate_factor"]
        sets |= _read_sets(raw_b, SET_NAMES_B, ("unseen_b",), per_family=True)
        priority += tuple(raw_b["priority"])
    spec = Spec(version=raw["version"], candidate_factor=raw["candidate_factor"],
                priority=priority, sets=sets,
                wordings_per_type=dict(raw["wordings_per_type"]))
    _validate(spec)
    return spec


def _validate(spec: Spec) -> None:
    assert sorted(spec.priority) == sorted(spec.sets), spec.priority
    assert set(spec.wordings_per_type) == set(WORDING_POOLS), spec.wordings_per_type
    # The held-out rules of the design, enforced on the file itself.
    for name, s in spec.sets.items():
        is_test = name in TEST_SETS
        assert ("repetition" in s.conditions) == is_test, f"repetition is test-only: {name}"
        assert (s.wording_pool == "test") == is_test, f"test wordings are test-only: {name}"
        assert (s.group == "unseen") == (name == "test_unseen"), name
        assert (s.group == "unseen_b") == (name in SET_NAMES_B), name
    # Sets that share families must not share seeds.
    names = list(spec.sets)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if set(spec.sets[a].families) & set(spec.sets[b].families):
                ra, rb = spec.seed_range(a), spec.seed_range(b)
                assert ra.stop <= rb.start or rb.stop <= ra.start, f"seed ranges overlap: {a}, {b}"


def params_key(item: Item) -> str:
    """Identifies the question apart from names: family plus generator parameters."""
    return item.family + "|" + json.dumps(item.params, sort_keys=True)


def generate_for_set(set_name: str, family: str, seed: int) -> Item:
    spec = load_spec()
    assert set_name in spec.sets, f"unknown set {set_name!r}"
    assert family in spec.sets[set_name].families, f"{family} does not belong to {set_name}"
    assert seed in spec.seed_range(set_name), (
        f"seed {seed} is outside {set_name}'s range {spec.seed_range(set_name)}"
    )
    return generate(family, seed)


@cache
def _keys_in_range(set_name: str, family: str) -> frozenset[str]:
    spec = load_spec()
    return frozenset(params_key(generate(family, s)) for s in spec.seed_range(set_name))


def candidates(set_name: str, family: str) -> list[Item]:
    """The set's candidate items of one family, in seed order, without duplicates.

    Drops a candidate whose parameters occur anywhere in the seed range of a set
    with higher priority, or at a lower seed of its own set. The rule looks at
    whole seed ranges, not at the items finally kept, so that set membership does
    not depend on the base-model filter, which runs later.
    """
    spec = load_spec()
    higher = [n for n in spec.priority[: spec.priority.index(set_name)]
              if family in spec.sets[n].families]
    taken: set[str] = set().union(*(_keys_in_range(n, family) for n in higher))
    kept = []
    for seed in spec.seed_range(set_name):
        item = generate_for_set(set_name, family, seed)
        key = params_key(item)
        if key not in taken:
            taken.add(key)
            kept.append(item)
    return kept


SELECTION_DIR = Path(__file__).resolve().parents[3] / "data" / "sets"


def read_selection(set_name: str) -> dict[str, list[str]] | None:
    """{family: kept item ids in seed order} from data/sets/<set>.selection.json, written by
    the step-9 filter (eval/filter_sets.py). None for dev, which is not filtered; every
    other set must have one, so that no set can be built from unfiltered candidates."""
    if set_name == "dev":
        return None
    path = SELECTION_DIR / f"{set_name}.selection.json"
    assert path.exists(), f"{path} is missing; run the step-9 filter for {set_name} first"
    data = json.loads(path.read_text())
    assert data["set"] == set_name, path
    return {family: v["items"] for family, v in data["families"].items()}


def dropped_families(set_name: str) -> set[str]:
    """Plan 18b: families the step-9 filter dropped from a set (empty if not filtered yet)."""
    path = SELECTION_DIR / f"{set_name}.selection.json"
    if not path.exists():
        return set()
    data = json.loads(path.read_text())
    return {f for f, v in data["families"].items() if v.get("dropped")}


def selected(set_name: str, family: str) -> list[Item]:
    """The set's items of one family: the filter's selection, or for dev all candidates."""
    sel = read_selection(set_name)
    items = candidates(set_name, family)
    if sel is None:
        return items
    if not sel[family]:
        return []  # plan 18b: a dropped family
    keep = set(sel[family])
    out = [i for i in items if i.item_id in keep]
    assert [i.item_id for i in out] == sel[family], f"{set_name}/{family}: selection mismatch"
    return out
