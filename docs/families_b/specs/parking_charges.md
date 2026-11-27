# parking_charges

## Document
"{town} station car park tariff". Visible rules (in order, 1–2 irrelevant sections mixed in):
1. Parking costs {rate} per started hour.
2. Parking is paid at the exit machine before leaving.
3. A lost ticket is charged at the day rate of {day_rate}.

Irrelevant: open 24 hours; vehicles over 2.1 m cannot enter; season tickets at the ticket office.
Neutral withheld (one of): EV charging on level 1; motorcycles park free; 240 spaces.

Money format: unnamed currency, two decimals, no thousands separator ("9.50"); amounts are given in cents in params.

## Withheld changing rule
"Cars that enter after 18:00 pay a flat evening rate of {evening}, however long they stay before 08:00 the next morning."

Condition: applies iff entry_minutes > 1080 (18:00). By construction: applies → entry 18:01–21:30; not applies → entry 14:00–17:59. Durations are at most 7 hours, so every stay of an applying car ends by 04:30, before 08:00.

## Case
Lead: "{person} parks at the {town} station car park." Then in random order: "{First}'s car enters the car park at {HH:MM}." (24-hour, zero-padded); "{First}'s car stays in the car park for {h} hour(s) and {m} minute(s)."; "{First} still has the parking ticket when leaving."; "{First} pays {by card | in cash | with a phone app}."

Question: "How much does {person} pay on leaving?"

## Answers
- started = ceil(duration_minutes / 60); full = floor(duration_minutes / 60) (duration is never a whole number of hours)
- default = started × rate_cents
- changed = argued = evening_cents
- distractor = full × rate_cents (mistake: only full hours charged)
- filler = (full − 1) × rate_cents if filler_low, else (started + 1) × rate_cents. filler_low is true only when full ≥ 2.
All four distinct and none equals the day rate.

Argument: "The car entered the car park after 18:00, so the flat evening rate applies and {person} pays {evening}."

## Params
- town (str)
- rate_cents (int, 120–450 step 10): price per started hour
- evening_cents (int, 400–1200 step 50): flat evening rate
- day_rate_cents (int, 1500–3000 step 50): lost-ticket rate (irrelevant)
- entry_minutes (int): entry time as minutes after midnight
- duration_minutes (int, 70–420, not a multiple of 60)
- filler_low (bool)

## Deviations from the candidate
The case gives the entry time and the length of stay (not an exit time), so no exit clock across midnight is shown. The filler is below the distractor in about half the items (full − 1 hours) instead of always default + rate.
