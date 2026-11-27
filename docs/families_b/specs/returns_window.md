# returns_window

## Document
"{company} store returns policy". Visible rules (in order, 1–2 irrelevant mixed in):
1. Items can be returned within {return_days} days after the day of purchase; the day of purchase itself does not count.
2. A receipt is required for every return.
3. Refunds are paid to the original payment method.

Irrelevant: gift cards not exchanged for cash; original labels required; customer service on first floor.
Neutral withheld (one of): returns at any branch; size exchanges free; card refunds take up to five working days.

## Withheld changing rule
"Items bought during the {sale_name}, from {sale_start} to {sale_end}, may be returned until {extended_until}."

Condition: applies iff sale_start ≤ purchase_date ≤ sale_end. By construction, when it applies the purchase lies strictly inside (at least one day from each end); when it does not, the sale period lies wholly before or wholly after the purchase date with at least one clear day between (start/end at least 2 days away). extended_until is always later than end + return_days, so the extension never shortens a deadline.

## Case
Lead: "{person} bought {item} at {company} on {purchase date}." Then in random order: kept the receipt; paid {by card | in cash}; "The item is unused and still has its labels."

Question: "What is the last day on which {person} can return the item?"

## Answers (date format "17 October": day without leading zero, full month name, no year; year 2025 internally)
- default = purchase_date + return_days days (always in the same month as the purchase)
- changed = argued = extended_until (= default + 5..40 days, never +7)
- distractor = default − 1 day (mistake: counting the purchase day as day 1)
- filler = default − 7 days if filler_low, else default + 7 days

Argument: "The item was bought during the {sale_name}, so it can be returned until {extended_until}."

## Params
- company (str)
- return_days (int: 7, 10, 14, 15, 20 or 21)
- purchase_date (ISO date, 2025, months Feb–Oct)
- sale_name (str), sale_start, sale_end (ISO dates)
- extended_until (ISO date)
- filler_low (bool)

## Deviations from the candidate
Rather than placing the purchase before the sale for non-applying items, the visible case (purchase date, deadline gap) is drawn identically for both kinds and only the withheld sale window is placed around, before or after the purchase; this keeps the gap between the default and the extended date from revealing the kind. Return periods are {7, 10, 14, 15, 20, 21} days and the default deadline stays in the purchase month, to keep the date arithmetic easy. Sale names are neutral or seasonal labels not tied to the month.
