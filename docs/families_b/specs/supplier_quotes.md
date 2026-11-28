# supplier_quotes

## Document
"{Town} Primary School purchasing rules". Visible sections (in this order, with one or two
irrelevant sections mixed in at random places):
- "Each quote's total is its goods price plus its delivery charge."
- "The order goes to the supplier whose quote has the lowest total."
- "Quotes received for {quantity} {item}:" followed by one line per supplier,
  "   {Supplier}: goods {goods}, delivery {delivery}", in the order `table_order`.

Case: "The school is ordering {quantity} {item} and has received four quotes." followed (in
shuffled order) by one sentence per supplier, "{Supplier} is based {d} km from the school.",
and one sentence about the month the goods are needed.

Question: "Which supplier gets the order?" Options are the four supplier names.

## Withheld changing rule
"Quotes from suppliers based within {radius_km} km of the school are compared at
{100 − discount_pct}% of their total."

Condition: a supplier's distance is below `radius_km` (distance is never equal to the radius;
it is at least 3 km away from it on either side). The rule applies to the item when the
argued supplier (`argued`) is within the radius. Exactly one supplier is within the radius in
every item: in rule-applies items it is the argued supplier; otherwise it is the default
winner, or another supplier whose discounted total is still above the default winner's
total (so the winner does not change).

## Answers
total(s) = goods(s) + delivery(s).
- default: the supplier with the lowest total (unique; second lowest is at least 10 higher).
- changed / argued: the supplier `argued`, which has the second-lowest total and satisfies
  total(argued) × (100 − p) < total(default) × 100 (strict). With the rule applied to the
  within-radius supplier, it has the lowest compared total.
- distractor: the supplier with the lowest goods price (delivery ignored); its total is above
  the argued supplier's total.
- filler: the remaining supplier (total above the argued supplier's total).
All four options are distinct supplier names. Amounts are whole numbers; goods prices are
multiples of 10 printed with a thousands comma (e.g. "1,110"), delivery charges multiples of 5.

Argument (rule_reasoning): "{argued} is based within {radius_km} km of the school, so its quote
is compared at {100 − p}% of its total. That makes it the lowest, and {argued} gets the order."

## Params
- suppliers: list[str], the four supplier names in role order [default, argued/changed,
  distractor, filler] (the roles can also be recomputed from the numbers).
- table_order: list[str], the order of rows in the quote table.
- goods: list[int], goods price per supplier, aligned with `suppliers`.
- delivery: list[int], delivery charge per supplier, aligned with `suppliers`.
- distance_km: list[int], distance from the school per supplier, aligned with `suppliers`.
- radius_km: int, one of 20, 30, 40, 50.
- discount_pct: int, 5 or 10 (quotes compared at 100 − this percent).
- quantity: int, number of items ordered (not used in any computation).
- item: str, the goods ordered (text only).
- argued: str, the supplier named in the argument (= the changed answer).

rule_applies = distance_km of `argued` < radius_km.

## Deviations from the candidate
- The table gives each supplier's goods price for the whole order instead of unit price ×
  quantity, so the visible arithmetic is four additions (no multiplications).
- The distractor is "lowest goods price" (delivery ignored) instead of "lowest unit price".
- In rule-not-met items, one other supplier (default winner, or one whose discounted total
  stays above the winner's) is within the radius, so both kinds always have exactly one
  local supplier.
- Radius drawn from 20/30/40/50 (candidate: 30/40/50).
