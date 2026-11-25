"""Unseen families 9-12: train timetable, grant budget sheet, greenhouse sensor log, parcel sorting.

These four appear only in the test-unseen set. Each `draw_*` function takes a
seeded random generator and returns one Item, or raises Reject when the drawn
numbers break a constraint (the caller redraws).

Order of drawing, in every family: first everything the rule argument mentions,
then, depending on whether the rule is to apply, the case detail that decides
it. The argument's text is therefore distributed alike for items where it is
sound and items where it is not; only the case tells them apart.
"""

from __future__ import annotations

import itertools
import random

from ..core import Item, Reject, build_item, clock, count, pick, rule_applies_for
from ..names import COMPANIES, TOWNS, WEEKDAYS, person


def draw_train_timetable(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    scheduled = rng.randrange(6 * 60, 21 * 60)
    delay = rng.randint(3, 8)
    actual = scheduled + delay
    # Four departures: one between scheduled and actual arrival (reachable only by someone
    # who ignores the delay: the misleading answer), one shortly after arrival (default),
    # one after the minimum changing time (changed), one later still (filler).
    missed = rng.randint(scheduled + 1, actual - 1)
    gap = rng.randint(4, 7)
    first = actual + gap
    min_change = rng.choice([m for m in (8, 10, 12) if m > gap])
    # Strictly more than the minimum changing time: a train leaving exactly at the limit
    # would leave it open whether it can be caught.
    wait = rng.randint(min_change + 1, min_change + 25)
    second = actual + wait
    third = second + rng.randint(20, 40)
    # All departures leave from platforms 5-8. An arrival on platforms 1-4 means a
    # change between the two groups, which the withheld rule is about; an arrival on
    # platforms 5-8 does not.
    arrival_platform = rng.randint(1, 4) if applies else rng.randint(5, 8)
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
            f"{name.split()[0]} carries one suitcase.",
        ],
        question=f"Which is the earliest train to {destination} that {name} can take?",
        answers={
            "default": f"The {clock(first)} train",
            "changed": f"The {clock(second)} train",
            "distractor": f"The {clock(missed)} train",
            "filler": f"The {clock(third)} train",
        },
        rule_applies=applies,
        rule_reasoning=(
            f"{name} has to change between platforms 1–4 and platforms 5–8, which takes at least "
            f"{min_change} minutes, but the {clock(first)} train leaves only {gap} minutes after "
            f"the arrival. The {clock(second)} train leaves {wait} minutes after the arrival, so "
            f"it is the earliest one {name} can take."
        ),
        distractor_reasoning=(
            f"The train from {origin} is due at {clock(scheduled)}, so {name} is at the station "
            f"before the {clock(missed)} train leaves and can take it."
        ),
        params={"arrival_scheduled": scheduled, "arrival_actual": actual,
                "departures": departures, "min_change": min_change,
                "arrival_platform": arrival_platform, "departure_platforms": platforms},
    )


_LABS = ("Optics", "Polymer", "Soil", "Acoustics", "Robotics", "Imaging", "Catalysis", "Hydrology")


def draw_grant_budget(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    threshold = rng.choice((40_000, 50_000, 60_000))
    pct = rng.choice((10, 20, 25))
    target = rng.randrange(3)
    # Staff numbers of the three labs and the amount per staff member. The grant lies
    # above or below the threshold as the item's kind requires, and every amount in
    # the options is a whole number.
    staff, unit = pick(rng, [
        (s, u) for s in itertools.permutations(range(2, 9), 3)
        for u in (2000, 3000, 4000, 5000, 6000)
        if ((sum(s) * u > threshold) if applies else (sum(s) * u < threshold))
        and sum(s) * u % 3 == 0 and s[target] * u * pct % 100 == 0
    ])
    budget = sum(staff) * unit
    share = staff[target] * unit
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
        changing=(f"If the grant is larger than {threshold:,}, {pct}% of it is set aside for "
                  "shared equipment before the split."),
        case_lead="The grant for the coming year is being divided.",
        case_rest=[
            f"The {labs[target]} lab moved to the second floor this year.",
            f"The {labs[other]} lab was founded {rng.randint(4, 30)} years ago.",
        ],
        question=f"How much does the {labs[target]} lab receive?",
        answers={
            "default": f"{share:,}",
            "changed": f"{reduced:,}",
            "distractor": f"{budget // 3:,}",
            "filler": f"{staff[other] * unit:,}",
        },
        rule_applies=applies,
        rule_reasoning=(
            f"The grant is larger than {threshold:,}, so {pct}% of it is set aside first, and the "
            f"{labs[target]} lab receives its share of what is left."
        ),
        distractor_reasoning=(
            f"The grant is split between three labs, so each lab receives {budget:,} ÷ 3 = "
            f"{budget // 3:,}."
        ),
        params={"budget": budget, "staff": list(staff), "target": target, "reserve_pct": pct,
                "reserve_threshold": threshold},
    )


