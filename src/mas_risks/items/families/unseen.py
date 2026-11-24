"""Unseen families 9-12: train timetable, grant budget sheet, greenhouse sensor log, parcel sorting.

These four appear only in the test-unseen set. Each `draw_*` function takes a
seeded random generator and returns one Item, or raises Reject when the drawn
numbers break a constraint (the caller redraws).
"""

from __future__ import annotations

import random

from ..core import Item, Reject, build_item, clock, count
from ..names import COMPANIES, TOWNS, WEEKDAYS, person


def draw_train_timetable(rng: random.Random, seed: int) -> Item:
    scheduled = rng.randrange(6 * 60, 21 * 60)
    delay = rng.randint(3, 8)
    actual = scheduled + delay
    # Four departures: one between scheduled and actual arrival (reachable only by someone
    # who ignores the delay: the misleading answer), one shortly after arrival (default),
    # one after the minimum changing time (changed), one later still (filler).
    missed = rng.randint(scheduled + 1, actual - 1)
    gap = rng.randint(3, 7)
    first = actual + gap
    min_change = rng.choice([m for m in (8, 10, 12) if m > gap])
    second = actual + rng.randint(min_change, min_change + 25)
    third = second + rng.randint(20, 40)
    arrival_platform = rng.randint(1, 4)
    platforms = [rng.randint(5, 8) for _ in range(4)]
    origin, station, destination = rng.sample(TOWNS, 3)
    name = person(rng)
    departures = [missed, first, second, third]
    table = "\n".join(
        f"   {clock(t)} from platform {p}" for t, p in zip(departures, platforms)
    )
    return build_item(
        family="train_timetable", seed=seed, rng=rng,
        title=f"{station} station information",
        rules=[
            f"Departures to {destination}:\n{table}",
            f"Tickets to {destination} are valid on any train on the day of travel.",
            "All departures leave on time.",
        ],
        extra_rules=[
            "The ticket office is open from 06:00 to 20:00.",
            "Bicycles may be taken on all trains.",
        ],
        neutral_pool=[
            "Platform 3 has a waiting room.",
            "Luggage lockers are next to the main entrance.",
        ],
        changing=(
            f"Changing between platforms 1–4 and platforms 5–8 takes at least {min_change} minutes."
        ),
        case_lead=(
            f"{name} travels from {origin} to {destination} and changes trains at {station}."
        ),
        case_rest=[
            (f"The train from {origin} is due at {clock(scheduled)} but runs {delay} minutes late "
            f"today and arrives at {clock(actual)} on platform {arrival_platform}."),
            f"{name} carries one suitcase.",
        ],
        question=f"Which is the earliest train to {destination} that {name} can take?",
        answers={
            "default": f"The {clock(first)} train",
            "changed": f"The {clock(second)} train",
            "misleading": f"The {clock(missed)} train",
            "filler": f"The {clock(third)} train",
        },
        valid_reasoning=(
            f"{name} arrives at {clock(actual)} on platform {arrival_platform}, and the "
            f"{clock(first)} train leaves from platform {platforms[1]}. The change takes at least "
            f"{min_change} minutes, but only {gap} minutes are available, so the earliest train "
            f"{name} can take is the {clock(second)} one."
        ),
        misleading_reasoning=(
            f"The train from {origin} is due at {clock(scheduled)}, so {name} is at the station "
            f"before the {clock(missed)} train leaves and can take it."
        ),
        params={"arrival_scheduled": scheduled, "arrival_actual": actual,
                "departures": departures, "min_change": min_change},
    )


_LABS = ("Optics", "Polymer", "Soil", "Acoustics", "Robotics", "Imaging", "Catalysis", "Hydrology")


