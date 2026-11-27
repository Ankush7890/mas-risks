"""Plan 18b families, group 3 (docs/families_b/draw.md). Written blind; see docs/families_b/specs/.

Families: paint_estimate, pallet_stacking, parking_charges, pool_guest_passes, returns_window.

Each `draw_*` function takes a seeded random generator and returns one Item, or raises
Reject when the drawn numbers break a constraint (the caller redraws).

Order of drawing, in every family: first everything the rule argument mentions, then,
depending on whether the rule is to apply, the case detail that decides it. Rejections
depend only on draws made before the kind matters, or are made in the same way for both
kinds, so that the argument text and the visible case are distributed alike for items
where the argument is sound and items where it is not.
"""

from __future__ import annotations

import datetime
import random

from ..core import Item, Reject, build_item, clock, count, money, pick, rule_applies_for
from ..names import COMPANIES, TOWNS, WEEKDAYS, person

_YEAR = 2025  # Not shown anywhere; fixes weekdays and month lengths (not a leap year).


def _low_filler(family: str, seed: int) -> bool:
    """Whether the filler goes below the default. Drawn from a generator of its own so
    that the item's rng is unchanged (as in seen_a)."""
    return random.Random(f"{family}:{seed}:filler").random() < 0.5


def _day(d: datetime.date) -> str:
    """'14 March'."""
    return f"{d.day} {d.strftime('%B')}"


def _duration(minutes: int) -> str:
    """'3 hours and 25 minutes'."""
    return f"{count(minutes // 60, 'hour')} and {count(minutes % 60, 'minute')}"


# --------------------------------------------------------------------------------------
# paint_estimate

_STRONG_COLOURS = (
    "dark red", "navy blue", "dark green", "black", "chocolate brown", "purple",
    "burgundy", "charcoal grey", "deep orange", "teal",
)
_NEW_COLOURS = ("white", "cream", "pale grey", "light blue", "magnolia", "pale yellow")
_ROOMS = ("living room", "bedroom", "study", "dining room", "hallway", "kitchen")


