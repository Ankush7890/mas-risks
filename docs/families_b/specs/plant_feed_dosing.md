# plant_feed_dosing (group b5)

## Document
"{Company} nursery feeding instructions". Visible sections (in this order, with 1–2 irrelevant sections mixed in at random places):
1. "Feed solution: mix `ml_per_litre` ml of concentrate into each litre of water."
2. "Each pot gets `litres_per_pot` litre(s) of feed solution per feeding." ("1 litre", "2 litres", "3 litres")
3. "Concentrate needed for a batch = number of pots × litres of solution per pot × ml of concentrate per litre."

Irrelevant sections: feed every 7/10/14 days April–September; water the day before feeding; store concentrate out of sunlight.

Case: "{Name} is feeding a batch of `pots` `plant` at the {Company} nursery." Shuffled: "Each pot in the batch is `pot_width_cm` cm across."; greenhouse number; last fed on a weekday.

Question: "How many ml of concentrate does the batch need?"

## Withheld changing rule
"Pots narrower than `width_limit_cm` cm across get half the usual amount of feed solution."
Condition: `pot_width_cm < width_limit_cm` (strict). Never equal: applies ⇒ width in limit−6 … limit−1; not applies ⇒ limit+1 … limit+8.

Neutral withheld sections: solution best used on the day it is mixed; wear gloves; rinse watering cans.

## Answers (option text "{n} ml", integer, no thousands separator)
- default = pots × litres_per_pot × ml_per_litre.
- changed = default / 2 (always an integer: pots is even). Argued answer = changed.
- distractor = litres_per_pot × ml_per_litre (concentrate for one pot; mistake: forgetting to multiply by the number of pots).
- filler = 2 × default.

Argument: "The pots are narrower than {limit} cm across, so each pot gets half the usual feed solution, {litres_per_pot/2} litre(s), and the batch needs {changed} ml of concentrate." (half-litres written "0.5 litres", "1 litre", "1.5 litres"). It does not state the pot width.

## params
- `pots` int: number of pots, even, 6–40.
- `litres_per_pot` int: litres of solution per pot (1, 2, 3).
- `ml_per_litre` int: ml concentrate per litre (2–10).
- `width_limit_cm` int: rule threshold (12, 15, 18, 20).
- `pot_width_cm` int: pot diameter in the case (deciding detail).
- `plant` str: plant name (irrelevant).
- rule applies iff pot_width_cm < width_limit_cm.

## Deviations from the candidate design
Litres per pot drawn from whole numbers {1, 2, 3} (not 0.4–1.0) to keep the visible arithmetic to integer multiplications, and the multiplication formula is stated explicitly; pots even (6–40) so half is whole; D drawn from {12, 15, 18, 20}. Distractor changed to "one pot's concentrate" (the candidate's N·k equals the default whenever litres_per_pot = 1); filler fixed at 2 × default.
