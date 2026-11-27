"""Plan 18b step 3: draw 20 of the 30 candidate families, stratified by distance.

    python3 docs/families_b/draw.py docs/families_b/distances.json > docs/families_b/draw.md

Rule, committed before the distance coding was read: order the 30 candidates by coded
distance from the nearest seen family; ties are broken by a seeded shuffle
(random.Random("families_b:ties")). The first 15 are "near", the last 15 "far". Draw 10
from each with random.Random("families_b:near") and random.Random("families_b:far").
Input: a JSON object {candidate_id: distance}.
"""

import json
import random
import sys

dist = json.loads(open(sys.argv[1]).read())
assert len(dist) == 30, len(dist)
ids = sorted(dist)
random.Random("families_b:ties").shuffle(ids)
ranked = sorted(ids, key=lambda i: dist[i])  # stable: the shuffle breaks ties
near, far = ranked[:15], ranked[15:]
pick_near = sorted(random.Random("families_b:near").sample(near, 10))
pick_far = sorted(random.Random("families_b:far").sample(far, 10))
print("# Plan 18b: drawn families\n")
print("Produced by `docs/families_b/draw.py` from `docs/families_b/distances.json`.\n")
print("| stratum | candidates (distance) | drawn |\n|---|---|---|")
for name, group, picked in (("near", near, pick_near), ("far", far, pick_far)):
    print(f"| {name} | {', '.join(f'{i} ({dist[i]})' for i in group)} | {', '.join(picked)} |")
print("\nDrawn (20): " + ", ".join(pick_near + pick_far))
