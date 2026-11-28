# energy_rating

## Document
"{Company} housing cooperative energy survey". Visible sections:
- "Energy classes by yearly energy use in kWh per m² of heated floor area: A: under 50; B: 50
  to under 100; C: 100 to under 150; D: 150 to under 200; E: 200 to under 250; F: 250 or
  more."
- "Energy use per m² = yearly energy use ÷ heated floor area. Only the heated floor area
  counts."
plus one or two irrelevant sections.

Case: "The house at {n} {street}, {town}, has been surveyed." followed (shuffled) by "Its heated
floor area is {heated_area_m2} m².", "It also has an unheated garage and workshop of
{garage_area_m2} m².", "Its yearly energy use is {yearly_use_kwh} kWh." (thousands comma),
"The house stands at {altitude_m} m above sea level." and a build-year sentence.

Question: "Which energy class does the house get?" Options "Class X".

## Withheld changing rule
"For houses standing above {altitude_limit_m} m altitude, reduce the yearly energy use by
{reduction_pct}% before classing."

Condition: altitude_m > altitude_limit_m (never equal; at least 20 m away). Rule-applies items:
limit+20 … limit+400; otherwise max(10, limit−400) … limit−20 (steps of 10).

## Answers
class(x): A if x < 50, B if < 100, C if < 150, D if < 200, E if < 250, else F.
- default = class(yearly_use / heated_area); this is a whole number 150–290, at least 4 away
  from any band edge (so the default is D, E or F).
- changed / argued = class(yearly_use × (100 − p)/100 / heated_area); always exactly one class
  better than default, at least 2 away from any band edge.
- distractor = class(yearly_use / (heated_area + garage_area)) (unheated area wrongly
  counted); at least two classes better than default and at least 3 away from a band edge.
- filler = `filler_class` param: a class distinct from the other three, within two classes of
  the default.

Argument: "The house stands above {altitude_limit_m} m, so its yearly energy use is reduced by
{reduction_pct}% before classing, which puts it in class {changed}."

## Params
- heated_area_m2: int, one of 80, 100, 120, 150, 200, 250.
- garage_area_m2: int, multiple of 5, 15 to 90% of the heated area.
- yearly_use_kwh: int, heated_area × whole kWh/m².
- altitude_m: int.
- altitude_limit_m: int, one of 400, 500, 600, 800.
- reduction_pct: int, one of 10, 15, 20.
- filler_class: str, letter of the filler class.

rule_applies = altitude_m > altitude_limit_m.

## Deviations from the candidate
- Six classes A–F with "under" bands, so that fractional values after the reduction are never
  ambiguous; the default is always D–F.
- Heated areas from a small friendly set and use per m² a whole number, so the one visible
  division is exact and easy.
- The distractor requires a sizeable unheated garage (to land two classes better), so it never
  coincides with the changed class; the filler is any remaining class near the default.
