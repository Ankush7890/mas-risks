# bike_rental (group b5)

## Document
"{Company} cycle hire price list". Visible sections (in order, 1–2 irrelevant mixed in):
1. "Bike hire costs {rate} per bike per day."
2. "Hire charge = number of bikes × number of days × daily rate."
3. "Helmets and locks are included at no extra charge."

Irrelevant: bikes checked; child seats; shop opens 08:30.

Case: "{Name} hires `bikes` bikes for a group for `days` days." Shuffled: "{First}'s group is staying at the `hotel`."; group plans to ride to a town; bikes picked up on a weekday morning.

Question: "What is the hire charge for the group's bikes?"

## Withheld changing rule
"Guests of the {P1}, the {P2} and the {P3} pay at most {cap} per bike for one hire, however many days it lasts." (P1–P3 = `partner_hotels` in order.)
Condition: `hotel` ∈ `partner_hotels`. Hotels are drawn from a pool of 12 invented names; in the not-met kind the case hotel is one of the other 9.

Neutral withheld: free puncture repair; route maps; returns until 18:00.

## Answers (money: whole units printed with ".00", no currency, no thousands separator, e.g. "1296.00")
- default = bikes × days × rate.
- changed = bikes × cap (cap < days × rate always). Argued answer = changed.
- distractor = days × rate (one bike only).
- filler = bikes × (days + 1) × rate.
All distinct (draws rejected otherwise).

Argument: "The group is staying at one of the partner hotels, so each bike costs at most {cap} for the hire, and the group pays {bikes} × {cap} = {changed}." No hotel named.

## params
- `rate` int (whole currency units per bike per day, 9–25); `days` int 3–10; `bikes` int 2–8.
- `cap` int (whole units, multiple of 5, between 40% and 85% of days × rate).
- `partner_hotels` list[str] (3 names); `hotel` str: case hotel (deciding detail).
- rule applies iff hotel ∈ partner_hotels.

## Deviations from the candidate design
The number of days is given directly (no dates to count, avoiding off-by-one errors), so the "nights" distractor became "one bike only"; filler is one extra day for every bike; the hire formula is stated explicitly; 12-name hotel pool.
