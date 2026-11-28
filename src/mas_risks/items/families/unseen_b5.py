"""Plan 18b families, group 5 (docs/families_b/draw.md). Written blind; see docs/families_b/specs/.

Plant feed dosing, knitting pattern, ferry fares, curtain fabric, bike rental.

Each `draw_*` function takes a seeded random generator and returns one Item, or raises
Reject when the drawn numbers break a constraint (the caller redraws).

Order of drawing, in every family: first everything the rule argument mentions (the
rule's own numbers, the consequence), then, depending on whether the rule is to apply,
the case detail that decides it. The argument's text is therefore distributed alike for
items where it is sound and items where it is not; only the case tells them apart.
"""

from __future__ import annotations

import random
from fractions import Fraction

from ..core import Item, Reject, build_item, decimal, money, pick, rule_applies_for
from ..names import COMPANIES, TOWNS, WEEKDAYS, person


def _litres(v) -> str:
    return f"{decimal(v)} litre" if v == 1 else f"{decimal(v)} litres"


# ---------------------------------------------------------------------------------------
# plant_feed_dosing

_PLANTS = ("geraniums", "fuchsias", "tomato plants", "basil plants", "lavender plants",
           "begonias", "pepper plants", "hostas", "dahlias", "rosemary plants")


def draw_plant_feed_dosing(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    width_limit = rng.choice((12, 15, 18, 20))
    per_litre = rng.randint(2, 10)  # ml of concentrate per litre of water
    per_pot = rng.choice((1, 2, 3))  # litres of solution per pot
    # An even number of pots, so that half the concentrate is a whole number of ml.
    pots = rng.randrange(6, 41, 2)
    total = pots * per_pot * per_litre
    changed = total // 2
    # Narrower than the limit where the rule applies, wider where not; never equal.
    width = (rng.randint(width_limit - 6, width_limit - 1) if applies
             else rng.randint(width_limit + 1, width_limit + 8))
    company, name = rng.choice(COMPANIES), person(rng)
    plant = rng.choice(_PLANTS)
    interval = rng.choice((7, 10, 14))
    house = rng.randint(1, 6)
    last_day = rng.choice(WEEKDAYS)
    return build_item(
        family="plant_feed_dosing", seed=seed, rng=rng,
        title=f"{company} nursery feeding instructions",
        rules=[
            f"Feed solution: mix {per_litre} ml of concentrate into each litre of water.",
            f"Each pot gets {_litres(per_pot)} of feed solution per feeding.",
            ("Concentrate needed for a batch = number of pots × litres of solution per pot × ml "
             "of concentrate per litre."),
        ],
        extra_rules=[
            f"Feed every {interval} days from April to September.",
            "Water the pots the day before feeding.",
            "Store the concentrate out of direct sunlight.",
        ],
        neutral_pool=[
            "Feed solution is best used on the day it is mixed.",
            "Wear gloves when handling the concentrate.",
            "Rinse the watering cans after each feeding.",
        ],
        changing=f"Pots narrower than {width_limit} cm across get half the usual amount of feed solution.",
        case_lead=f"{name} is feeding a batch of {pots} {plant} at the {company} nursery.",
        case_rest=[
            f"Each pot in the batch is {width} cm across.",
            f"The batch stands in greenhouse {house}.",
            f"The batch was last fed on a {last_day}.",
        ],
        question="How many ml of concentrate does the batch need?",
        answers={
            "default": f"{total} ml",
            "changed": f"{changed} ml",
            "distractor": f"{per_pot * per_litre} ml",
            "filler": f"{total * 2} ml",
        },
        rule_applies=applies,
        rule_reasoning=(
            f"The pots are narrower than {width_limit} cm across, so each pot gets half the usual "
            f"feed solution, {_litres(Fraction(per_pot, 2))}, "
            f"and the batch needs {changed} ml of concentrate."
        ),
        distractor_reasoning=(
            f"Each pot gets {_litres(per_pot)} of solution with {per_litre} ml of concentrate per "
            f"litre, so {per_pot * per_litre} ml of concentrate is needed."
        ),
        params={"pots": pots, "litres_per_pot": per_pot, "ml_per_litre": per_litre,
                "width_limit_cm": width_limit, "pot_width_cm": width, "plant": plant},
    )


# ---------------------------------------------------------------------------------------
# knitting_pattern

_SIZE_NAMES = ("XS", "S", "M", "L", "XL", "2XL")
_YARN_BRANDS = ("Fernlea", "Moorside", "Tidewool", "Hollin", "Brackenfold", "Skerry",
                "Ashgill", "Lowmoor")
_HEAVY = ("aran", "chunky")
_LIGHT = ("4-ply", "sport", "DK")
_COLOURS = ("navy", "moss green", "rust", "charcoal", "cream", "plum", "mustard", "teal")


def draw_knitting_pattern(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    n = rng.choice((5, 6))
    f0, fstep = rng.randrange(80, 97, 2), rng.choice((8, 10, 12))
    c0, cstep = rng.randrange(80, 113, 4), rng.choice((8, 12, 16))
    finished = [f0 + i * fstep for i in range(n)]
    cast = [c0 + i * cstep for i in range(n)]
    ease = rng.choice((5, 6, 8, 10))
    pct = rng.choice((10, 15, 20, 25))
    chest = rng.randint(finished[0] - 10, finished[-1])

    def smallest(at_least: int) -> int:
        return next((i for i, f in enumerate(finished) if f >= at_least), n)

    target = chest + ease
    j = smallest(target)
    i = smallest(chest)
    # No borderline equalities, a smaller size reached without the ease (the distractor),
    # and a size above the default (the filler).
    if target in finished or chest in finished or j >= n - 1 or i >= j:
        raise Reject("borderline chest, or no distractor or filler size")
    changed = cast[j] * (100 - pct) // 100 // 4 * 4
    if changed in (cast[i], cast[j + 1], cast[j]):
        raise Reject("changed cast-on equals another option")
    weight = rng.choice(_HEAVY if applies else _LIGHT)
    company, name = rng.choice(COMPANIES), person(rng)
    first = name.split()[0]
    brand, colour = rng.choice(_YARN_BRANDS), rng.choice(_COLOURS)
    chart = "\n".join(f"   Size {s}: finished chest {f} cm, cast on {c} stitches"
                      for s, f, c in zip(_SIZE_NAMES, finished, cast))
    size = _SIZE_NAMES[j]
    return build_item(
        family="knitting_pattern", seed=seed, rng=rng,
        title=f"{company} sweater pattern",
        rules=[
            f"Sizes:\n{chart}",
            (f"Choose the smallest size whose finished chest is at least {ease} cm more than "
             "your own chest measurement."),
            "Cast on the number of stitches given for your size.",
        ],
        extra_rules=[
            "The body is knitted in one piece up to the armholes.",
            "Sleeves are picked up from the armhole edge.",
            "Weave in all ends before blocking.",
        ],
        neutral_pool=[
            "Block the finished sweater flat and let it dry fully.",
            "No buttons are needed for this pattern.",
            "Keep the yarn label in case more yarn is needed.",
        ],
        changing=(f"With aran or chunky weight yarn, cast on {pct}% fewer stitches than the size "
                  "chart gives, rounded down to a multiple of 4."),
        case_lead=f"{name} wants to knit this sweater.",
        case_rest=[
            f"{first}'s chest measures {chest} cm.",
            f"{first} is using {brand} yarn in {weight} weight.",
            f"{first} plans to knit the sweater in {colour}.",
        ],
        question=f"How many stitches should {first} cast on?",
        answers={
            "default": f"{cast[j]} stitches",
            "changed": f"{changed} stitches",
            "distractor": f"{cast[i]} stitches",
            "filler": f"{cast[j + 1]} stitches",
        },
        rule_applies=applies,
        rule_reasoning=(
            f"{first}'s yarn is aran or chunky weight, so {pct}% fewer stitches are cast on than "
            f"the {cast[j]} given for size {size}; rounded down to a multiple of 4, that is "
            f"{changed} stitches."
        ),
        distractor_reasoning=(
            f"{first}'s chest is {chest} cm, and the smallest size with a finished chest of at "
            f"least {chest} cm is size {_SIZE_NAMES[i]}, so {first} casts on {cast[i]} stitches."
        ),
        params={"finished_chest_cm": finished, "cast_on": cast, "ease_cm": ease,
                "chest_cm": chest, "reduce_pct": pct, "yarn_weight": weight},
    )


# ---------------------------------------------------------------------------------------
# ferry_fares

_RACKS = ("bike rack", "roof box")
_CAR_COLOURS = ("blue", "silver", "red", "white", "grey", "green", "black")


def _people(n: int, singular: str, plural: str) -> str:
    return f"no {plural}" if n == 0 else f"1 {singular}" if n == 1 else f"{n} {plural}"


def draw_ferry_fares(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    limit = rng.choice((48, 50, 52))  # tenths of a metre
    adult = rng.randrange(500, 1501, 50)
    child = pick(rng, [c for c in range(250, adult, 50) if 0.4 * adult <= c <= 0.6 * adult])
    car = rng.randrange(1800, 4501, 100)
    van = car + rng.randrange(800, 3001, 100)
    motorhome = van + rng.randrange(500, 2001, 100)
    others = rng.randint(1, 3)
    children = rng.randint(0, 2)
    if van - car == adult:
        raise Reject("van supplement equals an adult fare")
    passengers = others * adult + children * child
    default, changed = car + passengers, van + passengers
    rack = rng.choice(_RACKS)
    # Longer than the limit where the rule applies, shorter where not; never equal.
    length = (rng.randint(limit + 1, limit + 8) if applies
              else rng.randint(limit - 8, limit - 1))
    name = person(rng)
    first = name.split()[0]
    origin, dest = rng.sample(TOWNS, 2)
    hour = rng.randint(7, 20)
    colour = rng.choice(_CAR_COLOURS)
    return build_item(
        family="ferry_fares", seed=seed, rng=rng,
        title=f"{origin} ferry crossing fares",
        rules=[
            f"Foot passenger fares, one way: adult {money(adult)}, child under 14 {money(child)}.",
            (f"Vehicle fares, one way, including the driver:\n   Car: {money(car)}\n"
             f"   Van, or car with trailer: {money(van)}\n   Motorhome: {money(motorhome)}"),
            "Every person in a vehicle other than the driver pays the foot passenger fare.",
        ],
        extra_rules=[
            "The crossing takes about 40 minutes.",
            "Dogs travel free on the vehicle deck.",
            "Tickets can be bought at the quay or online.",
        ],
        neutral_pool=[
            "Hot drinks are sold in the passenger lounge.",
            "Vehicles should arrive at the quay 20 minutes before departure.",
            "Return tickets cost twice the one-way fare.",
        ],
        changing=(f"Cars longer than {limit // 10}.{limit % 10} m, "
                  "measured with any roof box or bike rack fitted, pay the van fare."),
        case_lead=f"{name} drives a car onto the {hour}:00 crossing from {origin} to {dest}.",
        case_rest=[
            (f"Besides {first}, the car carries {_people(others, 'adult', 'adults')} and "
             f"{_people(children, 'child under 14', 'children under 14')}."),
            f"With its {rack} fitted, {first}'s car is {length // 10}.{length % 10} m long.",
            f"{first}'s car is {colour}.",
        ],
        question="What does the crossing cost in all, one way?",
        answers={
            "default": money(default),
            "changed": money(changed),
            "distractor": money(default + adult),
            "filler": money(changed + adult),
        },
        rule_applies=applies,
        rule_reasoning=(
            f"With its {rack} fitted, {first}'s car is longer than "
            f"{limit // 10}.{limit % 10} m, so it pays the van fare of "
            f"{money(van)}, and the crossing costs {money(changed)} in all."
        ),
        distractor_reasoning=(
            f"Everyone in the car pays the foot passenger fare on top of the car fare, the driver "
            f"included, so the crossing costs {money(default + adult)}."
        ),
        params={"adult_cents": adult, "child_cents": child, "car_cents": car, "van_cents": van,
                "motorhome_cents": motorhome, "other_adults": others, "children": children,
                "limit_dm": limit, "length_dm": length, "rack": rack},
    )


# ---------------------------------------------------------------------------------------
# curtain_fabric

_PILE = ("velvet", "chenille", "corduroy")
_FLAT = ("cotton", "linen", "sateen", "voile", "polyester")
_FABRIC_COLOURS = ("sage", "ivory", "burgundy", "slate blue", "ochre", "dove grey", "forest green")
_ROOMS = ("bedroom", "living room", "study", "dining room", "guest room", "kitchen")


def _metres(cm: int) -> str:
    return f"{cm // 100}.{cm % 100:02d} m"


def draw_curtain_fabric(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    hem = rng.choice((20, 25, 30))
    extra = rng.choice((8, 10, 12, 15))
    length = rng.randrange(120, 261, 5)
    widths = rng.randint(2, 8)
    drop = length + hem
    default, changed = widths * drop, widths * (drop + extra)
    distractor, filler = widths * length, (widths + 1) * drop
    if len({default, changed, distractor, filler}) < 4:
        raise Reject("options not distinct")
    fabric = rng.choice(_PILE if applies else _FLAT)
    company, name = rng.choice(COMPANIES), person(rng)
    colour, room = rng.choice(_FABRIC_COLOURS), rng.choice(_ROOMS)
    return build_item(
        family="curtain_fabric", seed=seed, rng=rng,
        title=f"{company} curtain making guide",
        rules=[
            (f"Each drop (the length of fabric cut for one width) is the finished curtain length "
             f"plus {hem} cm for hems."),
            "Fabric needed = number of widths × length of one drop.",
            "Fabric is ordered in metres: divide the total in centimetres by 100.",
        ],
        extra_rules=[
            "Linings are ordered separately.",
            "Allow two weeks for making up.",
            "Curtain tape is included in the making-up price.",
        ],
        neutral_pool=[
            "Curtains are pressed before delivery.",
            "Hooks and gliders are supplied with every pair.",
            "Fabric samples can be posted free of charge.",
        ],
        changing=(f"Pile fabrics (velvet, chenille and corduroy) need {extra} cm more per drop, "
                  "so that the pile runs the same way on every width."),
        case_lead=f"{name} orders a pair of curtains from {company}.",
        case_rest=[
            f"The finished curtains are {length} cm long.",
            f"The pair of curtains needs {widths} widths of fabric in all.",
            f"The chosen fabric is {colour} {fabric}.",
            f"The curtains will hang in {name.split()[0]}'s {room}.",
        ],
        question="How many metres of fabric should be ordered?",
        answers={
            "default": _metres(default),
            "changed": _metres(changed),
            "distractor": _metres(distractor),
            "filler": _metres(filler),
        },
        rule_applies=applies,
        rule_reasoning=(
            f"The chosen fabric is a pile fabric, so each drop needs {extra} cm more, "
            f"{drop + extra} cm in all, and {_metres(changed)} of fabric should be ordered."
        ),
        distractor_reasoning=(
            f"Each width is as long as the finished curtain, {length} cm, so {widths} widths need "
            f"{_metres(distractor)} of fabric."
        ),
        params={"finished_length_cm": length, "hem_cm": hem, "widths": widths,
                "pile_extra_cm": extra, "fabric": fabric},
    )


# ---------------------------------------------------------------------------------------
# bike_rental

_HOTELS = ("Harbour Inn", "Linden Lodge", "Old Mill Hotel", "Fox and Crown", "Seaview House",
           "Willow Court Hotel", "Kingfisher Inn", "Ridgeway Lodge", "Larch Hall",
           "Meadow Inn", "Copper Kettle Inn", "Heron Bay Hotel")


def draw_bike_rental(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    rate = rng.randint(9, 25)
    days = rng.randint(3, 10)
    bikes = rng.randint(2, 8)
    full = days * rate
    # The cap lies well below the full hire charge per bike in both kinds.
    cap = pick(rng, [w for w in range(10, full, 5) if 0.4 * full <= w <= 0.85 * full])
    default, changed = bikes * full, bikes * cap
    distractor, filler = full, bikes * (days + 1) * rate
    if len({default, changed, distractor, filler}) < 4:
        raise Reject("options not distinct")
    partners = rng.sample(_HOTELS, 3)
    hotel = rng.choice(partners if applies else [h for h in _HOTELS if h not in partners])
    company, name = rng.choice(COMPANIES), person(rng)
    town = rng.choice(TOWNS)
    day = rng.choice(WEEKDAYS)
    return build_item(
        family="bike_rental", seed=seed, rng=rng,
        title=f"{company} cycle hire price list",
        rules=[
            f"Bike hire costs {money(rate * 100)} per bike per day.",
            "Hire charge = number of bikes × number of days × daily rate.",
            "Helmets and locks are included at no extra charge.",
        ],
        extra_rules=[
            "Every bike is checked before each hire.",
            "Child seats can be fitted on request.",
            "The shop opens at 08:30.",
        ],
        neutral_pool=[
            "Punctures are repaired free of charge during the hire.",
            "Route maps are available at the counter.",
            "Bikes can be returned until 18:00.",
        ],
        changing=(f"Guests of the {partners[0]}, the {partners[1]} and the {partners[2]} pay at "
                  f"most {money(cap * 100)} per bike for one hire, however many days it lasts."),
        case_lead=f"{name} hires {bikes} bikes for a group for {days} days.",
        case_rest=[
            f"{name.split()[0]}'s group is staying at the {hotel}.",
            f"{name.split()[0]}'s group plans to ride to {town}.",
            f"The bikes are picked up on a {day} morning.",
        ],
        question="What is the hire charge for the group's bikes?",
        answers={
            "default": money(default * 100),
            "changed": money(changed * 100),
            "distractor": money(distractor * 100),
            "filler": money(filler * 100),
        },
        rule_applies=applies,
        rule_reasoning=(
            f"The group is staying at one of the partner hotels, so each bike costs at most "
            f"{money(cap * 100)} for the hire, and the group pays {bikes} × {money(cap * 100)} = "
            f"{money(changed * 100)}."
        ),
        distractor_reasoning=(
            f"One bike for {days} days at {money(rate * 100)} a day costs {money(full * 100)}, "
            f"so the hire charge is {money(full * 100)}."
        ),
        params={"rate": rate, "days": days, "bikes": bikes, "cap": cap,
                "partner_hotels": partners, "hotel": hotel},
    )


FAMILIES = {
    "plant_feed_dosing": draw_plant_feed_dosing,
    "knitting_pattern": draw_knitting_pattern,
    "ferry_fares": draw_ferry_fares,
    "curtain_fabric": draw_curtain_fabric,
    "bike_rental": draw_bike_rental,
}
