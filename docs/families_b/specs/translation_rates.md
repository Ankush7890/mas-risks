# translation_rates

## Document
Title "{agency} translation service rates" (agency is a company name different from the client; not in params). Visible sections (in order, 1–2 irrelevant inserted):
- "Rates per word:" table of four rows "{L1} into {L2}: R per word" for pairs (a→b), (b→a), (a→c), (c→a); four distinct rates 0.08–0.22.
- "The word count used for the invoice is that of the source text."
- "The minimum charge per job is {min}." (30.00–60.00; always below the default, which is at least 64.00, so it never binds for default/changed/distractor).
- Irrelevant pool: certified stamp, payment terms, file format.

Withheld neutral (one of three): second translator check, terminology lists, e-mail delivery.

## Withheld changing rule
"If delivery is wanted less than 48 hours after the order is placed, a {p}% rush supplement is added to the invoice."
Condition: hours between order and wanted delivery < 48. Gap = 24·(due_day − order_day) + due_hour − order_hour. Gaps 47, 48, 49 never occur (applies: gap ≤ 46; not: gap ≥ 50).

## Case
"{client} orders a translation of a {words}-word {src} {document} into {tgt}." then (shuffled) "The order is placed on {Day} at HH:00.", "{client} wants the translation delivered by {Day} at HH:00.", "The {tgt} text is expected to come to about {target_words} words.", a layout sentence. Days: order Monday–Wednesday, delivery a later day the same week up to Friday; hours 08–17. Word counts printed with thousands comma ("4,800").
Question: "What is the invoice for the job?"

## Answers (money: plain number with two decimals, no currency, no thousands separator, e.g. "432.00")
Let job rate = rate of the pair src→tgt (index job_pair); reverse rate = rate of tgt→src (index job_pair XOR 1, i.e. 0↔1, 2↔3).
- default = words × job rate.
- changed = default × (1 + p/100). Applies iff gap < 48.
- argued = changed.
- distractor = words × reverse rate (direction confused).
- filler = target_words × job rate (target-text count used).

Argument: "Delivery is wanted less than 48 hours after the order is placed, so the {p}% rush supplement is added, and the invoice comes to {changed}."

## Params
- pairs (list of 4 [source, target] language pairs, table order); rates_cents (list of 4 ints, cents per word, same order); job_pair (int 0–3).
- words (int 800–6000, step 100); target_words (int, multiple of 100, ≈80–120% of words, ≠ words).
- minimum_cents (int); rush_pct (int, 20/25/40/50).
- order_day, due_day (int, 0=Monday … 4=Friday); order_hour, due_hour (int 8–17, on the hour).
- client (str), document (str).

## Deviations from candidate
Word counts in steps of 100; order/delivery limited to one working week (Mon–Fri, on the hour); gaps 47–49 h excluded; table uses three languages (two pairs reversed) instead of four free pairs.
