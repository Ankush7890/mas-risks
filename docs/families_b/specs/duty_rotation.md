# duty_rotation

## Document
"{Company} weekend duty rota". Visible: "Duty weekends in {Month} (Saturday–Sunday): a–a+1, b–b+1, ... {Month}." (3 or 4 weekends, all within days 1–28); the rota order as a numbered list of 4–6 first names; the first name is on duty on the first listed weekend, each following weekend the next name, wrapping to the top after the last.

Case: "The team is checking the {Month} rota." then (shuffled) "{P} is on leave from {lo} to {hi} {Month}." (P = person on duty on the asked weekend by rotation) and an irrelevant sentence about another rota member.

Question: "Who is on duty on the weekend of {S}–{S+1} {Month}?" (S is never the first weekend.)

## Withheld changing rule
"If the person whose turn it is is on leave during the duty weekend, the next person in the order takes that weekend instead."

Condition: P's leave (inclusive days lo..hi) covers the asked weekend. Applies items: lo ≤ S and hi ≥ S+1 (covers both days). Non-applies items: the leave ends by S−1 (Friday or earlier) or starts on S+2 (Monday) or later; never a partial overlap. All dates in 1–30 of the month; leave lasts at least 3 days.

## Answers (option text: the first name)
- k = index of S in weekend_saturdays (0-based); n = number of names.
- default: names[k mod n].
- changed (= argued): names[(k+1) mod n].
- distractor: names[(k−1) mod n] (counting the asked weekend as "k weekends after the first, so name number k").
- filler: one other name (random among the rest).

## Params
- names: list of 4–6 distinct first names, rota order.
- weekend_saturdays: list of ints, the Saturday dates of the duty weekends (Sunday is +1).
- asked_saturday: int, Saturday of the asked weekend.
- leave_from, leave_to: int, inclusive leave dates (same month).
- month: str, month name.
- filler: str, the filler option name (one of names, other than the three role names).

## Deviations from candidate
The duty weekend dates are listed explicitly (no calendar arithmetic); everything stays inside one month; at most 4 weekends.
