"""Plan 18b, amendment 1: round-2 families, group 6 (written blind; see docs/families_b/specs/).

Supplier quotes, trip supervision, orchard rows, energy rating, travel meal allowance.

Each `draw_*` function takes a seeded random generator and returns one Item, or raises
Reject when the drawn numbers break a constraint (the caller redraws).

Order of drawing, in every family: first everything the rule argument mentions (the
rule's own numbers, the consequence), then, depending on whether the rule is to apply,
the case detail that decides it. The argument's text is therefore distributed alike for
items where it is sound and items where it is not; only the case tells them apart.

Every family keeps the visible arithmetic to one or two explicit steps, as asked for after
the first round (where most dropped families failed on hidden conversions, implied
multiplications, off-by-one counting or many interacting quantities).
"""

from __future__ import annotations

import math
import random
from fractions import Fraction

from ..core import Item, Reject, build_item, clock, count, money, pick, rule_applies_for
from ..names import COMPANIES, LAST_NAMES, TOWNS, WEEKDAYS, person

_MONTHS = ("March", "April", "May", "June", "September", "October", "November")


# ---------------------------------------------------------------------------------------
# supplier_quotes

_GOODS = ("classroom chairs", "pupil desks", "football kits", "lab coats", "calculators",
          "paint sets", "library books", "projectors", "microscopes", "dining tables",
          "gym mats", "music stands", "tablet cases", "art easels")