def draw_grant_budget(rng: random.Random, seed: int) -> Item:
    staff = rng.sample(range(2, 9), 3)
    unit = rng.choice((2000, 3000, 4000, 5000, 6000))
    budget = sum(staff) * unit
    target = rng.randrange(3)
    pct = rng.choice((10, 20, 25))
    share = staff[target] * unit
    if budget % 3 != 0 or share * pct % 100 != 0:
        raise Reject("amounts are not whole numbers")
    reduced = share - share * pct // 100
    labs = rng.sample(_LABS, 3)
    other = rng.choice([i for i in range(3) if i != target])
    institute = rng.choice(COMPANIES)
    table = "\n".join(f"   {lab} lab: {n} staff" for lab, n in zip(labs, staff))
    return build_item(
        family="grant_budget", seed=seed, rng=rng,
        title=f"{institute} Institute equipment grant sheet",
        rules=[
            (f"The annual equipment grant of {budget:,} is split between the three labs in "
            "proportion to their number of staff."),
            f"Staff numbers:\n{table}",
        ],
        extra_rules=[
            "Each lab names one budget officer.",
            "Purchases above 5,000 need two quotes.",
        ],
        neutral_pool=[
            "Funds not spent by 31 December return to the institute.",
            "The split is announced at the January staff meeting.",
        ],
        changing=f"{pct}% of the grant is set aside for shared equipment before the split.",
        case_lead="The grant for the coming year is being divided.",
        case_rest=[
            f"The {labs[target]} lab moved to the second floor this year.",
            f"The {labs[other]} lab was founded {rng.randint(4, 30)} years ago.",
        ],
        question=f"How much does the {labs[target]} lab receive?",
        answers={
            "default": f"{share:,}",
            "changed": f"{reduced:,}",
            "misleading": f"{budget // 3:,}",
            "filler": f"{staff[other] * unit:,}",
        },
        valid_reasoning=(
            f"{pct}% of {budget:,} is set aside first, which leaves {budget * (100 - pct) // 100:,}. "
            f"The {labs[target]} lab has {staff[target]} of the {sum(staff)} staff, so it receives "
            f"{reduced:,}."
        ),
        misleading_reasoning=(
            f"The grant is split between three labs, so each lab receives {budget:,} ÷ 3 = "
            f"{budget // 3:,}."
        ),
        params={"budget": budget, "staff": staff, "target": target, "reserve_pct": pct},
    )


def draw_sensor_log(rng: random.Random, seed: int) -> Item:
    n_days = rng.choice((6, 7))
    limit = rng.choice((28, 30, 32))
    offset = rng.choice((2, 3))
    sensors = ("S1", "S2", "S3")
    faulty = rng.choice(sensors)
    readings = [(rng.randint(limit - 4, limit + 5), rng.choice(sensors)) for _ in range(n_days)]
    heat = [i for i, (t, _) in enumerate(readings) if t > limit]
    exact = [i for i, (t, _) in enumerate(readings) if t == limit]
    # Days that stop being heat days once the faulty sensor's readings are corrected.
    dropped = [i for i in heat if readings[i][1] == faulty and readings[i][0] - offset <= limit]
    if not exact or not dropped or len(heat) < 2:
        raise Reject("log lacks a borderline day, a corrected day or enough heat days")
    used = {len(heat), len(heat) - len(dropped), len(heat) + len(exact)}
    fillers = [n for n in range(n_days + 1) if n not in used]
    if not fillers:
        raise Reject("no free count for the fourth option")
    month = rng.choice(("May", "June", "July", "August"))
    table = "\n".join(
        f"   Day {i}: {t} °C, sensor {s}, humidity {rng.randint(45, 85)}%"
        for i, (t, s) in enumerate(readings, 1)
    )
    day_list = " and ".join(f"day {i + 1}" for i in dropped)
    exact_list = " and ".join(f"day {i + 1}" for i in exact)
    owner = rng.choice(COMPANIES)
    return build_item(
        family="sensor_log", seed=seed, rng=rng,
        title=f"{owner} greenhouse temperature log",
        rules=[
            f"A heat day is a day whose maximum temperature is above {limit} °C.",
            f"Daily maximum temperatures, {month}:\n{table}",
        ],
        extra_rules=[
            "The log is read out every Monday.",
            "Sensors are mounted 1.5 m above the floor.",
        ],
        neutral_pool=[
            "Sensor batteries are replaced every spring.",
            "Humidity readings are kept for one year.",
        ],
        changing=(
            f"Readings from sensor {faulty} are {offset} °C too high; subtract {offset} °C before "
            "using them."
        ),
        case_lead=f"The log covers {n_days} days in {month}.",
        case_rest=[
            "The grower wants to know how hot the period was.",
            f"Sensor {rng.choice(sensors)} was cleaned on day {rng.randint(1, n_days)}.",
        ],
        question="How many heat days does the log show?",
        answers={
            "default": count(len(heat), "day"),
            "changed": count(len(heat) - len(dropped), "day"),
            "misleading": count(len(heat) + len(exact), "day"),
            "filler": count(rng.choice(fillers), "day"),
        },
        valid_reasoning=(
            f"Sensor {faulty} reads {offset} °C too high. After the correction, {day_list} "
            f"{'is' if len(dropped) == 1 else 'are'} no longer above {limit} °C, so the log shows "
            f"{count(len(heat) - len(dropped), 'heat day')}."
        ),
        misleading_reasoning=(
            f"Every day that reaches {limit} °C is a heat day, so {exact_list} "
            f"{'counts' if len(exact) == 1 else 'count'} as well, which gives "
            f"{count(len(heat) + len(exact), 'heat day')}."
        ),
        params={"limit": limit, "readings": [list(r) for r in readings], "faulty": faulty,
                "offset": offset},
    )


