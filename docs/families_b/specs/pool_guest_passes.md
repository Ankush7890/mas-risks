# pool_guest_passes

## Document
"{town} swimming club member rules". Visible rules (in order, 1–2 irrelevant mixed in):
1. Members may bring one guest per visit. Guests swim free of charge.
2. No guests are allowed on {no_guest_weekday} mornings, before 12:00.
3. Children under 8 must be accompanied in the water by an adult.

Irrelevant: lane swimming reserved on weekday evenings; coin lockers; membership renewed in January.
Neutral withheld (one of): guests sign guest book; caps sold at reception; closed on public holidays.

## Withheld changing rule
"Each member's first {quota} guest visits in a calendar month are free; after that, each further guest pays {fee}."

Condition: let m = number of `this_month_dates` (earlier guest visits in the visit's calendar month). The planned visit is visit number m + 1. The rule applies (the guest pays) iff m + 1 > quota, i.e. m ≥ quota. By construction: applies → m ∈ {quota+1, quota+2}; not applies → m ∈ {quota−3, quota−2} (never quota−1 or quota). Visits in the previous month (`previous_month_dates`, 1–3 of them) never count.

## Case
Lead: "{member}, a member of the club, wants to bring {a guest description} to the pool on {Weekday} {D Month} at {HH:MM}." The visit is always on no_guest_weekday, always in the afternoon (13:00–19:30), between day 12 and 28 of the month. Then in random order:
- "So far in {Month}, {First} has brought a guest on {date list}." or, when m = 0, "So far in {Month}, {First} has not brought a guest."
- "In {PrevMonth}, {First} brought a guest on {date list}."
- "The guest is {19–70} years old."
Date format "3 September"; lists "a, b and c". Year 2025 (not shown) fixes weekdays.

Question: "Can {member} bring the guest on {D Month}, and on what terms?"

## Answers
- default: "Yes, and the guest swims free of charge"
- changed = argued: "Yes, but the guest pays {fee}"
- distractor: "No, guests are not allowed on {no_guest_weekday}s" (mistake: ignoring that the ban is mornings only)
- filler: "Yes, but the guest pays {filler_fee}"
Money: two decimals, e.g. "6.50".

Argument: "{member} has already used up the {quota} free guest visits of this calendar month, so this guest pays {fee}."

## Params
- town (str), member (str, full name)
- quota (int: 3, 4 or 5)
- fee_cents (int, 300–900 step 50); filler_fee_cents (int, same range, ≠ fee_cents)
- no_guest_weekday (str, Monday–Sunday)
- visit_date (ISO date string, 2025), visit_minutes (int, minutes after midnight, 13:00–19:30 step 15)
- this_month_dates (list of ISO dates, sorted, all before visit_date in the same month)
- previous_month_dates (list of ISO dates in the previous month)

## Deviations from the candidate
The "No" distractor names the weekday; the filler is a second fee option ("Yes, but the guest pays {other fee}") instead of an under-16 condition. Counts within one of the quota boundary (m = quota − 1 or quota) are excluded. The quota is 3–5 (not 2–5) so the non-applying count range is non-negative.
