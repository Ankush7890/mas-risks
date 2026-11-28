# curtain_fabric (group b5)

## Document
"{Company} curtain making guide". Visible sections (in order, 1–2 irrelevant mixed in):
1. "Each drop (the length of fabric cut for one width) is the finished curtain length plus `hem_cm` cm for hems."
2. "Fabric needed = number of widths × length of one drop."
3. "Fabric is ordered in metres: divide the total in centimetres by 100."

Irrelevant: linings ordered separately; two weeks for making up; curtain tape included.

Case: "{Name} orders a pair of curtains from {Company}." Shuffled: "The finished curtains are `finished_length_cm` cm long."; "The pair of curtains needs `widths` widths of fabric in all."; "The chosen fabric is {colour} `fabric`."; room sentence.

Question: "How many metres of fabric should be ordered?"

## Withheld changing rule
"Pile fabrics (velvet, chenille and corduroy) need `pile_extra_cm` cm more per drop, so that the pile runs the same way on every width."
Condition: `fabric` ∈ {velvet, chenille, corduroy}. Not met: cotton, linen, sateen, voile, polyester.

Neutral withheld: pressed before delivery; hooks supplied; free samples.

## Answers (metres with exactly two decimals and " m", e.g. "10.40 m"; computed in whole cm then divided by 100)
drop = finished_length_cm + hem_cm.
- default = widths × drop.
- changed = widths × (drop + pile_extra_cm). Argued answer = changed.
- distractor = widths × finished_length_cm (hems forgotten).
- filler = (widths + 1) × drop.

Argument: "The chosen fabric is a pile fabric, so each drop needs {e} cm more, {drop + e} cm in all, and {changed} of fabric should be ordered." No fabric named.

## params
- `finished_length_cm` int 120–260 step 5; `hem_cm` int (20, 25, 30); `widths` int 2–8; `pile_extra_cm` int (8, 10, 12, 15); `fabric` str (deciding detail).
- rule applies iff fabric is velvet, chenille or corduroy.

## Deviations from the candidate design
The number of widths is given in the case instead of computed as ceil(2 × track ÷ fabric width) (removes a rounding step with decimals); the cm → m conversion is stated explicitly; answers shown with two decimals instead of one.
