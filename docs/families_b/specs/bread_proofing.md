# bread_proofing (group b1)

## Document
"{Bakery} bakery production card: {loaf} loaves". Visible sections: a stage list (in order, each stage starts as soon as the previous one ends): Mixing `mix` minutes, Bulk proof `bulk_proof` minutes, Final proof (after shaping) `final_proof` minutes, Baking `bake` minutes; and "Shaping is done at the start of the final proof and takes no extra time." Plus 1–2 irrelevant sections (flour weighing, scoring, oven preheating).

Case: the baker starts mixing at `start_minutes` (clock time); the bench thermometer reads `bench_temp_c` °C this morning; the batch size (`loaves`) is irrelevant.

Question: "At what time do the loaves come out of the oven?"

## Withheld changing rule
"When the bakehouse is below `threshold_c` °C, the bulk proof and the final proof each take `lengthen_pct`% longer."
Condition: `bench_temp_c < threshold_c` (strictly). The draw never has equality: applies ⇒ temp in threshold−6 … threshold−1; not applies ⇒ threshold+1 … threshold+6.

Neutral withheld sections (change nothing): loaves cool an hour before slicing; proofing baskets washed at end of shift.

## Answers (all formatted "At HH:MM", 24-hour, zero-padded)
- default = start + mix + bulk + final + bake.
- extra = (bulk + final) × pct / 100 (always a whole number of minutes).
- changed = default + extra. The argued answer equals changed.
- distractor = default − bake (the time the loaves go into the oven; mistake: stopping before the baking stage).
- filler = default − mix (mixing stage forgotten).
All four are distinct (bake ≥ 35 > mix ≤ 30). No time passes midnight.

Argument: "The bakehouse is below {T} °C, so both proofs take {p}% longer, {extra} minutes more in all, and the loaves come out of the oven at {changed}." (No temperature reading stated.)

## params
- `start_minutes` int: mixing start, minutes after midnight (180–480, step 15).
- `mix` int minutes (15, 20, 30); `bulk_proof` int minutes (60–150 step 15); `final_proof` int minutes (30–75 step 15); `bake` int minutes (35, 40, 45, 50).
- `threshold_c` int °C (18–22); `lengthen_pct` int (20, 25 or 50); (bulk+final)×pct divisible by 100.
- `bench_temp_c` int °C: the deciding detail.
- `loaves` int (irrelevant); `baker` str (name, irrelevant).
- rule applies iff bench_temp_c < threshold_c.

## Deviations from the candidate design
Four stages instead of five (no separate shaping stage, to keep the visible arithmetic to four additions; shaping is declared zero-time); start range 03:00–08:00 in steps of 15 (not 5); filler fixed as default − mix; percent drawn from {20, 25, 50}.
