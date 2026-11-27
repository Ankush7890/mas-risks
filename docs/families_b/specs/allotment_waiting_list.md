# allotment_waiting_list (group b1)

## Document
"{Road} allotment society plot rules" (road name, never a town). Visible: a waiting list of four applicants, each "{Name}: applied {Month} {Year}", not in date order; and "A plot that becomes free goes to the applicant who has waited longest, that is, the one with the earliest application date." Plus 1–2 irrelevant sections. All four application years are distinct.

Case: "Plot {plot} has become free, and the four people on the waiting list still want a plot." Then one sentence per applicant: "{Name} lives in {Town}." (shuffled).

Question: "Who gets plot {plot}?"

## Withheld changing rule
"Applicants who live in {P1} or {P2}, the society's home parish, go ahead of all applicants from elsewhere, whatever their application date."
Condition: some applicant lives in P1 or P2. By construction: applies ⇒ exactly the argued applicant X (never the earliest) lives in P1/P2, everyone else elsewhere; not applies ⇒ no applicant lives in P1/P2. Under the rule the winner is X if applies, else the earliest applicant.

## Answers (option text = applicant's full name)
- default = applicant with the earliest application date (earliest year).
- changed = X, the argued applicant. Argued answer = changed.
- distractor = the applicant listed first on the waiting list (mistake: taking list order as priority); never the earliest nor X.
- filler = the remaining applicant.

Argument: "{X} lives in the society's home parish, so {X first name} goes ahead of the applicants from elsewhere and gets plot {plot}." (X's town is not stated.)

## params
- `applicants`: list of 4 [full name str, application year int 2017–2025, month int 1–12, home town str]; index = applicant id.
- `listing_order`: list of 4 applicant ids in the order shown on the waiting list (first = distractor).
- `parish`: [P1, P2] town names.
- `argued`: applicant id of X.
- `plot`: int plot number (irrelevant to answers).

## Deviations from the candidate design
Application years are all distinct (dates shown as month and year) to keep the default easy; the society is named after a road, not a town, so no visible town hints at the parish.
