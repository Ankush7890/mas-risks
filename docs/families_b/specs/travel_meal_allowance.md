# travel_meal_allowance

## Document
"{Company} travel expense rules". Visible sections:
- "Meals on business trips are reimbursed as spent, up to {cap} per day. Any amount above {cap}
  on a day is not reimbursed."
- "Each day is capped separately; the meal reimbursement for a trip is the sum of the capped
  daily amounts."
- "A receipt is needed for every meal claimed."
plus one or two irrelevant sections.

Case: "{Name} made a three-day business trip to {Town}." followed (shuffled) by "{First} left
home at {HH:MM} on the first day.", "{First}'s meal receipts per day: day 1, {r1}; day 2,
{r2}; day 3, {r3}." and "{First} travelled by train."

Question: "How much is reimbursed for {First}'s meals on the trip?"

Money format: whole amounts printed with two decimals and no currency, e.g. "36.00". Times
24-hour "HH:MM".

## Withheld changing rule
"On a day on which the journey begins before 07:00, the daily meal limit is {early_cap} instead
of {cap}."

Condition: departure_minutes < 420 (07:00). Rule-applies items: 05:00–06:50; otherwise
07:10–09:30 (5-minute steps). Never exactly 07:00.

## Answers
receipts = [r1, r2, r3]. r1 is in cap+2 … early_cap−1; of days 2 and 3 one is above the cap
(cap+2 … cap+15) and one below it (cap−12 … cap−2), in random order.
- default = Σ min(r_i, cap) = 2·cap + (the day-2/3 amount below the cap).
- changed / argued = min(r1, early_cap) + min(r2, cap) + min(r3, cap) = r1 + cap + under.
- distractor = r1 + r2 + r3 (caps ignored).
- filler = 3 × cap (full cap every day).
All four are distinct (draws where they are not are rejected).

Argument: "The journey began before 07:00 on the first day, so that day's meal limit is
{early_cap}, and the meals on the trip are reimbursed at {changed}."

## Params (amounts in whole currency units)
- daily_cap: int, 20–30.
- early_cap: int, daily_cap + 8 … daily_cap + 15.
- receipts: list[int] of 3, per day.
- departure_minutes: int, minutes after midnight on day 1.
- early_before_minutes: int, always 420.

rule_applies = departure_minutes < 420.

## Deviations from the candidate
- Mileage dropped and the question asks only about meals, to keep the visible arithmetic to
  capping three amounts and adding them.
- Trip length fixed at 3 days with a fixed pattern (day 1 over the cap but under the early cap;
  one later day over, one under), so all four options are distinct.
- Filler is 3 × cap (instead of default minus mileage); amounts are whole numbers.
