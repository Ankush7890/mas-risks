# coffee_stamp_card (group b1)

## Document
"{Cafe} café loyalty card terms". Visible: "Each hot drink bought earns one stamp on the card." "Cold drinks and food earn no stamps." "Stamps stay on the card from week to week." Plus 1–2 irrelevant sections.

Case: before any purchase this week the card showed `start_stamps` stamps; a list of 4 or 5 purchases on distinct weekdays (Monday–Friday, in order), each "{Day} at HH:MM: {h} hot drink(s)[ and 1 cold drink]."; plus two irrelevant sentences (pays in cash, works nearby).

Question: "How many stamps does the card show at the end of the week?"

## Withheld changing rule
"Hot drinks bought before `cutoff` earn two stamps each." (cutoff one of 08:00, 08:30, 09:00, 09:30, 10:00.)
Condition for the item: rule applies iff the argued purchases (1 or 2 of them, named by weekday in the argument) are before the cutoff. By construction: applies ⇒ argued purchases are at cutoff−90 … cutoff−10 minutes, all other purchases at cutoff+10 … 18:00; not applies ⇒ every purchase (argued ones at cutoff+10 … cutoff+90) is after the cutoff. Never exactly at the cutoff. So under the rule, the changed count is correct exactly when applies; a checker can compute: changed-correct count = default + sum of hot drinks of purchases with time < cutoff.

## Answers (formatted "{n} stamps", "1 stamp" for one)
- default = start + Σ hot drinks over all purchases.
- changed = default + Σ hot drinks of the argued purchases. Argued answer = changed.
- distractor = default + Σ cold drinks (mistake: counting cold drinks too). Draws with no cold drink or distractor = changed are rejected.
- filler = `filler` param (a free count in [max(1, default−4), changed+3] different from the other three).

Argument: "The drinks on {argued weekdays joined with ', ' / ' and '} were bought before {cutoff}, so the hot drinks then earn two stamps each, and the card shows {changed} stamps at the end of the week." (No purchase time stated.)

## params
- `cutoff_minutes` int, minutes after midnight.
- `start_stamps` int 0–6.
- `purchases` list of [weekday name str, time in minutes after midnight int, hot drinks int 1–3, cold drinks int 0–1], in weekday order.
- `argued_purchases` list of int: 0-based indices into `purchases`.
- `filler` int: the filler count.
- `customer` str (name).

## Deviations from the candidate design
Distractor is "cold drinks counted too" (each purchase may include one cold drink) instead of "number of purchases"; cut-off set extended to 08:00–10:00 in half hours; start stamps given in the case; "after Friday" replaced by "at the end of the week" since the last purchase may be on Thursday.
