# paint_estimate

## Document
"{company} decorators' estimate sheet". Visible rules (kept in this order, with one or two irrelevant sections mixed in):
1. The area to paint is the total wall area minus 2 m² for each door and {window_area_m2} m² for each window.
2. Walls get one coat of paint.
3. One tin of paint covers {tin_coverage_m2} m² with one coat. The number of tins is rounded up to whole tins.

Irrelevant sections (1–2 of): estimates valid for 30 days; brushes etc. included in labour; ceilings on a separate sheet.
Neutral withheld section (one of): furniture moved and covered; paint bought on the day; unopened tins taken back.

## Withheld changing rule
"Walls that are currently {c1}, {c2}, {c3} or {c4} need two coats." (c1..c4 = `two_coat_colours`, in that order.)

Condition: the rule applies iff `current_colour` is one of `two_coat_colours`. Every colour (listed or not) comes from the same pool of ten strong colours: dark red, navy blue, dark green, black, chocolate brown, purple, burgundy, charcoal grey, deep orange, teal. Where the rule does not apply, the current colour is one of the six pool colours not listed.

## Case
Lead: "{person} wants the walls of a {room} painted {new_colour}." Then, in random order: total wall area {gross_area_m2} m² counting doors and windows; the room has {doors} door(s) and {windows} window(s); "The walls are currently {current_colour}."

Question: "How many tins of paint does the job need?"

## Answers (all formatted "N tins", "1 tin" when N = 1)
- net = gross_area_m2 − doors × door_area_m2 − windows × window_area_m2
- default = ceil(net / tin_coverage_m2)
- changed = argued = ceil(2 × net / tin_coverage_m2)
- distractor = ceil(gross_area_m2 / tin_coverage_m2) (mistake: door and window deductions forgotten)
- filler = default − 1 if `filler_low` is true, else changed + 1

Constraints: net, 2 × net and gross are never exact multiples of the coverage; the four counts are distinct.

Argument: "The walls are currently a colour that needs two coats, so the paint needed doubles and the job needs {changed} tins." (does not name the colour)

## Params
- company (str): company name in the title
- gross_area_m2 (int, m², 30–80): total wall area including doors and windows
- door_area_m2 (int, always 2): deduction per door
- window_area_m2 (int, 1 or 2): deduction per window
- doors (int, 1–2), windows (int, 1–3)
- tin_coverage_m2 (int, one of 10, 12, 15, 20): m² one tin covers with one coat
- two_coat_colours (list of 4 str): colours named in the withheld rule, in order
- current_colour (str): current wall colour; rule applies iff it is in two_coat_colours
- new_colour (str): the colour to be painted (irrelevant)
- filler_low (bool): whether filler = default − 1

## Deviations from the candidate
Room dimensions (perimeter × height) replaced by a stated total wall area, and litres-per-m² plus tin size merged into one "m² per tin" figure, to cut the visible arithmetic to subtract–divide–round up. Coverage set is {10, 12, 15, 20} m² per tin. The filler is default − 1 in about half the items (instead of always changed + 1), so the default's rank among the options varies.
