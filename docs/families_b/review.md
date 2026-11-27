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