def draw_sensor_log(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    n_days = rng.choice((6, 7))
    limit = rng.choice((28, 30, 32))
    offset = rng.choice((2, 3))
    sensors = ("S1", "S2", "S3")
    readings = [(rng.randint(limit - 4, limit + 5), rng.choice(sensors)) for _ in range(n_days)]
    heat = [i for i, (t, _) in enumerate(readings) if t > limit]
    exact = [i for i, (t, _) in enumerate(readings) if t == limit]

    def droppable(sensor: str) -> list[int]:
        """Days that would stop being heat days if this sensor's readings were corrected."""
        return [i for i in heat if readings[i][1] == sensor and readings[i][0] - offset <= limit]

    with_effect = [s for s in sensors if droppable(s)]
    without_effect = [s for s in sensors if not droppable(s)]
    # Both kinds of sensor are required in both kinds of item, so that the logs are
    # distributed alike.
    if not exact or not with_effect or not without_effect or len(heat) < 2:
        raise Reject("log lacks a borderline day, enough heat days, or a sensor of each kind")
    # The rule argument always names the days of a sensor whose correction would lower
    # the count. Where the rule applies, that is the sensor the withheld section calls
    # faulty. Where it does not, the withheld section names a sensor whose correction
    # changes nothing, and the argument attributes the other sensor's days to it.
    argued_sensor = rng.choice(with_effect)
    faulty = argued_sensor if applies else rng.choice(without_effect)
    dropped = droppable(argued_sensor)
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
            f"The greenhouse is planted with {rng.choice(('tomatoes', 'peppers', 'cucumbers', 'basil'))}.",
        ],
        question="How many heat days does the log show?",
        answers={
            "default": count(len(heat), "day"),
            "changed": count(len(heat) - len(dropped), "day"),
            "distractor": count(len(heat) + len(exact), "day"),
            "filler": count(rng.choice(fillers), "day"),
        },
        rule_applies=applies,
        rule_reasoning=(
            f"Sensor {faulty} reads {offset} °C too high. After the correction, {day_list} "
            f"{'is' if len(dropped) == 1 else 'are'} no longer above {limit} °C, so the log shows "
            f"{count(len(heat) - len(dropped), 'heat day')}."
        ),
        distractor_reasoning=(
            f"Every day that reaches {limit} °C is a heat day, so {exact_list} "
            f"{'counts' if len(exact) == 1 else 'count'} as well, which gives "
            f"{count(len(heat) + len(exact), 'heat day')}."
        ),
        params={"limit": limit, "readings": [list(r) for r in readings], "faulty": faulty,
                "offset": offset, "argued_days": [i + 1 for i in dropped]},
    )


# (case detail that meets the rule's condition, case detail that does not, withheld
# section, phrase for the rule argument)
_PARCEL_TRIGGERS = (
    ("The parcel is marked fragile.", "The parcel is not marked fragile.",
     "Parcels marked fragile always go to belt 4.", "is marked fragile"),
    ("The parcel contains liquids.", "The parcel contains no liquids.",
     "Parcels containing liquids always go to belt 4.", "contains liquids"),
)


def draw_parcel_sorting(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
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
    met, not_met, changing, phrase = rng.choice(_PARCEL_TRIGGERS)
    detail = met if applies else not_met
    depot = rng.choice(TOWNS)
    return build_item(
        family="parcel_sorting", seed=seed, rng=rng,
        title=f"{depot} depot sorting hall rules",
        rules=[
            "The hall has four belts, numbered 1 to 4.",
            # Gives belt 4 a visible purpose that does not apply to the case. Without it,
            # an unused fourth belt next to a "fragile" parcel gives the withheld rule away.
            "Parcels whose label cannot be read go to belt 4.",
            (f"Parcels are sorted by actual weight: under {low} kg to belt 1; from {low} kg to "
            f"{high} kg to belt 2; over {high} kg to belt 3."),
        ],
        extra_rules=[
            "The belts stop for maintenance at 02:00 each night.",
            "Each parcel is scanned at the hall entrance.",
        ],
        neutral_pool=[
            "Parcels for the same postcode area are bagged together after sorting.",
            "Sorting staff change shifts at 06:00 and 14:00.",
        ],
        changing=changing,
        case_lead=f"A parcel for {rng.choice([t for t in TOWNS if t != depot])} weighs {weight} kg.",
        case_rest=[
            detail,
            f"The parcel's volumetric weight, calculated from its size, is {volumetric} kg.",
            f"The parcel was posted on {rng.choice(WEEKDAYS)}.",
            "The parcel's label was read without problems.",
        ],
        question="Which belt does the parcel go to?",
        answers={
            "default": f"Belt {belt}",
            "changed": "Belt 4",
            "distractor": f"Belt {wrong_belt}",
            "filler": f"Belt {filler_belt}",
        },
        rule_applies=applies,
        rule_reasoning=(
            f"The parcel {phrase}, and such parcels always go to belt 4, whatever their weight."
        ),
        distractor_reasoning=(
            f"The parcel's volumetric weight is {volumetric} kg, which is {ranges[wrong_belt]}, "
            f"so it goes to belt {wrong_belt}."
        ),
        params={"limits": [low, high], "weight": weight, "volumetric_weight": volumetric,
                "special_handling": applies, "label_readable": True},
    )