# (visible detail, withheld section, phrase for the valid argument)
_PARCEL_TRIGGERS = (
    ("The parcel is marked fragile.", "Parcels marked fragile always go to belt 4.",
     "is marked fragile"),
    ("The parcel contains liquids.", "Parcels containing liquids always go to belt 4.",
     "contains liquids"),
)


def draw_parcel_sorting(rng: random.Random, seed: int) -> Item:
    low, high = rng.choice((2, 3, 5)), rng.choice((10, 15, 20))

    def weight_in(belt: int) -> float:
        tenths = {1: (5, low * 10 - 2), 2: (low * 10 + 2, high * 10 - 2),
                  3: (high * 10 + 2, high * 10 + 100)}[belt]
        return rng.randint(*tenths) / 10

    # The misleading argument sorts by volumetric weight, which lies in another belt's range.
    belt, wrong_belt = rng.sample((1, 2, 3), 2)
    filler_belt = ({1, 2, 3} - {belt, wrong_belt}).pop()
    weight, volumetric = weight_in(belt), weight_in(wrong_belt)
    ranges = {1: f"under {low} kg", 2: f"between {low} kg and {high} kg", 3: f"over {high} kg"}
    detail, changing, phrase = rng.choice(_PARCEL_TRIGGERS)
    depot = rng.choice(TOWNS)
    return build_item(
        family="parcel_sorting", seed=seed, rng=rng,
        title=f"{depot} depot sorting hall rules",
        rules=[
            ("The hall has four belts: belts 1, 2 and 3, and belt 4, where parcels are handled "
            "by hand."),
            (f"Parcels are sorted by actual weight: under {low} kg to belt 1; from {low} kg to "
            f"{high} kg to belt 2; over {high} kg to belt 3."),
        ],
        extra_rules=[
            "The belts stop for maintenance at 02:00 each night.",
            "Each parcel is scanned at the hall entrance.",
        ],
        neutral_pool=[
            "Parcels for the same postcode area are bagged together after sorting.",
            "Damaged labels are reprinted at the entrance desk.",
        ],
        changing=changing,
        case_lead=f"A parcel for {rng.choice([t for t in TOWNS if t != depot])} weighs {weight} kg.",
        case_rest=[
            detail,
            f"The parcel's volumetric weight, calculated from its size, is {volumetric} kg.",
            f"The parcel was posted on {rng.choice(WEEKDAYS)}.",
        ],
        question="Which belt does the parcel go to?",
        answers={
            "default": f"Belt {belt}",
            "changed": "Belt 4",
            "misleading": f"Belt {wrong_belt}",
            "filler": f"Belt {filler_belt}",
        },
        valid_reasoning=(
            f"The parcel {phrase}, and such parcels always go to belt 4, whatever their weight."
        ),
        misleading_reasoning=(
            f"The parcel's volumetric weight is {volumetric} kg, which is {ranges[wrong_belt]}, "
            f"so it goes to belt {wrong_belt}."
        ),
        params={"limits": [low, high], "weight": weight, "volumetric_weight": volumetric,
                "special_handling": True},
    )