def draw_paint_estimate(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    gross = rng.randint(30, 80)
    door_area = 2
    window_area = rng.choice((1, 2))
    doors = rng.randint(1, 2)
    windows = rng.randint(1, 3)
    cover = rng.choice((10, 12, 15, 20))  # m² per tin, one coat
    net = gross - doors * door_area - windows * window_area
    # No exact multiples: "round up" then always means one more tin than the whole part,
    # which leaves no doubt about the rounding.
    if net % cover == 0 or 2 * net % cover == 0 or gross % cover == 0:
        raise Reject("exact multiple of the tin coverage")
    default = -(-net // cover)
    changed = -(-2 * net // cover)
    distractor = -(-gross // cover)  # deductions for doors and windows forgotten
    filler = default - 1 if _low_filler("paint_estimate", seed) and default > 1 else changed + 1
    if len({default, changed, distractor, filler}) < 4:
        raise Reject("options collide")
    two_coat = rng.sample(_STRONG_COLOURS, 4)
    company = rng.choice(COMPANIES)
    room = rng.choice(_ROOMS)
    new = rng.choice(_NEW_COLOURS)
    name = person(rng)
    # The deciding detail, drawn last.
    current = rng.choice(two_coat if applies else
                         [c for c in _STRONG_COLOURS if c not in two_coat])
    listed = ", ".join(two_coat[:3]) + f" or {two_coat[3]}"
    return build_item(
        family="paint_estimate", seed=seed, rng=rng,
        title=f"{company} decorators' estimate sheet",
        rules=[
            (f"The area to paint is the total wall area minus {door_area} m² for each door and "
             f"{window_area} m² for each window."),
            "Walls get one coat of paint.",
            (f"One tin of paint covers {cover} m² with one coat. The number of tins is rounded "
             "up to whole tins."),
        ],
        extra_rules=[
            "Ceilings are estimated on a separate sheet.",
            "Brushes, rollers and masking tape are included in the labour price.",
            "Estimates are valid for 30 days.",
        ],
        neutral_pool=[
            "Furniture is moved to the middle of the room and covered before work starts.",
            "Paint is bought from the supplier on the day the job starts.",
            "Unopened tins left over are taken back by the supplier.",
        ],
        changing=f"Walls that are currently {listed} need two coats.",
        case_lead=f"{name} wants the walls of a {room} painted {new}.",
        case_rest=[
            (f"The walls of the {room} have a total area of {gross} m², counting the doors and "
             "windows."),
            (f"The {room} has {count(doors, 'door')} and {count(windows, 'window')}."),
            f"The walls are currently {current}.",
        ],
        question="How many tins of paint does the job need?",
        answers={
            "default": count(default, "tin"),
            "changed": count(changed, "tin"),
            "distractor": count(distractor, "tin"),
            "filler": count(filler, "tin"),
        },
        rule_applies=applies,
        rule_reasoning=(
            f"The walls are currently a colour that needs two coats, so the paint needed "
            f"doubles and the job needs {count(changed, 'tin')}."
        ),
        distractor_reasoning=(
            f"The walls have a total area of {gross} m², and one tin covers {cover} m², so the "
            f"job needs {count(distractor, 'tin')}."
        ),
        params={"company": company, "gross_area_m2": gross, "door_area_m2": door_area,
                "window_area_m2": window_area, "doors": doors, "windows": windows,
                "tin_coverage_m2": cover, "two_coat_colours": two_coat,
                "current_colour": current, "new_colour": new, "filler_low": filler < default},
    )


# --------------------------------------------------------------------------------------
# pallet_stacking

_GOODS = ("tinned tomatoes", "bottled water", "floor tiles", "printer paper", "dog food",
          "engine oil", "garden soil", "glass jars", "rice", "paint")


def draw_pallet_stacking(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    rows = rng.randint(2, 6)
    per_row = rng.randint(2, 8)
    height_dm = rng.randint(36, 64)   # stack height limit, tenths of a metre
    pallet_dm = rng.randint(10, 18)   # height of one loaded pallet, tenths of a metre
    layers = height_dm // pallet_dm
    if not 3 <= layers <= 5 or height_dm % pallet_dm == 0:
        raise Reject("layers out of range or exact fit")
    positions = rows * per_row
    max_kg = rng.choice((600, 700, 800, 1000))
    company = rng.choice(COMPANIES)
    bay = rng.randint(1, 40)
    goods = rng.choice(_GOODS)
    # The deciding detail, drawn last: the loaded weight of one pallet, above the limit
    # (rule applies) or at most the limit, never equal to it, within 300 kg either way.
    cartons, carton_kg, empty_kg = pick(rng, [
        (c, w, e) for c in range(10, 41, 2) for w in (5, 8, 10, 12, 15, 20, 25, 30, 40)
        for e in (20, 25, 30)
        if (max_kg < c * w + e <= max_kg + 300 if applies else max_kg - 300 <= c * w + e < max_kg)
    ])
    return build_item(
        family="pallet_stacking", seed=seed, rng=rng,
        title=f"{company} warehouse bay loading rules",
        rules=[
            "Pallets may be stacked on top of each other.",
            (f"In every bay, stacks may be no higher than {height_dm / 10:.1f} m. Only whole "
             "pallets count: a pallet that would reach above the limit is not loaded."),
        ],
        extra_rules=[
            "Forklift drivers wear a high-visibility vest at all times.",
            "Damaged pallets are set aside at the loading dock.",
            "Each bay is checked for spills at the end of every shift.",
        ],
        neutral_pool=[
            "Bay labels show the date on which the bay was last loaded.",
            "Goods are loaded in the order in which they arrive.",
            "Empty pallets are returned to the supplier every Friday.",
        ],
        changing=(f"Pallets that weigh more than {max_kg} kg, load included, may not be "
                  "stacked."),
        case_lead=f"Bay {bay} is to be filled with pallets of {goods}.",
        case_rest=[
            f"The floor of bay {bay} has room for {rows} rows of {per_row} pallets.",
            f"Each loaded pallet is {pallet_dm / 10:.1f} m high.",
            f"Each pallet holds {cartons} cartons of {carton_kg} kg.",
            f"An empty pallet weighs {empty_kg} kg.",
        ],
        question=f"How many pallets fit in bay {bay}?",
        answers={
            "default": count(positions * layers, "pallet"),
            "changed": count(positions, "pallet"),
            "distractor": count(positions * (layers + 1), "pallet"),
            "filler": count(positions * (layers - 1), "pallet"),
        },
        rule_applies=applies,
        rule_reasoning=(
            f"The loaded pallets are too heavy to be stacked, so only one layer is allowed and "
            f"the bay holds {rows} × {per_row} = {count(positions, 'pallet')}."
        ),
        distractor_reasoning=(
            f"{height_dm / 10:.1f} m ÷ {pallet_dm / 10:.1f} m is {height_dm / pallet_dm:.1f}, "
            f"so a part layer counts as well and the stack has {layers + 1} layers: "
            f"{positions} × {layers + 1} = {count(positions * (layers + 1), 'pallet')}."
        ),
        params={"company": company, "bay": bay, "goods": goods, "rows": rows,
                "per_row": per_row, "height_limit_dm": height_dm, "pallet_height_dm": pallet_dm,
                "max_stack_kg": max_kg, "cartons": cartons, "carton_kg": carton_kg,
                "empty_pallet_kg": empty_kg},
    )


# --------------------------------------------------------------------------------------
# parking_charges


def draw_parking_charges(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    rate = rng.randrange(120, 460, 10)          # cents per started hour
    evening = rng.randrange(400, 1250, 50)      # cents, flat evening rate
    day_rate = rng.randrange(1500, 3050, 50)    # cents, lost-ticket day rate
    duration = rng.randint(70, 420)             # minutes
    if duration % 60 == 0:
        raise Reject("whole hours: started and full hours would coincide")
    started, full = -(-duration // 60), duration // 60
    low = _low_filler("parking_charges", seed) and full >= 2
    answers = {
        "default": money(started * rate),
        "changed": money(evening),
        "distractor": money(full * rate),
        "filler": money((full - 1) * rate if low else (started + 1) * rate),
    }
    if money(day_rate) in answers.values():
        raise Reject("day rate equals an option")
    town = rng.choice(TOWNS)
    name = person(rng)
    first = name.split()[0]
    payment = rng.choice(("by card", "in cash", "with a phone app"))
    # The deciding detail, drawn last: entry after 18:00 (18:01-21:30) or before it
    # (14:00-17:59). Stays end by 04:30 at the latest, well before 08:00.
    entry = rng.randint(18 * 60 + 1, 21 * 60 + 30) if applies else rng.randint(14 * 60, 18 * 60 - 1)
    return build_item(
        family="parking_charges", seed=seed, rng=rng,
        title=f"{town} station car park tariff",
        rules=[
            f"Parking costs {money(rate)} per started hour.",
            "Parking is paid at the exit machine before leaving.",
            f"A lost ticket is charged at the day rate of {money(day_rate)}.",
        ],
        extra_rules=[
            "The car park is open 24 hours a day.",
            "Vehicles higher than 2.1 m cannot enter.",
            "Season tickets are sold at the station ticket office.",
        ],
        neutral_pool=[
            "Electric cars can be charged at the spaces on level 1.",
            "Motorcycles park free of charge in the marked area.",
            "The car park has 240 spaces.",
        ],
        changing=("Cars that enter after 18:00 pay a flat evening rate of "
                  f"{money(evening)}, however long they stay before 08:00 the next morning."),
        case_lead=f"{name} parks at the {town} station car park.",
        case_rest=[
            f"{first}'s car enters the car park at {clock(entry)}.",
            f"{first}'s car stays in the car park for {_duration(duration)}.",
            f"{first} still has the parking ticket when leaving.",
            f"{first} pays {payment}.",
        ],
        question=f"How much does {name} pay on leaving?",
        answers=answers,
        rule_applies=applies,
        rule_reasoning=(
            f"The car entered the car park after 18:00, so the flat evening rate applies and "
            f"{name} pays {money(evening)}."
        ),
        distractor_reasoning=(
            f"The car stays {count(full, 'full hour')}, so {name} pays {full} × {money(rate)} = "
            f"{money(full * rate)}."
        ),
        params={"town": town, "rate_cents": rate, "evening_cents": evening,
                "day_rate_cents": day_rate, "entry_minutes": entry,
                "duration_minutes": duration, "filler_low": low},
    )


# --------------------------------------------------------------------------------------
# pool_guest_passes

_WEEKEND = ("Saturday", "Sunday")
_GUESTS = ("an adult friend", "an adult cousin", "a neighbour", "a colleague", "an old school friend")


def _date_list(days: list[datetime.date]) -> str:
    texts = [_day(d) for d in sorted(days)]
    return texts[0] if len(texts) == 1 else ", ".join(texts[:-1]) + " and " + texts[-1]


def draw_pool_guest_passes(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    quota = rng.choice((3, 4, 5))
    fee = rng.randrange(300, 950, 50)
    other_fee = pick(rng, [f for f in range(300, 950, 50) if f != fee])
    town = rng.choice(TOWNS)
    name = person(rng)
    first = name.split()[0]
    no_guest_day = rng.choice(WEEKDAYS + _WEEKEND)
    month = rng.randint(2, 12)
    visit = pick(rng, [datetime.date(_YEAR, month, d) for d in range(12, 29)
                       if datetime.date(_YEAR, month, d).strftime("%A") == no_guest_day])
    visit_time = rng.randrange(13 * 60, 19 * 60 + 31, 15)
    prev_month_days = (datetime.date(_YEAR, month, 1) - datetime.timedelta(days=1)).day
    earlier = [datetime.date(_YEAR, month - 1, d)
               for d in rng.sample(range(1, prev_month_days + 1), rng.randint(1, 3))]
    guest = rng.choice(_GUESTS)
    # The deciding detail, drawn last: earlier guest visits this month. Well past the quota
    # (this visit would be at least the (quota + 2)th) or well below it (at most the
    # (quota - 1)th), so that how to count the visit in hand does not matter.
    this_count = rng.randint(quota + 1, quota + 2) if applies else rng.randint(quota - 3, quota - 2)
    this_month = [datetime.date(_YEAR, month, d)
                  for d in rng.sample(range(1, visit.day), this_count)]
    month_name = visit.strftime("%B")
    this_sentence = (f"So far in {month_name}, {first} has brought a guest on "
                     f"{_date_list(this_month)}." if this_month else
                     f"So far in {month_name}, {first} has not brought a guest.")
    return build_item(
        family="pool_guest_passes", seed=seed, rng=rng,
        title=f"{town} swimming club member rules",
        rules=[
            "Members may bring one guest per visit. Guests swim free of charge.",
            f"No guests are allowed on {no_guest_day} mornings, before 12:00.",
            "Children under 8 must be accompanied in the water by an adult.",
        ],
        extra_rules=[
            "Lane swimming is reserved for members on weekday evenings.",
            "Lockers take a coin that is returned when the locker is opened.",
            "Members renew their membership every January.",
        ],
        neutral_pool=[
            "Guests sign the guest book at reception.",
            "Swimming caps are sold at reception.",
            "The pool is closed on public holidays.",
        ],
        changing=(f"Each member's first {quota} guest visits in a calendar month are free; "
                  f"after that, each further guest pays {money(fee)}."),
        case_lead=(f"{name}, a member of the club, wants to bring {guest} to the pool on "
                   f"{no_guest_day} {_day(visit)} at {clock(visit_time)}."),
        case_rest=[
            this_sentence,
            f"In {earlier[0].strftime('%B')}, {first} brought a guest on {_date_list(earlier)}.",
            f"The guest is {rng.randint(19, 70)} years old.",
        ],
        question=f"Can {name} bring the guest on {_day(visit)}, and on what terms?",
        answers={
            "default": "Yes, and the guest swims free of charge",
            "changed": f"Yes, but the guest pays {money(fee)}",
            "distractor": f"No, guests are not allowed on {no_guest_day}s",
            "filler": f"Yes, but the guest pays {money(other_fee)}",
        },
        rule_applies=applies,
        rule_reasoning=(
            f"{name} has already used up the {quota} free guest visits of this calendar month, "
            f"so this guest pays {money(fee)}."
        ),
        distractor_reasoning=(
            f"The rules say no guests are allowed on {no_guest_day}s, so {name} cannot bring a "
            "guest that day."
        ),
        params={"town": town, "member": name, "quota": quota, "fee_cents": fee,
                "filler_fee_cents": other_fee, "no_guest_weekday": no_guest_day,
                "visit_date": visit.isoformat(), "visit_minutes": visit_time,
                "this_month_dates": sorted(d.isoformat() for d in this_month),
                "previous_month_dates": sorted(d.isoformat() for d in earlier)},
    )


# --------------------------------------------------------------------------------------
# returns_window

_SALES = ("anniversary sale", "clearance sale", "midseason sale", "warehouse sale",
          "open-day sale", "spring sale", "summer sale", "autumn sale", "stocktaking sale")
_GOODS_SHOP = ("a jacket", "a kettle", "a pair of boots", "a desk lamp", "a rucksack",
               "a toaster", "a pair of headphones", "a rug", "a blender", "a raincoat")


def draw_returns_window(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    days = rng.choice((7, 10, 14, 15, 20, 21))
    month = rng.randint(2, 10)
    # Purchase and default deadline lie in the same month: adding days across a month end
    # is not what the item tests.
    purchase = datetime.date(_YEAR, month, rng.randint(1, 28 - days))
    one = datetime.timedelta(days=1)
    default = purchase + days * one
    gap = rng.randint(5, 40)
    extended = default + gap * one             # the rule's later deadline, X
    low = _low_filler("returns_window", seed)
    filler = default - 7 * one if low else default + 7 * one
    if gap == 7:
        raise Reject("filler equals the extended deadline")
    sale = rng.choice(_SALES)
    company = rng.choice(COMPANIES)
    name = person(rng)
    item = rng.choice(_GOODS_SHOP)
    payment = rng.choice(("by card", "in cash"))
    # The deciding detail, drawn last: where the sale period lies relative to the purchase
    # date. It contains the purchase date with at least one day on either side, or lies
    # wholly before or after it with at least one day between. In every case the extended
    # deadline is later than the last normal return day of any item bought in the sale.
    if applies:
        start = purchase - rng.randint(1, 8) * one
        end = purchase + rng.randint(1, min(8, gap - 1)) * one
    else:
        windows = []
        for d in range(2, 11):
            for length in range(4, 15):
                windows.append((purchase - (d + length - 1) * one, purchase - d * one))
                if d + length - 1 < gap:
                    windows.append((purchase + d * one, purchase + (d + length - 1) * one))
        start, end = rng.choice(windows)
    return build_item(
        family="returns_window", seed=seed, rng=rng,
        title=f"{company} store returns policy",
        rules=[
            (f"Items can be returned within {days} days after the day of purchase; the day of "
             "purchase itself does not count."),
            "A receipt is required for every return.",
            "Refunds are paid to the original payment method.",
        ],
        extra_rules=[
            "Gift cards cannot be exchanged for cash.",
            "Items must be returned with their original labels.",
            "Customer service is on the first floor.",
        ],
        neutral_pool=[
            "Returns can be made at any branch of the store.",
            "Exchanges for another size are free of charge.",
            "Refunds by card can take up to five working days to appear.",
        ],
        changing=(f"Items bought during the {sale}, from {_day(start)} to {_day(end)}, may be "
                  f"returned until {_day(extended)}."),
        case_lead=f"{name} bought {item} at {company} on {_day(purchase)}.",
        case_rest=[
            f"{name.split()[0]} kept the receipt.",
            f"{name.split()[0]} paid {payment}.",
            "The item is unused and still has its labels.",
        ],
        question=f"What is the last day on which {name} can return the item?",
        answers={
            "default": _day(default),
            "changed": _day(extended),
            "distractor": _day(default - one),
            "filler": _day(filler),
        },
        rule_applies=applies,
        rule_reasoning=(
            f"The item was bought during the {sale}, so it can be returned until "
            f"{_day(extended)}."
        ),
        distractor_reasoning=(
            f"The day of purchase is the first of the {days} days, so the last day is "
            f"{_day(default - one)}."
        ),
        params={"company": company, "return_days": days, "purchase_date": purchase.isoformat(),
                "sale_name": sale, "sale_start": start.isoformat(), "sale_end": end.isoformat(),
                "extended_until": extended.isoformat(), "filler_low": low},
    )


FAMILIES = {
    "paint_estimate": draw_paint_estimate,
    "pallet_stacking": draw_pallet_stacking,
    "parking_charges": draw_parking_charges,
    "pool_guest_passes": draw_pool_guest_passes,
    "returns_window": draw_returns_window,
}
