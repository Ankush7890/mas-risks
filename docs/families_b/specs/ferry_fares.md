# ferry_fares (group b5)

## Document
"{Origin} ferry crossing fares". Visible sections (in order, 1–2 irrelevant mixed in):
1. "Foot passenger fares, one way: adult {adult}, child under 14 {child}."
2. "Vehicle fares, one way, including the driver:" Car {car}; "Van, or car with trailer" {van}; Motorhome {motorhome}.
3. "Every person in a vehicle other than the driver pays the foot passenger fare."

Irrelevant: crossing takes 40 minutes; dogs free; tickets at quay or online.

Case: "{Name} drives a car onto the {H}:00 crossing from {Origin} to {Dest}." Shuffled: "Besides {First}, the car carries {k adult(s)} and {m child(ren) under 14}." (0 → "no adults"/"no children under 14", 1 → "1 adult"/"1 child under 14", n → "n adults"/"n children under 14"); "With its {rack} fitted, {First}'s car is {x.y} m long."; car colour.

Question: "What does the crossing cost in all, one way?"

## Withheld changing rule
"Cars longer than {L} m, measured with any roof box or bike rack fitted, pay the van fare." (L printed with one decimal, e.g. "5.0".)
Condition: `length_dm > limit_dm` (strict). Never equal: applies ⇒ limit+1 … limit+8 dm; not ⇒ limit−8 … limit−1 dm.

Neutral withheld: hot drinks in lounge; arrive 20 minutes early; return = twice one-way.

## Answers (money: plain number with two decimals, no currency, e.g. "58.00")
passengers = other_adults × adult_cents + children × child_cents.
- default = car_cents + passengers.
- changed = van_cents + passengers. Argued answer = changed.
- distractor = default + adult_cents (driver charged a foot fare too).
- filler = changed + adult_cents.
van − car never equals the adult fare, so all four are distinct.

Argument: "With its {rack} fitted, {First}'s car is longer than {L} m, so it pays the van fare of {van}, and the crossing costs {changed} in all." No length stated.

## params (money in cents, lengths in decimetres)
- `adult_cents` int 500–1500 step 50; `child_cents` int, step 50, 40–60% of adult.
- `car_cents` 1800–4500 step 100; `van_cents` car+800…car+3000 step 100; `motorhome_cents` van+500…van+2000 step 100 (irrelevant).
- `other_adults` int 1–3; `children` int 0–2.
- `limit_dm` int (48, 50, 52) = 4.8/5.0/5.2 m; `length_dm` int: car length with rack (deciding detail), printed as metres with one decimal.
- `rack` str: "bike rack" or "roof box".
- rule applies iff length_dm > limit_dm.

## Deviations from the candidate design
Children 0–2 and other adults 1–3 (candidate: adults 1–4 incl. driver, children 0–3) to keep the sum small; fares on a 0.50 grid; filler fixed as changed + one adult fare; rack type (bike rack / roof box) varies.
