# knitting_pattern (group b5)

## Document
"{Company} sweater pattern". Visible sections (in order, 1–2 irrelevant sections mixed in):
1. Size chart: "Size {S}: finished chest {f} cm, cast on {c} stitches" for 5 or 6 sizes named XS, S, M, L, XL, 2XL (in that order; the first n names are used).
2. "Choose the smallest size whose finished chest is at least `ease_cm` cm more than your own chest measurement."
3. "Cast on the number of stitches given for your size."

Irrelevant: body knitted in one piece; sleeves picked up; weave in ends.

Case: "{Name} wants to knit this sweater." Shuffled: "{First}'s chest measures `chest_cm` cm."; "{First} is using {Brand} yarn in `yarn_weight` weight."; a colour sentence.

Question: "How many stitches should {First} cast on?"

## Withheld changing rule
"With aran or chunky weight yarn, cast on `reduce_pct`% fewer stitches than the size chart gives, rounded down to a multiple of 4."
Condition: `yarn_weight` is "aran" or "chunky". Not met: "4-ply", "sport" or "DK".

Neutral withheld: block flat; no buttons; keep yarn label.

## Answers (option text "{n} stitches")
Let j = index of the smallest size with finished_chest_cm[j] ≥ chest_cm + ease_cm (never equal by construction), i = index of the smallest size with finished_chest_cm[i] ≥ chest_cm (never equal; always i < j), and j+1 always exists.
- default = cast_on[j].
- changed = floor(floor(cast_on[j] × (100 − reduce_pct) / 100) / 4) × 4. Argued answer = changed.
- distractor = cast_on[i] (mistake: ignoring the ease).
- filler = cast_on[j+1] (one size too large).
All four distinct (draws rejected otherwise).

Argument: "{First}'s yarn is aran or chunky weight, so {p}% fewer stitches are cast on than the {cast_on[j]} given for size {S_j}; rounded down to a multiple of 4, that is {changed} stitches." No yarn weight named.

## params
- `finished_chest_cm` list[int]: finished chest per size (start 80–96 even, step 8/10/12).
- `cast_on` list[int]: cast-on per size (start 80–112 step 4, step 8/12/16).
- `ease_cm` int (5, 6, 8, 10).
- `chest_cm` int: the knitter's chest.
- `reduce_pct` int (10, 15, 20, 25).
- `yarn_weight` str: deciding detail.
- Size names follow from list position (XS, S, M, L, XL, 2XL).
- rule applies iff yarn_weight ∈ {aran, chunky}.

## Deviations from the candidate design
Size count 5–6 with evenly spaced chart; reduction percent drawn from {10, 15, 20, 25}; yarn brand is an invented name; no-equality constraints added for both comparisons.
