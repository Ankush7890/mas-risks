# water_tariff

## Document
Title "{company} Water quarterly household tariff". Visible sections (in order, 1–2 irrelevant inserted):
- "Each household pays a standing charge of {S} per quarter."
- "Water used in the quarter is charged as follows: the first {B1} m³ at {r1} per m³, all further water at {r2} per m³."
- "Meters are read once a quarter."
- Irrelevant pool: billing time, sewerage, leaks.

Withheld neutral (one of three): payment methods, meter test, price review.

## Withheld changing rule
"Households of five or more people have a first band of {B2} m³ instead of {B1} m³."
Condition: number of residents ≥ 5. Residents are 5–7 when the rule applies, 2–4 otherwise.

## Case
"The {surname} household at {number} {street}, {town}, used {Q} m³ of water this quarter." then (shuffled) "The people living at the address are A, B, … and Z." (first names; count them), a meter-reading month sentence, a direct-debit sentence.
Question: "What is the household's water bill for the quarter?"

## Answers (money: two decimals, no currency, e.g. "141.50")
- default = S + B1·r1 + (Q − B1)·r2.
- changed = S + B2·r1 + (Q − B2)·r2. Applies iff len(residents) ≥ 5.
- argued = changed.
- distractor = default − S (standing charge forgotten).
- filler = S + Q·r1 (all water at the low rate).
Q > B2 + 2 always.

Argument: "The household has five or more people, so its first {B2} m³ are charged at {r1} per m³, and the bill for the quarter is {changed}."

## Params
- standing_cents (int: 1000/1200/1500/1800/2000/2500) = S.
- band_m3 (int 10/15/20/25) = B1; big_band_m3 (int, B1 + 5/10/15) = B2.
- low_rate_cents (int 100/150/200/250) = r1; high_rate_cents (int, r1 + 50/100/150) = r2.
- used_m3 (int, B2+3 … 90) = Q.
- residents (list of str): first names of the people at the address.
- big_household_min (int, 5): the threshold in the rule.
- company (str).

## Deviations from candidate
Rates restricted to multiples of 0.50 and bands to multiples of 5 for friendly arithmetic; household size given as a list of names to count.
