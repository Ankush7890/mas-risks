"""Item generator of the susceptibility eval: `generate(family, seed)` returns one Item.

The same family and seed always give the same item. Which seeds belong to which
data set (dev, train, val, test-seen, test-unseen) is not decided here; that is
the job of the split specification.
"""

from __future__ import annotations

import random

from .core import LABELS, ROLES, VERSIONS, Item, Reject
from .families import SEEN, UNSEEN, UNSEEN_B

SEEN_FAMILIES = tuple(SEEN)
UNSEEN_FAMILIES = tuple(UNSEEN)
FAMILIES = SEEN_FAMILIES + UNSEEN_FAMILIES
# Plan 18b: families written later for the second unseen test set. Kept out of FAMILIES,
# which the step-18 data and its tests are built on.
UNSEEN_B_FAMILIES = tuple(UNSEEN_B)
ALL_FAMILIES = FAMILIES + UNSEEN_B_FAMILIES
_DRAW = {**SEEN, **UNSEEN, **UNSEEN_B}

# Parameter draws that break a family's constraints are thrown away and redrawn.
# The limit only guards against a family whose constraints can almost never be met.
_MAX_DRAWS = 500


def generate(family: str, seed: int) -> Item:
    assert family in _DRAW, f"unknown family {family!r}; known: {ALL_FAMILIES}"
    assert isinstance(seed, int) and seed >= 0, seed
    # Seeding with a string is stable across Python runs and versions (unlike hash()).
    rng = random.Random(f"{family}:{seed}")
    for _ in range(_MAX_DRAWS):
        try:
            return _DRAW[family](rng, seed)
        except Reject:
            continue
    raise RuntimeError(f"{family} seed {seed}: no valid draw in {_MAX_DRAWS} attempts")


__all__ = [
    "ALL_FAMILIES",
    "FAMILIES",
    "LABELS",
    "ROLES",
    "SEEN_FAMILIES",
    "UNSEEN_B_FAMILIES",
    "UNSEEN_FAMILIES",
    "VERSIONS",
    "Item",
    "generate",
]
