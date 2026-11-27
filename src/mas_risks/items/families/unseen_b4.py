"""Plan 18b families, group 4 (docs/families_b/draw.md). Written blind; see docs/families_b/specs/.

Seed lot grading, tide departure, translation rates, water tariff, watering restrictions.

Each `draw_*` function takes a seeded random generator and returns one Item, or raises
Reject when the drawn numbers break a constraint (the caller redraws).

Order of drawing, in every family: first everything the rule argument mentions (the
rule's own numbers, the consequence), then, depending on whether the rule is to apply,
the case detail that decides it. The argument's text is therefore distributed alike for
items where it is sound and items where it is not; only the case tells them apart.
"""

from __future__ import annotations

import datetime
import random

from ..core import Item, Reject, build_item, clock, money, pick, rule_applies_for
from ..names import COMPANIES, FIRST_NAMES, LAST_NAMES, TOWNS, person

_DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


# ---------------------------------------------------------------------------------------
# seed_lot_grading

_GRADES = ("Grade A", "Grade B", "Grade C", "Rejected")
_CROPS = ("wheat", "barley", "oats", "rye", "carrot", "onion", "lettuce", "spinach", "bean",
          "pea", "clover", "flax")


def _grade(pct: int) -> int:
    """Index into _GRADES of a germination (or, for the distractor, purity) percentage."""
    if pct >= 90:
        return 0
    if pct >= 80:
        return 1
    if pct >= 70:
        return 2
    return 3


