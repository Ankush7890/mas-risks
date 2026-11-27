# alterations_service (group b1)

## Document
"{Shop} tailoring and alterations terms". Visible: "Standard alterations take {n} working days, counted from the day after hand-in; the garment is ready from 12:00 on the last of them." "Working days are Monday to Friday." Plus 1–2 irrelevant sections (opening hours Mon–Fri 09:00–18:30, uncollected garments, payment).

Case: the customer brings a garment for a standard alteration and "hands in the {garment} on {Weekday D Month} at HH:MM"; plus two irrelevant sentences.

Question: "On which day is the {garment} ready?"

## Withheld changing rule
"Garments handed in after 15:00 count as handed in on the next working day."
Condition: hand-in time > 15:00. Applies ⇒ time 15:05–18:30; not applies ⇒ 09:00–14:55 (5-minute steps; never 15:00).

## Answers (format "Weekday D Month", e.g. "Thursday 20 May"; no year; all dates in 2027)
Let W(d, k) = date k working days (Mon–Fri) after d (k may be negative).
- default = W(handin, n). Always in the hand-in week (hand-in weekday index + n ≤ Friday).
- next = W(handin, 1); changed = W(next, n) = W(handin, n+1). Argued answer = changed.
- distractor = W(default, −1) (mistake: counting the hand-in day as the first working day).
- filler = W(default, −2) if `low_filler` else W(changed, 1).

Argument: "The {garment} was handed in after the cut-off, so it counts as handed in on {next}, and it is ready on {changed}." (No time stated.)

## params
- `handin_date` str ISO date (a Monday–Wednesday in 2027).
- `handin_minutes` int, minutes after midnight (deciding detail).
- `cutoff_minutes` int = 900.
- `working_days` int n ∈ {2, 3, 4}.
- `low_filler` bool.
- `garment` str; `customer` str name.

## Deviations from the candidate design
n limited to 2–4 and the default kept within the hand-in week (no weekend counting for the default); distractor changed from "n calendar days" (identical to default without a weekend) to "hand-in day counted as first working day"; filler is two working days early or one after changed.