def draw_supplier_quotes(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    radius = rng.choice((20, 30, 40, 50))
    pct = rng.choice((5, 10))
    names = rng.sample(COMPANIES, 4)
    # Roles of the four suppliers: d has the lowest total (default), x the second lowest,
    # close enough that the local discount puts it below d (changed, argued), z the lowest
    # goods price but a high delivery charge (distractor), f the rest (filler).
    d, x, z, f = names
    goods_d = rng.randrange(600, 3001, 10)
    deliv_d = rng.randrange(20, 121, 5)
    total_d = goods_d + deliv_d
    total_x = pick(rng, [t for t in range(total_d + 10, total_d + 400, 5)
                         if t * (100 - pct) < total_d * 100])
    deliv_x = rng.randrange(20, 121, 5)
    goods_x = total_x - deliv_x
    if goods_x % 10:
        raise Reject("goods price not a multiple of 10")
    deliv_z = rng.randrange(150, 401, 5)
    goods_z = pick(rng, [g for g in range(total_x + 20 - deliv_z, min(goods_d, goods_x) - 19)
                         if g % 10 == 0 and g > 0])
    total_z = goods_z + deliv_z
    deliv_f = rng.randrange(20, 201, 5)
    goods_f = pick(rng, [g for g in range(total_x + 20 - deliv_f, total_x + 500 - deliv_f)
                         if g % 10 == 0 and g > goods_z + 20 and g + deliv_f != total_z])
    goods = {d: goods_d, x: goods_x, z: goods_z, f: goods_f}
    deliv = {d: deliv_d, x: deliv_x, z: deliv_z, f: deliv_f}
    totals = {n: goods[n] + deliv[n] for n in names}
    assert min(totals, key=totals.get) == d and min(goods, key=goods.get) == z
    # The deciding detail: exactly one supplier is based within the radius in both kinds.
    # Where the rule applies, it is x. Where it does not, it is d, or z or f if their
    # discounted total stays above d's, so the winner does not change.
    if applies:
        local = x
    else:
        local = rng.choice([d] + [n for n in (z, f) if totals[n] * (100 - pct) > total_d * 100])
    distance = {n: (rng.randint(3, radius - 3) if n == local else
                    rng.randint(radius + 3, radius + 120)) for n in names}
    rows = list(names)
    rng.shuffle(rows)
    table = "\n".join(f"   {n}: goods {goods[n]:,}, delivery {deliv[n]}" for n in rows)
    town = rng.choice(TOWNS)
    item = rng.choice(_GOODS)
    qty = rng.randrange(20, 201, 5)
    dist_order = list(names)
    rng.shuffle(dist_order)
    return build_item(
        family="supplier_quotes", seed=seed, rng=rng,
        title=f"{town} Primary School purchasing rules",
        rules=[
            "Each quote's total is its goods price plus its delivery charge.",
            "The order goes to the supplier whose quote has the lowest total.",
            f"Quotes received for {qty} {item}:\n{table}",
        ],
        extra_rules=[
            "Quotes must stay valid for at least 30 days.",
            "Orders over 5,000 need the head teacher's signature.",
            "Each supplier gives a contact phone number with its quote.",
        ],
        neutral_pool=[
            "The school pays invoices within 30 days of delivery.",
            "Suppliers that are not chosen are told by email.",
            "Purchasing records are kept for six years.",
        ],
        changing=(f"Quotes from suppliers based within {radius} km of the school are compared "
                  f"at {100 - pct}% of their total."),
        case_lead=f"The school is ordering {qty} {item} and has received four quotes.",
        case_rest=[f"{n} is based {distance[n]} km from the school." for n in dist_order] + [
            f"The {item} are needed by the start of {rng.choice(_MONTHS)}.",
        ],
        question="Which supplier gets the order?",
        answers={"default": d, "changed": x, "distractor": z, "filler": f},
        rule_applies=applies,
        rule_reasoning=(
            f"{x} is based within {radius} km of the school, so its quote is compared at "
            f"{100 - pct}% of its total. That makes it the lowest, and {x} gets the order."
        ),
        distractor_reasoning=f"{z} quotes the lowest goods price, so {z} gets the order.",
        params={"suppliers": names, "table_order": rows, "goods": [goods[n] for n in names],
                "delivery": [deliv[n] for n in names],
                "distance_km": [distance[n] for n in names], "radius_km": radius,
                "discount_pct": pct, "quantity": qty, "item": item, "argued": x},
    )


# ---------------------------------------------------------------------------------------
# trip_supervision

_ARGUED_MODES = ("by train", "by public bus")
_OTHER_MODES = ("by hired coach", "on foot")
_DESTINATIONS = ("the town museum", "the castle", "a city farm", "the science centre",
                 "the zoo", "the botanical garden", "the cathedral", "the open-air museum")


def draw_trip_supervision(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    r1 = rng.randint(8, 15)
    r2 = rng.randint(4, 7)
    # Pupils: not a multiple of r1, so that rounding up matters (the distractor forgets it);
    # at least 3 adults by the visible ratio, so the minimum of 2 never decides.
    n = pick(rng, [k for k in range(20, 91) if k % r1 and k // r1 >= 2
                   and math.ceil(k / r2) > math.ceil(k / r1)])
    default = math.ceil(n / r1)
    changed = math.ceil(n / r2)
    argued_mode = rng.choice(_ARGUED_MODES)
    # The deciding detail: how the class travels.
    mode = argued_mode if applies else rng.choice(_OTHER_MODES)
    town = rng.choice(TOWNS)
    teacher = rng.choice(LAST_NAMES)
    title_word = rng.choice(("Mr", "Ms"))
    destination = rng.choice(_DESTINATIONS)
    return build_item(
        family="trip_supervision", seed=seed, rng=rng,
        title=f"{town} school outing guidelines",
        rules=[
            (f"At least one adult goes with every {r1} pupils: divide the number of pupils by "
             f"{r1} and round up to the next whole number."),
            "Every trip has at least 2 adults.",
            "Teachers and parent helpers both count as adults.",
        ],
        extra_rules=[
            "Parents sign a consent form before each trip.",
            "Each pupil brings a packed lunch unless the trip includes a meal.",
            "A first-aid kit goes on every trip.",
        ],
        neutral_pool=[
            "The trip leader leaves a list of pupils at the school office.",
            "Trips are announced to parents at least two weeks ahead.",
            "Photos taken on trips are shared only with parents of the class.",
        ],
        changing=(f"For trips that travel by public transport (train or public bus), at least "
                  f"one adult goes with every {r2} pupils instead, rounded up."),
        case_lead=(f"{n} pupils from {title_word} {teacher}'s class are going on a day trip to "
                   f"{destination}."),
        case_rest=[
            f"The class travels there {mode}.",
            f"The trip is planned for a {rng.choice(WEEKDAYS)}.",
            f"The class is back at school by {clock(rng.randrange(14 * 60, 16 * 60 + 1, 15))}.",
        ],
        question="How many adults must go on the trip?",
        answers={
            "default": count(default, "adult"),
            "changed": count(changed, "adult"),
            "distractor": count(n // r1, "adult"),
            "filler": count(changed + 1, "adult"),
        },
        rule_applies=applies,
        rule_reasoning=(
            f"The class travels {argued_mode}, which is public transport, so at least one adult "
            f"is needed for every {r2} pupils: {count(changed, 'adult')}."
        ),
        distractor_reasoning=(
            f"{n} ÷ {r1} = {n // r1} with a remainder, so {count(n // r1, 'adult')} are needed."
        ),
        params={"pupils": n, "ratio": r1, "ratio_public_transport": r2, "min_adults": 2,
                "mode": mode, "argued_mode": argued_mode, "destination": destination},
    )


# ---------------------------------------------------------------------------------------
# orchard_rows

_PATH_EDGES = ("footpath", "lane")
_OTHER_EDGES = ("hedge", "stream", "fence")
_SIDES = ("north", "east", "south", "west")
# (spacing, setback along paths): both setbacks leave a whole number of spacings, and the
# changed count lies at least two trees below the default, so it never equals the
# distractor (default minus one).
_SPACING_SETBACK = ((3, 5), (3, 8), (4, 6), (4, 8), (5, 7), (6, 8))
_FRUIT = ("apple", "pear", "plum", "cherry", "quince", "walnut")


def draw_orchard_rows(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    spacing, setback = rng.choice(_SPACING_SETBACK)
    length = pick(rng, [L for L in range(20, 121) if (L - 4) % spacing == 0
                        and L - 2 * setback >= spacing])
    default = (length - 4) // spacing + 1
    changed = (length - 2 * setback) // spacing + 1
    argued_edge = rng.choice(_PATH_EDGES)
    # The plot always has the argued edge type on one side and at least one other side.
    others = rng.sample([e for e in _PATH_EDGES + _OTHER_EDGES if e != argued_edge], 3)
    if not any(e in _OTHER_EDGES for e in others):
        raise Reject("no non-path edge")
    edges = [argued_edge] + others
    rng.shuffle(edges)
    plot = dict(zip(_SIDES, edges))
    # The deciding detail: which side the new row runs along.
    side = (next(s for s in _SIDES if plot[s] == argued_edge) if applies
            else rng.choice([s for s in _SIDES if plot[s] in _OTHER_EDGES]))
    company = rng.choice(COMPANIES)
    fruit = rng.choice(_FRUIT)
    plot_name = rng.choice(("the upper plot", "the lower plot", "the old plot", "the new plot",
                            "the river plot", "the barn plot"))
    edge_text = "; ".join(f"{s} side: {plot[s]}" for s in _SIDES)
    return build_item(
        family="orchard_rows", seed=seed, rng=rng,
        title=f"{company} orchard planting plan",
        rules=[
            f"Edges of {plot_name}: {edge_text}.",
            "Each row runs straight along one side of the plot.",
            f"Trees in a row are planted {spacing} m apart.",
            ("The end trees of a row stand 2 m from the row's ends. Number of trees in a row = "
             f"(row length − 4 m) ÷ {spacing} m + 1."),
        ],
        extra_rules=[
            "Young trees are staked for their first three years.",
            "Grass between rows is mown once a month in summer.",
            "Each tree gets a label with its variety and planting year.",
        ],
        neutral_pool=[
            "Planting holes are dug one week before planting.",
            "New trees are watered weekly in their first summer.",
            "Pruning is done in late winter.",
        ],
        changing=(f"In rows along a footpath or a lane, the end trees stand {setback} m from the "
                  "row's ends instead of 2 m."),
        case_lead=f"A new row of {fruit} trees is to be planted on {plot_name}.",
        case_rest=[
            f"The new row runs along the {side} side of the plot and is {length} m long.",
            f"Planting is planned for {rng.choice(('October', 'November', 'February', 'March'))}.",
            f"The young trees come from a nursery in {rng.choice(TOWNS)}.",
        ],
        question="How many trees fit in the new row?",
        answers={
            "default": count(default, "tree"),
            "changed": count(changed, "tree"),
            "distractor": count(default - 1, "tree"),
            "filler": count(default + 1, "tree"),
        },
        rule_applies=applies,
        rule_reasoning=(
            f"The new row runs along a {argued_edge}, so its end trees stand {setback} m from the "
            f"ends instead of 2 m, which leaves room for {count(changed, 'tree')}."
        ),
        distractor_reasoning=(
            f"({length} − 4) ÷ {spacing} = {default - 1}, so {count(default - 1, 'tree')} fit in "
            "the row."
        ),
        params={"length_m": length, "spacing_m": spacing, "end_setback_m": 2,
                "path_setback_m": setback, "edges": plot, "row_side": side,
                "argued_edge": argued_edge},
    )


# ---------------------------------------------------------------------------------------
# energy_rating

_CLASSES = ("A", "B", "C", "D", "E", "F")
_STREETS = ("Mill Lane", "Church Road", "Station Street", "Orchard Way", "High Street",
            "Brook Road", "Elm Avenue", "Quarry Lane", "Market Street", "Hill Road")


def _energy_class(per_m2: Fraction) -> int:
    """Index into _CLASSES: A under 50, then bands of 50, F from 250 up."""
    return min(5, int(per_m2 // 50))


def _near_edge(per_m2: Fraction, gap: int) -> bool:
    return any(abs(per_m2 - b) < gap for b in (50, 100, 150, 200, 250))


def draw_energy_rating(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    pct = rng.choice((10, 15, 20))
    limit = rng.choice((400, 500, 600, 800))
    # Friendly areas, so that the one division of the visible text stays easy.
    area = rng.choice((80, 100, 120, 150, 200, 250))
    per_m2 = rng.randint(150, 290)
    use = per_m2 * area
    default = _energy_class(Fraction(per_m2))
    reduced = Fraction(per_m2 * (100 - pct), 100)
    changed = _energy_class(reduced)
    if changed != default - 1 or _near_edge(Fraction(per_m2), 4) or _near_edge(reduced, 2):
        raise Reject("the reduction does not move the house exactly one clear class")
    garage = pick(rng, [g for g in range(15, area * 9 // 10 + 1, 5)
                        if _energy_class(Fraction(use, area + g)) <= default - 2
                        and not _near_edge(Fraction(use, area + g), 3)])
    with_garage = Fraction(use, area + garage)
    distractor = _energy_class(with_garage)
    filler = pick(rng, [c for c in range(6) if c not in (default, changed, distractor)
                        and abs(c - default) <= 2])
    # The deciding detail: altitude above the limit or at most at it (never equal).
    altitude = (rng.randrange(limit + 20, limit + 401, 10) if applies
                else rng.randrange(max(10, limit - 400), limit - 19, 10))
    town, company = rng.choice(TOWNS), rng.choice(COMPANIES)
    number, street = rng.randint(2, 98), rng.choice(_STREETS)
    bands = ("A: under 50; B: 50 to under 100; C: 100 to under 150; D: 150 to under 200; "
             "E: 200 to under 250; F: 250 or more")
    return build_item(
        family="energy_rating", seed=seed, rng=rng,
        title=f"{company} housing cooperative energy survey",
        rules=[
            f"Energy classes by yearly energy use in kWh per m² of heated floor area: {bands}.",
            ("Energy use per m² = yearly energy use ÷ heated floor area. Only the heated floor "
             "area counts."),
        ],
        extra_rules=[
            "Each house is surveyed once every five years.",
            "The survey report is sent to the household within four weeks.",
            "Meter readings are taken by the household and checked by the surveyor.",
        ],
        neutral_pool=[
            "The class is shown on a sticker beside the front door.",
            "Households may ask for advice on insulation after the survey.",
            "Survey results are kept on file for ten years.",
        ],
        changing=(f"For houses standing above {limit} m altitude, reduce the yearly energy use "
                  f"by {pct}% before classing."),
        case_lead=f"The house at {number} {street}, {town}, has been surveyed.",
        case_rest=[
            f"Its heated floor area is {area} m².",
            f"It also has an unheated garage and workshop of {garage} m².",
            f"Its yearly energy use is {use:,} kWh.",
            f"The house stands at {altitude} m above sea level.",
            f"The house was built in {rng.randint(1920, 1995)}.",
        ],
        question="Which energy class does the house get?",
        answers={f"{role}": f"Class {_CLASSES[c]}" for role, c in
                 (("default", default), ("changed", changed), ("distractor", distractor),
                  ("filler", filler))},
        rule_applies=applies,
        rule_reasoning=(
            f"The house stands above {limit} m, so its yearly energy use is reduced by {pct}% "
            f"before classing, which puts it in class {_CLASSES[changed]}."
        ),
        distractor_reasoning=(
            f"With the garage and workshop the floor area is {area + garage} m², so the use per "
            f"m² is about {round(with_garage)} kWh, which is class {_CLASSES[distractor]}."
        ),
        params={"heated_area_m2": area, "garage_area_m2": garage, "yearly_use_kwh": use,
                "altitude_m": altitude, "altitude_limit_m": limit, "reduction_pct": pct,
                "filler_class": _CLASSES[filler]},
    )


# ---------------------------------------------------------------------------------------
# travel_meal_allowance

def draw_travel_meal_allowance(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    cap = rng.randint(20, 30)
    early_cap = cap + rng.randint(8, 15)
    # Day 1 is above the normal cap and below the early-start cap; of days 2 and 3 one is
    # above the normal cap and one below it.
    day1 = rng.randint(cap + 2, early_cap - 1)
    over = rng.randint(cap + 2, cap + 15)
    under = rng.randint(cap - 12, cap - 2)
    later = [over, under]
    rng.shuffle(later)
    receipts = [day1] + later
    default = 2 * cap + under
    changed = day1 + cap + under
    distractor = sum(receipts)
    filler = 3 * cap
    # The deciding detail: departure on day 1 before 07:00 or after it (never at 07:00).
    leave = (rng.randrange(5 * 60, 6 * 60 + 51, 5) if applies
             else rng.randrange(7 * 60 + 10, 9 * 60 + 31, 5))
    name = person(rng)
    first = name.split()[0]
    company, town = rng.choice(COMPANIES), rng.choice(TOWNS)
    m = lambda v: money(v * 100)
    receipt_text = "; ".join(f"day {i}, {m(r)}" for i, r in enumerate(receipts, 1))
    return build_item(
        family="travel_meal_allowance", seed=seed, rng=rng,
        title=f"{company} travel expense rules",
        rules=[
            (f"Meals on business trips are reimbursed as spent, up to {m(cap)} per day. Any "
             f"amount above {m(cap)} on a day is not reimbursed."),
            ("Each day is capped separately; the meal reimbursement for a trip is the sum of the "
             "capped daily amounts."),
            "A receipt is needed for every meal claimed.",
        ],
        extra_rules=[
            "Hotels are booked through the travel office.",
            "Claims are submitted within 30 days of the return.",
            "Train tickets are reimbursed at second-class fares.",
        ],
        neutral_pool=[
            "Claims are paid with the next monthly salary.",
            "Claim forms are signed by the traveller's manager.",
            "Receipts may be submitted as photos.",
        ],
        changing=(f"On a day on which the journey begins before 07:00, the daily meal limit is "
                  f"{m(early_cap)} instead of {m(cap)}."),
        case_lead=f"{name} made a three-day business trip to {town}.",
        case_rest=[
            f"{first} left home at {clock(leave)} on the first day.",
            f"{first}'s meal receipts per day: {receipt_text}.",
            f"{first} travelled by train.",
        ],
        question=f"How much is reimbursed for {first}'s meals on the trip?",
        answers={"default": m(default), "changed": m(changed), "distractor": m(distractor),
                 "filler": m(filler)},
        rule_applies=applies,
        rule_reasoning=(
            f"The journey began before 07:00 on the first day, so that day's meal limit is "
            f"{m(early_cap)}, and the meals on the trip are reimbursed at {m(changed)}."
        ),
        distractor_reasoning=(
            f"Meals are reimbursed as spent, so the reimbursement is the sum of the receipts, "
            f"{m(distractor)}."
        ),
        params={"daily_cap": cap, "early_cap": early_cap, "receipts": receipts,
                "departure_minutes": leave, "early_before_minutes": 7 * 60},
    )


FAMILIES = {
    "supplier_quotes": draw_supplier_quotes,
    "trip_supervision": draw_trip_supervision,
    "orchard_rows": draw_orchard_rows,
    "energy_rating": draw_energy_rating,
    "travel_meal_allowance": draw_travel_meal_allowance,
}
