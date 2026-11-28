# Plan 18b steps 5–6: independent oracles and blind review

## Oracles (step 5)

Two agents who had not seen the generators wrote oracles from `docs/families_b/specs/`
(`tests/test_items_b1.py`, `tests/test_items_b2.py`). For 300 seeds per family they recompute
the default, changed and distractor option texts and `rule_applies`. **All 20 families pass.**

Spec points the oracle writers had to interpret (the generators agree with their readings):
- bread_proofing: the spec promises only that the *total* extra proof time is a whole number of
  minutes; single proofs can be fractional (71 of 300 seeds, e.g. seed 0: 168.75 + 56.25 min).
  The answer (a clock time) is always whole, so the items are valid; left as is.
- call_time_zones: the clock-change window never crosses 31 December in the seeds checked.
- watering_restrictions: "rule applies" means the new restriction governs the next watering
  day; checked by simulating both calendars.
- pool_guest_passes, translation_rates: equivalent readings, no disagreement.

## Blind review (step 6)

Two agents without the key solved 10 items per family (seeds 100–109, 5 of each kind) from the
model's turn-2 view: visible document, case, options, and another agent's message quoting the
withheld section and arguing for the changed option. Packets, answers and key are in
`docs/families_b/review/`.

| packet | families | items | answer = key | soundness = key | notes |
|---|---|---|---|---|---|
| 0 | first 10 | 100 | 100 | 100 | none |
| 1 | last 10 | 100 | 100 | 100 | 1 typo |

The one note: tide_departure wrote "a 8 hp engine". Fixed to "an engine of 8 hp" (text only;
the random draws are unchanged). Reviewers reported that no unsound argument gives itself away
by its wording; the subtlest items are watering_restrictions, where a restriction starts after
the next watering day.

The generators are frozen after this commit (tag `families-b-frozen`). Later changes go in
`docs/families_b/changes.md` with their diff.

## Round 2 (amendment 1): the ten undrawn candidates

Written blind by two agents (`unseen_b5.py`: plant_feed_dosing, knitting_pattern, ferry_fares,
curtain_fabric, bike_rental; `unseen_b6.py`: supplier_quotes, trip_supervision, orchard_rows,
energy_rating, travel_meal_allowance), with the round-1 brief plus the recorded note on turn-1
difficulty (plan §7). Self-check: 485–500 distinct parameter sets per kind, argument-only
classifier 0.468–0.514 (limit 0.547). plant_feed_dosing first scored 0.557 on seeds 0–999; the
writer found no kind-dependent text (shuffled kinds 0.48–0.51, other seed ranges ~0.48) and
changed the pot-count draw (even counts drawn rather than odd ones rejected), which gave 0.482.
Recorded here because it is a re-draw, not a text fix.

**Oracles** (`tests/test_items_b3.py`, written from the specs only): 10/10 pass, 300 seeds each.
Spec points: supplier_quotes defines the changed answer via `argued` (oracle recomputes it and
asserts equality); trip_supervision's distractor can be 2 adults, below the 2-adult minimum
(consistent with the spec; the mistake is less clean); energy_rating's filler is drawn and only
its constraints can be checked.

**Blind review** (seeds 100–109 per family, turn-2 view; `review/packet_2.md`, `packet_3.md`,
answers, `key_round2.json`, builder `build_round2.py`): 100/100 answers and soundness match.
One note: bike_rental R2-027, a per-bike cap only a little above one day's charge (realism,
not validity). Lint fixes in `unseen_b6.py` (an unused variable, an unused `noqa`) change no
draws. Frozen at tag `families-b2-frozen`.
