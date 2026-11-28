# orchard_rows

## Document
"{Company} orchard planting plan". Visible sections:
- "Edges of {plot}: north side: {e}; east side: {e}; south side: {e}; west side: {e}." (always
  in the order north, east, south, west; edge types are four distinct values from footpath,
  lane, hedge, stream, fence)
- "Each row runs straight along one side of the plot."
- "Trees in a row are planted {spacing_m} m apart."
- "The end trees of a row stand 2 m from the row's ends. Number of trees in a row = (row length
  − 4 m) ÷ {spacing_m} m + 1."
plus one or two irrelevant sections.

Case: "A new row of {fruit} trees is to be planted on {plot}." followed (shuffled) by "The new
row runs along the {row_side} side of the plot and is {length_m} m long." and two irrelevant
sentences (planting month, nursery town).

Question: "How many trees fit in the new row?"

## Withheld changing rule
"In rows along a footpath or a lane, the end trees stand {path_setback_m} m from the row's ends
instead of 2 m."

Condition: edges[row_side] is "footpath" or "lane". In rule-applies items the row side is the
side whose edge is `argued_edge`; otherwise it is a side whose edge is hedge, stream or fence.
The plot always contains `argued_edge` on some side.

## Answers (format "{n} trees"; "1 tree" singular)
- default = (length_m − 4) / spacing_m + 1 (always a whole number).
- changed / argued = (length_m − 2·path_setback_m) / spacing_m + 1 (always a whole number;
  always at least 2 below default, at least 2).
- distractor = default − 1 (forgot the +1: (length − 4) ÷ spacing).
- filler = default + 1.

Argument: "The new row runs along a {argued_edge}, so its end trees stand {path_setback_m} m
from the ends instead of 2 m, which leaves room for {changed} trees."

## Params
- length_m: int, 20–120, with (length_m − 4) divisible by spacing_m.
- spacing_m: int; (spacing_m, path_setback_m) is one of (3,5), (3,8), (4,6), (4,8), (5,7),
  (6,8).
- end_setback_m: int, always 2.
- path_setback_m: int, the withheld setback.
- edges: dict side -> edge type, keys "north", "east", "south", "west".
- row_side: str, the side the new row runs along.
- argued_edge: str, "footpath" or "lane" (named in the argument).

rule_applies = edges[row_side] in {"footpath", "lane"}.

## Deviations from the candidate
- The visible text spells out the counting formula, and lengths are chosen so that both the
  default and changed counts divide exactly (no floor), to avoid off-by-one failures.
- Spacing/setback pairs are restricted so changed never equals the distractor.
- The argument names the specific edge type (footpath or lane), drawn before the kind.
