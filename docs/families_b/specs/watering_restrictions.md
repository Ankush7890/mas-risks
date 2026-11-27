# watering_restrictions

## Document
Title "{town} garden watering notice". Visible sections (in order, 1–2 irrelevant inserted):
- Hose/sprinkler watering by house number: odd numbers on Monday, Wednesday and Friday; even numbers on Tuesday, Thursday and Saturday.
- "No garden watering is allowed on Sundays."
- "For flats, the number of the building counts, not the flat number."
- Irrelevant pool: watering cans, car washing, swimming pools.

Withheld neutral (one of three): helpline, allotments, monthly review.

## Withheld changing rule
"From {start date}, odd numbers may water on {D_odd} only and even numbers on {D_even} only." D_odd ∈ {Monday, Wednesday, Friday}; D_even ∈ {Tuesday, Thursday, Saturday}. Dates are written "D Month" (e.g. "12 July"), year 2026 (not shown).
Condition used for the item: the restriction governs the next watering. Applies: start is 1–12 days before today (already in force). Not applies: start is 1–12 days after the default watering day (so the next ordinary watering day still falls before it).

## Case
"{name} lives in Flat {flat}, {house} {street}, {town}, and wants to water the garden with a hose." then (shuffled) "Today is {Weekday} {D Month}, and {first name} will not water today.", a lawn sentence. The flat number has the opposite parity of the house number.
Question: "On which day of the week can {name} next water the garden with a hose?"

## Answers (a weekday name, e.g. "Wednesday")
- today's weekday from params.today (Monday = 0).
- default = first weekday strictly after today that is in the house number's parity set (odd: Mon/Wed/Fri; even: Tue/Thu/Sat).
- changed = D_odd if house odd, else D_even (never equal to default). Applies iff start < today.
- argued = changed.
- distractor = first weekday strictly after today in the flat number's parity set.
- filler = weekday filler_day (Monday–Saturday, different from the three above).

Argument: "The new restriction is in force, so {house} {street} may water only on {changed}, and the next day {name} can water the garden is {changed}."

## Params
- house (int 1–199), flat (int 1–12, opposite parity).
- today (ISO date str), start (ISO date str): today and the start date of the changing rule.
- new_odd_day, new_even_day (int, 0=Monday … 5=Saturday): D_odd, D_even.
- filler_day (int, 0=Monday … 5=Saturday): the filler weekday.
- street, town (str).

## Deviations from candidate
Added a visible rule that the building number counts for flats (makes the flat-number distractor a clear mistake and the default unambiguous); "not applies" places the start date after the default watering day, not merely after today; today is stated with its weekday so no calendar lookup is needed.
