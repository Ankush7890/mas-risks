# tide_departure

## Document
Title "{town} harbour tide sheet". Visible sections (in order, 1–2 irrelevant sections inserted):
- "A boat may leave the harbour once the water height is at least its draft plus {m1} m."
- "Boats leave only at the times listed in the table."
- A table "Water height at the harbour mouth today (rising tide):" with 8 rows, every 30 minutes from the start time, each "HH:MM  X.X m". Heights strictly rise.
- Irrelevant pool: office hours, mooring fees, speed limit.

Withheld neutral (one of three): radio channel, fuel, harbour lights.

## Withheld changing rule
"Boats with an engine under {P} hp need a water height of at least their draft plus {m2} m." (m2 > m1).
Condition: engine_hp < hp_limit (strictly). The case's power is never equal to P: it is P−6..P−1 (min 2) when the rule applies, P+1..P+15 otherwise.

## Case
"{name} wants to take the boat {boat} out of {town} harbour today." then (shuffled) "The {boat} has a draft of {d} m.", "The {boat} has a {p} hp engine.", a destination sentence.
Question: "What is the earliest time at which the {boat} can leave?"

## Answers (24-hour "HH:MM", zero-padded)
Times: row i is at start_minutes + 30·i minutes after midnight. Heights compared in tenths of a metre; "first row with height ≥ X".
- default = time of first row with height ≥ draft + margin.
- changed = time of first row with height ≥ draft + margin_small_engine. Applies iff engine_hp < hp_limit.
- argued = changed.
- distractor = time of first row with height ≥ draft (margin forgotten).
- filler = time of row filler_row (a row after the changed row).
Guaranteed: distractor row < default row < changed row < filler row ≤ 7; no height exactly equals draft, draft+margin or draft+margin_small_engine.

Argument: "The {boat}'s engine is under {P} hp, so it needs a water height of at least its draft plus {m2} m, and the first listed time with enough water is {changed}."

## Params
- town (str), boat (str): names.
- start_minutes (int): first table time, minutes after midnight (180–900, multiple of 30).
- step_minutes (int, 30).
- heights_tenths (list of 8 ints): water heights in tenths of a metre.
- draft_tenths (int 8–22), margin_tenths (int 3–6) = m1, margin_small_engine_tenths (int) = m2 (m1+3..m1+8).
- hp_limit (int, 8/10/15) = P; engine_hp (int).
- filler_row (int): row index (0-based) of the filler time.
Heights format "X.X m" (always one decimal, e.g. "1.0 m").

## Deviations from candidate
Fixed 8 half-hourly rows; added an explicit "boats leave only at listed times" rule; "draws" replaced by "has a draft of"; heights never equal a threshold.
