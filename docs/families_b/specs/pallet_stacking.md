# pallet_stacking

## Document
"{company} warehouse bay loading rules". Visible rules (in order, with 1–2 irrelevant sections mixed in):
1. Pallets may be stacked on top of each other.
2. In every bay, stacks may be no higher than {H} m. Only whole pallets count: a pallet that would reach above the limit is not loaded.

H = height_limit_dm / 10, printed with one decimal (e.g. "4.5 m").
Irrelevant sections: forklift drivers wear vests; damaged pallets set aside; bays checked for spills.
Neutral withheld (one of): bay labels show last loading date; goods loaded in order of arrival; empty pallets returned on Fridays.

## Withheld changing rule
"Pallets that weigh more than {max_stack_kg} kg, load included, may not be stacked."

Condition: loaded weight = cartons × carton_kg + empty_pallet_kg. The rule applies iff loaded weight > max_stack_kg. By construction: applies → max_stack_kg < weight ≤ max_stack_kg + 300; not applies → max_stack_kg − 300 ≤ weight < max_stack_kg (never equal).

## Case
Lead: "Bay {bay} is to be filled with pallets of {goods}." Then in random order: "The floor of bay {bay} has room for {rows} rows of {per_row} pallets."; "Each loaded pallet is {h} m high." (h = pallet_height_dm / 10, one decimal); "Each pallet holds {cartons} cartons of {carton_kg} kg."; "An empty pallet weighs {empty_pallet_kg} kg."

Question: "How many pallets fit in bay {bay}?"

## Answers (formatted "N pallets")
- positions = rows × per_row; layers = floor(height_limit_dm / pallet_height_dm) (always 3–5, never an exact fit)
- default = positions × layers
- changed = argued = positions (one layer only)
- distractor = positions × (layers + 1) (mistake: a part layer counted as a whole layer, i.e. rounding the layer count up)
- filler = positions × (layers − 1)

Argument: "The loaded pallets are too heavy to be stacked, so only one layer is allowed and the bay holds {rows} × {per_row} = {positions} pallets."

## Params
- company (str), bay (int 1–40), goods (str)
- rows (int 2–6), per_row (int 2–8)
- height_limit_dm (int 36–64): stack height limit in tenths of a metre
- pallet_height_dm (int 10–18): height of one loaded pallet, tenths of a metre
- max_stack_kg (int: 600, 700, 800 or 1000): weight limit for stacking in the withheld rule
- cartons (int, even, 10–40), carton_kg (int, one of 5, 8, 10, 12, 15, 20, 25, 30, 40), empty_pallet_kg (int: 20, 25 or 30)

## Deviations from the candidate
Bay floor dimensions and pallet footprint replaced by a stated grid ("room for R rows of K pallets"), so the floor-area distractor is replaced by the round-up-layers mistake (the candidate's filler); the filler is positions × (layers − 1). The weight band is limited to within 300 kg of the limit.