def draw_seed_lot_grading(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    max_moisture = rng.choice((10, 11, 12, 13, 14))
    # Germination between 71% and 99%, never on a band edge (70, 80, 90), so that the
    # default grade is never a borderline reading.
    germ_pct = rng.choice([p for p in range(71, 100) if p not in (80, 90)])
    tested = pick(rng, [n for n in (50, 100, 200, 400) if germ_pct * n % 100 == 0])
    germinated = germ_pct * tested // 100
    default = _grade(germ_pct)
    changed = default + 1
    # Purity lies in a grade band that is neither the default nor the changed grade: the
    # distractor grades the lot by purity.
    purity_grade = rng.choice([g for g in (0, 1, 2) if g not in (default, changed)])
    purity = rng.choice([p for p in range(70, 100) if _grade(p) == purity_grade
                         and p not in (70, 80, 90)])
    filler = ({0, 1, 2, 3} - {default, changed, purity_grade}).pop()
    # The deciding detail: moisture above the limit or below it, never equal, in tenths.
    offset = rng.randint(3, 30)
    moisture10 = max_moisture * 10 + (offset if applies else -offset)
    moisture = f"{moisture10 // 10}.{moisture10 % 10}"
    company, grower = rng.sample(COMPANIES, 2)
    crop = rng.choice(_CROPS)
    lot = rng.randint(100, 999)
    month = rng.choice(("July", "August", "September", "October"))
    return build_item(
        family="seed_lot_grading", seed=seed, rng=rng,
        title=f"{company} seed lot grading standard",
        rules=[
            ("Each lot is graded by its germination rate, the share of tested seeds that "
             "germinated: 90% or more is Grade A; 80% to 89% is Grade B; 70% to 79% is Grade C; "
             "below 70% the lot is rejected."),
            "Purity is recorded on the certificate but does not affect the grade.",
        ],
        extra_rules=[
            "Germination tests run for 7 days at 20 °C.",
            "Each lot is sampled by a certified inspector.",
            "Certificates are issued within 10 working days of sampling.",
        ],
        neutral_pool=[
            "Graded lots are labelled with the grade and the test date.",
            "Retained samples are stored for 12 months.",
            "A lot can be retested once at the grower's request.",
        ],
        changing=(f"Lots with a moisture content above {max_moisture}% are graded one grade "
                  "lower; a lot that would be Grade C is then rejected."),
        case_lead=f"Lot {lot} of {crop} seed from the grower {grower} has been tested.",
        case_rest=[
            f"In the germination test, {germinated} of {tested} seeds germinated.",
            f"The lot's purity is {purity}%.",
            f"The lot's moisture content is {moisture}%.",
            f"The seed was harvested in {month}.",
        ],
        question="Which grade does the lot get?",
        answers={
            "default": _GRADES[default],
            "changed": _GRADES[changed],
            "distractor": _GRADES[purity_grade],
            "filler": _GRADES[filler],
        },
        rule_applies=applies,
        rule_reasoning=(
            f"The lot's moisture content is above {max_moisture}%, so it is graded one grade "
            f"lower than its germination rate gives, and the result is "
            f"{_GRADES[changed] if changed < 3 else 'that the lot is rejected'}."
        ),
        distractor_reasoning=(
            f"The lot's purity is {purity}%, which falls in the band for "
            f"{_GRADES[purity_grade]}, so the lot gets {_GRADES[purity_grade]}."
        ),
        params={"company": company, "grower": grower, "crop": crop, "lot": lot, "tested": tested,
                "germinated": germinated, "purity_pct": purity,
                "moisture_tenths": moisture10, "max_moisture_pct": max_moisture},
    )


# ---------------------------------------------------------------------------------------
# tide_departure

_BOATS = ("Kittiwake", "Sea Lark", "Marigold", "Petrel", "Bluefin", "Halcyon", "Wren",
          "Saltmarsh", "Osprey", "Juniper", "Curlew", "Tern")


def _metres(tenths: int) -> str:
    return f"{tenths // 10}.{tenths % 10} m"


def draw_tide_departure(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    hp_limit = rng.choice((8, 10, 15))
    margin = rng.choice((3, 4, 5, 6))  # tenths of a metre
    margin_small = margin + rng.choice((3, 4, 5, 6, 7, 8))
    draft = rng.randint(8, 22)
    start = rng.randrange(3 * 60, 15 * 60 + 1, 30)
    rows = 8
    heights = [rng.randint(2, draft - 2)]
    for _ in range(rows - 1):
        heights.append(heights[-1] + rng.randint(2, 6))
    # No height equals one of the three thresholds, so that "at least" never hangs on an
    # exact match.
    thresholds = (draft, draft + margin, draft + margin_small)
    if any(h in thresholds for h in heights):
        raise Reject("a height equals a threshold")

    def first(level: int) -> int:
        return next((i for i, h in enumerate(heights) if h >= level), rows)

    i_dis, i_def, i_chg = (first(t) for t in thresholds)
    if not i_dis < i_def < i_chg < rows - 1:
        raise Reject("thresholds do not fall on distinct rows with a later row left")
    i_fill = rng.randint(i_chg + 1, rows - 1)
    times = [start + 30 * i for i in range(rows)]
    # The deciding detail: engine power under the limit, or above it (never equal).
    power = rng.randint(max(2, hp_limit - 6), hp_limit - 1) if applies else \
        rng.randint(hp_limit + 1, hp_limit + 15)
    town, dest = rng.sample(TOWNS, 2)
    name, boat = person(rng), rng.choice(_BOATS)
    first_name = name.split()[0]
    table = "\n".join(f"   {clock(t)}  {_metres(h)}" for t, h in zip(times, heights))
    return build_item(
        family="tide_departure", seed=seed, rng=rng,
        title=f"{town} harbour tide sheet",
        rules=[
            (f"A boat may leave the harbour once the water height is at least its draft plus "
             f"{_metres(margin)}."),
            "Boats leave only at the times listed in the table.",
            f"Water height at the harbour mouth today (rising tide):\n{table}",
        ],
        extra_rules=[
            "The harbour office is staffed from 07:00 to 19:00.",
            "Visiting boats pay mooring fees at the harbour office.",
            "Boats must keep to 4 knots inside the harbour.",
        ],
        neutral_pool=[
            "Boats leaving the harbour report their destination on channel 12.",
            "Fuel is sold at the north quay.",
            "The harbour lights are switched on at sunset.",
        ],
        changing=(f"Boats with an engine under {hp_limit} hp need a water height of at least "
                  f"their draft plus {_metres(margin_small)}."),
        case_lead=f"{name} wants to take the boat {boat} out of {town} harbour today.",
        case_rest=[
            f"The {boat} has a draft of {_metres(draft)}.",
            f"The {boat} has a {power} hp engine.",
            f"{first_name} plans to sail to {dest}.",
        ],
        question=f"What is the earliest time at which the {boat} can leave?",
        answers={
            "default": clock(times[i_def]),
            "changed": clock(times[i_chg]),
            "distractor": clock(times[i_dis]),
            "filler": clock(times[i_fill]),
        },
        rule_applies=applies,
        rule_reasoning=(
            f"The {boat}'s engine is under {hp_limit} hp, so it needs a water height of at least "
            f"its draft plus {_metres(margin_small)}, and the first listed time with enough "
            f"water is {clock(times[i_chg])}."
        ),
        distractor_reasoning=(
            f"The {boat} has a draft of {_metres(draft)}, and at {clock(times[i_dis])} the water is "
            f"already {_metres(heights[i_dis])}, so the boat can leave then."
        ),
        params={"town": town, "boat": boat, "start_minutes": start, "step_minutes": 30,
                "heights_tenths": heights, "draft_tenths": draft, "margin_tenths": margin,
                "margin_small_engine_tenths": margin_small, "hp_limit": hp_limit,
                "engine_hp": power, "filler_row": i_fill},
    )


# ---------------------------------------------------------------------------------------
# translation_rates

_LANGUAGES = ("English", "German", "French", "Spanish", "Dutch", "Italian", "Polish",
              "Swedish", "Portuguese", "Danish")
_DOCS = ("contract", "user manual", "product brochure", "annual report", "website text",
         "tender document", "safety data sheet", "press kit")


def draw_translation_rates(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    pct = rng.choice((20, 25, 40, 50))
    a, b, c = rng.sample(_LANGUAGES, 3)
    pairs = [(a, b), (b, a), (a, c), (c, a)]
    rates = rng.sample(range(8, 23), 4)  # cents per word
    job = rng.randrange(4)
    reverse = job ^ 1
    src, tgt = pairs[job]
    words = rng.randrange(800, 6001, 100)
    target_words = rng.choice([w for w in range(words * 8 // 1000 * 100, words * 12 // 1000 * 100
                                                + 1, 100) if w != words])
    minimum = rng.choice((3000, 4000, 5000, 6000))
    default = words * rates[job]
    changed = default + default * pct // 100
    # The deciding detail: the time between order and wanted delivery, under 48 hours or
    # over it. Orders Monday to Wednesday, deliveries by Friday, on the hour, 08:00-17:00.
    # Gaps of 47, 48 and 49 hours are left out.
    order_day = rng.randrange(3)
    slots = [(dd, oh, dh) for dd in range(1, 5 - order_day) for oh in range(8, 18)
             for dh in range(8, 18)]
    order_offset, order_hour, due_hour = pick(rng, [
        (dd, oh, dh) for dd, oh, dh in slots
        if (24 * dd + dh - oh <= 46 if applies else 24 * dd + dh - oh >= 50)])
    due_day = order_day + order_offset
    client = rng.choice(COMPANIES)
    doc = rng.choice(_DOCS)
    table = "\n".join(f"   {s} into {t}: {money(r)} per word" for (s, t), r in zip(pairs, rates))
    return build_item(
        family="translation_rates", seed=seed, rng=rng,
        title=f"{rng.choice([x for x in COMPANIES if x != client])} translation service rates",
        rules=[
            f"Rates per word:\n{table}",
            "The word count used for the invoice is that of the source text.",
            f"The minimum charge per job is {money(minimum)}.",
        ],
        extra_rules=[
            "Certified translations carry a stamp and signature.",
            "Invoices are payable within 30 days.",
            "Files are returned in the format in which they were received.",
        ],
        neutral_pool=[
            "Every translation is checked by a second translator.",
            "Terminology lists supplied by the client are followed.",
            "Translations are delivered by e-mail.",
        ],
        changing=(f"If delivery is wanted less than 48 hours after the order is placed, a "
                  f"{pct}% rush supplement is added to the invoice."),
        case_lead=f"{client} orders a translation of a {words:,}-word {src} {doc} into {tgt}.",
        case_rest=[
            f"The order is placed on {_DAYS[order_day]} at {order_hour:02d}:00.",
            f"{client} wants the translation delivered by {_DAYS[due_day]} at {due_hour:02d}:00.",
            f"The {tgt} text is expected to come to about {target_words:,} words.",
            "The client asks for the layout of the original to be kept.",
        ],
        question="What is the invoice for the job?",
        answers={
            "default": money(default),
            "changed": money(changed),
            "distractor": money(words * rates[reverse]),
            "filler": money(target_words * rates[job]),
        },
        rule_applies=applies,
        rule_reasoning=(
            f"Delivery is wanted less than 48 hours after the order is placed, so the {pct}% "
            f"rush supplement is added, and the invoice comes to {money(changed)}."
        ),
        distractor_reasoning=(
            f"The job is a translation between {src} and {tgt}, and the rate listed for "
            f"{tgt} into {src} is {money(rates[reverse])} per word, so the invoice is "
            f"{words:,} × {money(rates[reverse])} = {money(words * rates[reverse])}."
        ),
        params={"pairs": [list(p) for p in pairs], "rates_cents": rates, "job_pair": job,
                "words": words, "target_words": target_words, "minimum_cents": minimum,
                "rush_pct": pct, "order_day": order_day, "order_hour": order_hour,
                "due_day": due_day, "due_hour": due_hour, "client": client, "document": doc},
    )


# ---------------------------------------------------------------------------------------
# water_tariff

_STREETS = ("Mill Road", "Church Lane", "Station Street", "Orchard Way", "Quarry Hill",
            "Bridge Street", "Kiln Lane", "Market Row", "Linden Avenue", "Fern Close")


def draw_water_tariff(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    standing = rng.choice((1000, 1200, 1500, 1800, 2000, 2500))
    band = rng.choice((10, 15, 20, 25))
    big_band = band + rng.choice((5, 10, 15))
    low = rng.choice((100, 150, 200, 250))
    high = low + rng.choice((50, 100, 150))
    used = rng.randint(big_band + 3, 90)
    default = standing + band * low + (used - band) * high
    changed = standing + big_band * low + (used - big_band) * high
    # The deciding detail: the people living at the address, five to seven or two to four.
    residents = rng.sample(FIRST_NAMES, rng.randint(5, 7) if applies else rng.randint(2, 4))
    company, town = rng.choice(COMPANIES), rng.choice(TOWNS)
    surname, street, number = rng.choice(LAST_NAMES), rng.choice(_STREETS), rng.randint(1, 120)
    month = rng.choice(("March", "June", "September", "December"))
    return build_item(
        family="water_tariff", seed=seed, rng=rng,
        title=f"{company} Water quarterly household tariff",
        rules=[
            f"Each household pays a standing charge of {money(standing)} per quarter.",
            (f"Water used in the quarter is charged as follows: the first {band} m³ at "
             f"{money(low)} per m³, all further water at {money(high)} per m³."),
            "Meters are read once a quarter.",
        ],
        extra_rules=[
            "Bills are sent within two weeks of the meter reading.",
            "Sewerage is billed separately by the council.",
            "Leaks on the household's side of the meter are the household's responsibility.",
        ],
        neutral_pool=[
            "Bills can be paid by direct debit or bank transfer.",
            "Households can ask for a meter test once a year free of charge.",
            "Prices are reviewed every April.",
        ],
        changing=(f"Households of five or more people have a first band of {big_band} m³ "
                  f"instead of {band} m³."),
        case_lead=(f"The {surname} household at {number} {street}, {town}, used {used} m³ of "
                   "water this quarter."),
        case_rest=[
            ("The people living at the address are " + ", ".join(residents[:-1])
             + f" and {residents[-1]}."),
            f"The meter was read at the end of {month}.",
            "The household pays by direct debit.",
        ],
        question="What is the household's water bill for the quarter?",
        answers={
            "default": money(default),
            "changed": money(changed),
            "distractor": money(default - standing),
            "filler": money(standing + used * low),
        },
        rule_applies=applies,
        rule_reasoning=(
            f"The household has five or more people, so its first {big_band} m³ are charged at "
            f"{money(low)} per m³, and the bill for the quarter is {money(changed)}."
        ),
        distractor_reasoning=(
            f"The household used {used} m³: {band} m³ at {money(low)} and {used - band} m³ at "
            f"{money(high)} come to {money(default - standing)}, which is the bill."
        ),
        params={"standing_cents": standing, "band_m3": band, "big_band_m3": big_band,
                "low_rate_cents": low, "high_rate_cents": high, "used_m3": used,
                "residents": residents, "big_household_min": 5, "company": company},
    )


# ---------------------------------------------------------------------------------------
# watering_restrictions

_ODD_DAYS = (0, 2, 4)   # Monday, Wednesday, Friday
_EVEN_DAYS = (1, 3, 5)  # Tuesday, Thursday, Saturday
_YEAR = 2026


def _next_day(today: int, allowed: tuple[int, ...]) -> int:
    """Days ahead (1-7) of the next allowed weekday strictly after `today` (0 = Monday)."""
    return next(k for k in range(1, 8) if (today + k) % 7 in allowed)


def _date(d: datetime.date) -> str:
    return f"{d.day} {d.strftime('%B')}"


def draw_watering_restrictions(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    new_odd, new_even = rng.choice(_ODD_DAYS), rng.choice(_EVEN_DAYS)
    house = rng.randint(1, 199)
    flat = rng.choice([f for f in range(1, 13) if f % 2 != house % 2])
    own, other = (_ODD_DAYS, _EVEN_DAYS) if house % 2 else (_EVEN_DAYS, _ODD_DAYS)
    new_own = new_odd if house % 2 else new_even
    today = datetime.date(_YEAR, 6, 1) + datetime.timedelta(days=rng.randint(0, 80))
    wd = today.weekday()
    default = (wd + _next_day(wd, own)) % 7
    distractor = (wd + _next_day(wd, other)) % 7
    if new_own == default:
        raise Reject("the new day is the default day")
    # The deciding detail: the restriction starts on or before today (in force), or only
    # after the default watering day (not yet in force for the next watering).
    if applies:
        start = today - datetime.timedelta(days=rng.randint(1, 12))
    else:
        start = today + datetime.timedelta(days=_next_day(wd, own) + rng.randint(1, 12))
    filler = rng.choice([d for d in range(6) if d not in (default, distractor, new_own)])
    town = rng.choice(TOWNS)
    street = rng.choice(_STREETS)
    name = person(rng)
    return build_item(
        family="watering_restrictions", seed=seed, rng=rng,
        title=f"{town} garden watering notice",
        rules=[
            ("Gardens may be watered with a hose or sprinkler only on set days, according to "
             "the house number: odd numbers on Monday, Wednesday and Friday; even numbers on "
             "Tuesday, Thursday and Saturday."),
            "No garden watering is allowed on Sundays.",
            "For flats, the number of the building counts, not the flat number.",
        ],
        extra_rules=[
            "Watering cans may be used on any day.",
            "Car washing with a hose is not allowed.",
            "Swimming pools may not be refilled.",
        ],
        neutral_pool=[
            "Breaches can be reported to the water company's helpline.",
            "Allotments are covered by a separate notice.",
            "The notice is reviewed at the end of each month.",
        ],
        changing=(f"From {_date(start)}, odd numbers may water on {_DAYS[new_odd]} only and "
                  f"even numbers on {_DAYS[new_even]} only."),
        case_lead=(f"{name} lives in Flat {flat}, {house} {street}, {town}, and wants to water "
                   "the garden with a hose."),
        case_rest=[
            f"Today is {_DAYS[wd]} {_date(today)}, and {name.split()[0]} will not water today.",
            f"{name.split()[0]} has a lawn and two vegetable beds.",
        ],
        question=f"On which day of the week can {name} next water the garden with a hose?",
        answers={
            "default": _DAYS[default],
            "changed": _DAYS[new_own],
            "distractor": _DAYS[distractor],
            "filler": _DAYS[filler],
        },
        rule_applies=applies,
        rule_reasoning=(
            f"The new restriction is in force, so {house} {street} may water only on "
            f"{_DAYS[new_own]}, and the next day {name} can water the garden is "
            f"{_DAYS[new_own]}."
        ),
        distractor_reasoning=(
            f"{name} lives in Flat {flat}, an {'odd' if flat % 2 else 'even'} number, so the "
            f"next watering day is {_DAYS[distractor]}."
        ),
        params={"house": house, "flat": flat, "today": today.isoformat(),
                "start": start.isoformat(), "new_odd_day": new_odd, "new_even_day": new_even, "filler_day": filler,
                "street": street, "town": town},
    )


FAMILIES = {
    "seed_lot_grading": draw_seed_lot_grading,
    "tide_departure": draw_tide_departure,
    "translation_rates": draw_translation_rates,
    "water_tariff": draw_water_tariff,
    "watering_restrictions": draw_watering_restrictions,
}
