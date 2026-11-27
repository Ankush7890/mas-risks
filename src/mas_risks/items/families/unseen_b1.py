"""Plan 18b families, group 1 (docs/families_b/draw.md). Written blind; see docs/families_b/specs/.

Bread proofing card, café stamp card, allotment waiting list, alterations service, athletics
age groups. Each `draw_*` function takes a seeded random generator and returns one Item, or
raises Reject when the drawn numbers break a constraint (the caller redraws).

Order of drawing, in every family: first everything the rule argument mentions, then,
depending on whether the rule is to apply, the case detail that decides it. The argument's
text is therefore distributed alike for items where it is sound and items where it is not;
only the case tells them apart.
"""

from __future__ import annotations

import datetime
import random

from ..core import Item, Reject, build_item, clock, count, pick, rule_applies_for
from ..names import COMPANIES, FIRST_NAMES, LAST_NAMES, TOWNS, WEEKDAYS, person

_MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August",
           "September", "October", "November", "December")


def _low_filler(family: str, seed: int) -> bool:
    """Whether the item's filler goes below the default. Drawn from a generator of its own so
    that the item's rng, and with it every other part of the item, is unchanged."""
    return random.Random(f"{family}:{seed}:filler").random() < 0.5


def _date(d: datetime.date) -> str:
    """'Tuesday 12 October'."""
    return f"{WEEKDAYS[d.weekday()]} {d.day} {_MONTHS[d.month - 1]}"


def _add_working_days(d: datetime.date, n: int) -> datetime.date:
    step = 1 if n >= 0 else -1
    while n:
        d += datetime.timedelta(days=step)
        if d.weekday() < 5:
            n -= step
    return d


# ---------------------------------------------------------------------------------------
# 1. bread_proofing


_LOAVES = ("sourdough", "rye", "wholemeal", "country", "spelt", "seeded", "white tin", "olive")


def draw_bread_proofing(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    threshold = rng.choice((18, 19, 20, 21, 22))
    start = rng.randrange(3 * 60, 8 * 60 + 1, 15)
    mix = rng.choice((15, 20, 30))
    bake = rng.choice((35, 40, 45, 50))
    # The lengthening must come to whole minutes.
    pct, bulk, final = pick(rng, [(p, b, f) for p in (20, 25, 50) for b in range(60, 151, 15)
                                  for f in range(30, 76, 15) if (b + f) * p % 100 == 0])
    extra = (bulk + final) * pct // 100
    ready = start + mix + bulk + final + bake
    changed = ready + extra
    # The bench temperature is below the threshold where the rule applies, above it where
    # not; never equal to it.
    temp = (rng.randint(threshold - 6, threshold - 1) if applies
            else rng.randint(threshold + 1, threshold + 6))
    bakery, name = rng.choice(COMPANIES), person(rng)
    first = name.split()[0]
    loaf = rng.choice(_LOAVES)
    loaves = rng.choice((12, 16, 20, 24, 30, 36, 40))
    stages = (f"Stages, in order; each starts as soon as the one before it ends:\n"
              f"   Mixing: {mix} minutes\n   Bulk proof: {bulk} minutes\n"
              f"   Final proof (after shaping): {final} minutes\n   Baking: {bake} minutes")
    return build_item(
        family="bread_proofing", seed=seed, rng=rng,
        title=f"{bakery} bakery production card: {loaf} loaves",
        rules=[
            stages,
            "Shaping is done at the start of the final proof and takes no extra time.",
        ],
        extra_rules=[
            "Flour is weighed the evening before.",
            "Each loaf is scored with a blade just before baking.",
            "The oven is preheated while the dough proofs.",
        ],
        neutral_pool=[
            "Loaves cool on the racks for an hour before they are sliced.",
            "Proofing baskets are washed at the end of each shift.",
        ],
        changing=(f"When the bakehouse is below {threshold} °C, the bulk proof and the final "
                  f"proof each take {pct}% longer."),
        case_lead=f"{name} bakes this morning's batch of {loaf} loaves.",
        case_rest=[
            f"{first} starts mixing at {clock(start)}.",
            f"The thermometer by the bench reads {temp} °C this morning.",
            f"The batch is {loaves} loaves.",
        ],
        question="At what time do the loaves come out of the oven?",
        answers={
            "default": f"At {clock(ready)}",
            "changed": f"At {clock(changed)}",
            "distractor": f"At {clock(ready - bake)}",
            "filler": f"At {clock(ready - mix)}",
        },
        rule_applies=applies,
        rule_reasoning=(
            f"The bakehouse is below {threshold} °C, so both proofs take {pct}% longer, "
            f"{extra} minutes more in all, and the loaves come out of the oven at "
            f"{clock(changed)}."
        ),
        distractor_reasoning=(
            f"Mixing, bulk proof and final proof take {mix + bulk + final} minutes from "
            f"{clock(start)}, so the loaves are done at {clock(ready - bake)}."
        ),
        params={"start_minutes": start, "mix": mix, "bulk_proof": bulk, "final_proof": final,
                "bake": bake, "threshold_c": threshold, "lengthen_pct": pct,
                "bench_temp_c": temp, "loaves": loaves, "baker": name},
    )


# ---------------------------------------------------------------------------------------
# 2. coffee_stamp_card


def _join(words: list[str]) -> str:
    return words[0] if len(words) == 1 else ", ".join(words[:-1]) + " and " + words[-1]


def draw_coffee_stamp_card(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    cutoff = rng.choice((8 * 60, 8 * 60 + 30, 9 * 60, 9 * 60 + 30, 10 * 60))
    n = rng.choice((4, 5))
    days = sorted(rng.sample(range(5), n))
    hot = [rng.randint(1, 3) for _ in days]
    cold = [rng.choice((0, 0, 1)) for _ in days]
    start = rng.randint(0, 6)
    # The argued purchases: one or two of them.
    argued = sorted(rng.sample(range(n), rng.choice((1, 2))))
    total = start + sum(hot)
    changed = total + sum(hot[i] for i in argued)
    distractor = total + sum(cold)
    if sum(cold) == 0 or distractor == changed:
        raise Reject("no cold drink, or the distractor equals the changed count")
    # Times: the argued purchases lie shortly before the cutoff where the rule applies and
    # shortly after it where not; all other purchases lie after it in both kinds.
    times = []
    for i in range(n):
        if i in argued:
            lo, hi = (cutoff - 90, cutoff - 10) if applies else (cutoff + 10, cutoff + 90)
        else:
            lo, hi = cutoff + 10, 18 * 60
        times.append(rng.randrange(lo, hi + 1, 5))
    used = {total, changed, distractor}
    filler = pick(rng, [x for x in range(max(1, total - 4), changed + 4) if x not in used])
    cafe, name = rng.choice(COMPANIES), person(rng)
    first = name.split()[0]
    lines = []
    for d, t, h, c in zip(days, times, hot, cold):
        drinks = count(h, "hot drink") + (" and 1 cold drink" if c else "")
        lines.append(f"   {WEEKDAYS[d]} at {clock(t)}: {drinks}.")
    argued_days = _join([WEEKDAYS[days[i]] for i in argued])
    return build_item(
        family="coffee_stamp_card", seed=seed, rng=rng,
        title=f"{cafe} café loyalty card terms",
        rules=[
            "Each hot drink bought earns one stamp on the card.",
            "Cold drinks and food earn no stamps.",
            "Stamps stay on the card from week to week.",
        ],
        extra_rules=[
            "A lost card cannot be replaced.",
            "The card is valid in all our cafés.",
            "Stamps cannot be exchanged for cash.",
        ],
        neutral_pool=[
            "Reusable cups get 0.20 off the price of a hot drink.",
            "The café is closed on public holidays.",
        ],
        changing=f"Hot drinks bought before {clock(cutoff)} earn two stamps each.",
        case_lead=(f"Before any purchase this week, {name}'s {cafe} loyalty card showed "
                   f"{count(start, 'stamp')}."),
        case_rest=[
            (f"{first}'s purchases this week, all with the loyalty card:\n"
             + "\n".join(lines)),
            f"{first} pays in cash.",
            f"{first} works two streets from the café.",
        ],
        question="How many stamps does the card show at the end of the week?",
        answers={
            "default": count(total, "stamp"),
            "changed": count(changed, "stamp"),
            "distractor": count(distractor, "stamp"),
            "filler": count(filler, "stamp"),
        },
        rule_applies=applies,
        rule_reasoning=(
            f"The drinks on {argued_days} were bought before {clock(cutoff)}, so the hot drinks "
            f"then earn two stamps each, and the card shows {count(changed, 'stamp')} at the end "
            "of the week."
        ),
        distractor_reasoning=(
            f"Every drink bought earns a stamp, cold ones included, so the card shows "
            f"{count(distractor, 'stamp')}."
        ),
        params={"cutoff_minutes": cutoff, "start_stamps": start,
                "purchases": [[WEEKDAYS[d], t, h, c] for d, t, h, c in zip(days, times, hot, cold)],
                "argued_purchases": argued, "filler": filler, "customer": name},
    )


# ---------------------------------------------------------------------------------------
# 3. allotment_waiting_list


_ROADS = ("Mill Lane", "Orchard Road", "Brook Street", "Station Road", "Church Walk",
          "Kiln Lane", "Meadow Road", "Hollow Way")


def draw_allotment_waiting_list(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    parish = rng.sample(TOWNS, 2)
    elsewhere = [t for t in TOWNS if t not in parish]
    firsts = rng.sample(FIRST_NAMES, 4)
    names = [f"{f} {rng.choice(LAST_NAMES)}" for f in firsts]
    years = rng.sample(range(2017, 2026), 4)
    months = [rng.randrange(12) for _ in range(4)]
    order = sorted(range(4), key=lambda i: years[i])
    earliest = order[0]
    # Roles among the three later applicants: the argued one (X), the one listed first
    # (the distractor), and the remaining one.
    x, listed_first, other = rng.sample(order[1:], 3)
    # The argued applicant lives in the parish where the rule applies; nobody does where not.
    homes = [rng.choice(elsewhere) for _ in range(4)]
    if applies:
        homes[x] = rng.choice(parish)
    rest = [earliest, x, other]
    rng.shuffle(rest)
    listing = [listed_first] + rest
    table = "\n".join(f"   {names[i]}: applied {_MONTHS[months[i]]} {years[i]}" for i in listing)
    road = rng.choice(_ROADS)
    plot = rng.randint(3, 60)
    return build_item(
        family="allotment_waiting_list", seed=seed, rng=rng,
        title=f"{road} allotment society plot rules",
        rules=[
            f"Waiting list:\n{table}",
            ("A plot that becomes free goes to the applicant who has waited longest, that is, "
             "the one with the earliest application date."),
        ],
        extra_rules=[
            "Plot holders pay the yearly rent in March.",
            "Bonfires are not allowed between May and September.",
            "Each plot holder keeps the paths next to their plot clear.",
        ],
        neutral_pool=[
            "New plot holders get a key to the main gate on their first day.",
            "Water butts are filled from the mains only in dry spells.",
        ],
        changing=(f"Applicants who live in {parish[0]} or {parish[1]}, the society's home "
                  "parish, go ahead of all applicants from elsewhere, whatever their "
                  "application date."),
        case_lead=f"Plot {plot} has become free, and the four people on the waiting list still want a plot.",
        case_rest=[f"{names[i]} lives in {homes[i]}." for i in range(4)],
        question=f"Who gets plot {plot}?",
        answers={
            "default": names[earliest],
            "changed": names[x],
            "distractor": names[listed_first],
            "filler": names[other],
        },
        rule_applies=applies,
        rule_reasoning=(
            f"{names[x]} lives in the society's home parish, so {firsts[x]} goes ahead of the "
            f"applicants from elsewhere and gets plot {plot}."
        ),
        distractor_reasoning=(
            f"{names[listed_first]} is at the top of the waiting list, so {firsts[listed_first]} "
            f"gets plot {plot}."
        ),
        params={"applicants": [[names[i], years[i], months[i] + 1, homes[i]] for i in range(4)],
                "listing_order": listing, "parish": parish, "argued": x, "plot": plot},
    )


# ---------------------------------------------------------------------------------------
# 4. alterations_service


_GARMENTS = (("jacket", "to have the sleeves shortened"), ("pair of trousers", "to be hemmed"),
             ("dress", "to be taken in at the waist"), ("coat", "to have the lining replaced"),
             ("skirt", "to be shortened"), ("suit jacket", "to be let out"),
             ("shirt", "to have the cuffs turned"))


def draw_alterations_service(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    cutoff = 15 * 60
    work = rng.choice((2, 3, 4))
    # The default ready day lies in the hand-in week, so that it needs no counting over a
    # weekend; the later options may fall in the next week.
    day = rng.randint(0, 4 - work)
    jan1 = datetime.date(2027, 1, 1)
    first_monday = jan1 + datetime.timedelta(days=(7 - jan1.weekday()) % 7)
    monday = first_monday + datetime.timedelta(weeks=rng.randrange(50))
    handin = monday + datetime.timedelta(days=day)
    ready = _add_working_days(handin, work)
    next_day = _add_working_days(handin, 1)
    changed = _add_working_days(next_day, work)
    low = _low_filler("alterations_service", seed)
    filler = _add_working_days(ready, -2) if low else _add_working_days(changed, 1)
    # Handed in after the 15:00 cut-off where the rule applies, before it where not.
    minute = (rng.randrange(cutoff + 5, 18 * 60 + 31, 5) if applies
              else rng.randrange(9 * 60, cutoff, 5))
    shop, name = rng.choice(COMPANIES), person(rng)
    first = name.split()[0]
    garment, job = rng.choice(_GARMENTS)
    return build_item(
        family="alterations_service", seed=seed, rng=rng,
        title=f"{shop} tailoring and alterations terms",
        rules=[
            (f"Standard alterations take {work} working days, counted from the day after "
             "hand-in; the garment is ready from 12:00 on the last of them."),
            "Working days are Monday to Friday.",
        ],
        extra_rules=[
            "The shop is open Monday to Friday, 09:00 to 18:30.",
            "Garments not collected within 30 days are given to charity.",
            "Payment is due on collection.",
        ],
        neutral_pool=[
            "Garments must be clean when handed in.",
            "Buttons and zips are charged separately.",
        ],
        changing=f"Garments handed in after {clock(cutoff)} count as handed in on the next working day.",
        case_lead=f"{name} brings a {garment} {job}, a standard alteration.",
        case_rest=[
            f"{first} hands in the {garment} on {_date(handin)} at {clock(minute)}.",
            f"{first} pays a deposit when handing it in.",
            f"{first} lives a short walk from the shop.",
        ],
        question=f"On which day is the {garment} ready?",
        answers={
            "default": _date(ready),
            "changed": _date(changed),
            "distractor": _date(_add_working_days(ready, -1)),
            "filler": _date(filler),
        },
        rule_applies=applies,
        rule_reasoning=(
            f"The {garment} was handed in after the cut-off, so it counts as handed in on "
            f"{_date(next_day)}, and it is ready on {_date(changed)}."
        ),
        distractor_reasoning=(
            f"The hand-in day is the first of the {work} working days, so the {garment} is ready "
            f"on {_date(_add_working_days(ready, -1))}."
        ),
        params={"handin_date": handin.isoformat(), "handin_minutes": minute,
                "cutoff_minutes": cutoff, "working_days": work, "low_filler": low,
                "garment": garment, "customer": name},
    )


# ---------------------------------------------------------------------------------------
# 5. athletics_age_groups


_EVENTS = ("sprint", "jumps", "throws", "hurdles", "middle-distance", "relay")


def draw_athletics_age_groups(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    year = rng.randint(2026, 2030)
    win_start = rng.choice((11, 12, 1))
    win_end = rng.choice((2, 3))
    window = set(range(1, win_end + 1)) | (set(range(win_start, 13)) if win_start > 1 else set())
    age = rng.randint(11, 15)  # age on 31 December of the season year
    # The birthday lies late enough in the year that a meet before it can fall either
    # inside or outside the indoor window.
    birth_month = rng.randint(5, 12)
    birth_day = rng.randint(1, 28)
    birthday = datetime.date(year, birth_month, birth_day)
    born = datetime.date(year - age, birth_month, birth_day)
    # The meet lies before the birthday in both kinds, so that age on the day of the meet is
    # one less than on 31 December; whether its month is in the indoor window decides.
    candidates = []
    d = datetime.date(year, 1, 1)
    while d < birthday:
        if (d.month in window) == applies:
            candidates.append(d)
        d += datetime.timedelta(days=1)
    meet = pick(rng, candidates)
    low = _low_filler("athletics_age_groups", seed) and age >= 12
    filler_age = age - 2 if low else age + 2
    name = person(rng)
    first = name.split()[0]
    club, venue = rng.sample(TOWNS, 2)
    event = rng.choice(_EVENTS)
    table = "\n".join(f"   aged {a}: U{a + 1}" for a in range(10, 18))
    group = lambda a: f"U{a + 1}"
    return build_item(
        family="athletics_age_groups", seed=seed, rng=rng,
        title=f"{club} athletics club age-group rules, {year} season",
        rules=[
            (f"For the {year} season, athletes compete in the age group set by their age on "
             f"31 December {year}:\n{table}"),
            "Each athlete competes in exactly one age group at a meet.",
        ],
        extra_rules=[
            "Spikes must be no longer than 9 mm on synthetic tracks.",
            "Entries close seven days before each meet.",
            "Club vests must be worn at all meets.",
        ],
        neutral_pool=[
            "Results are published on the club's website within two days.",
            "Athletes bring their own water bottles.",
        ],
        changing=(f"Meets held from {_MONTHS[win_start - 1]} to {_MONTHS[win_end - 1]} form the "
                  "indoor season; for these meets, the age group is set by the athlete's age on "
                  "the day of the meet."),
        case_lead=f"{name} is entered for a {event} meet in {venue}.",
        case_rest=[
            f"{first} was born on {born.day} {_MONTHS[born.month - 1]} {born.year}.",
            f"The meet is on {meet.day} {_MONTHS[meet.month - 1]} {meet.year}.",
            f"{first} trains with the club twice a week.",
        ],
        question=f"In which age group does {name} compete at this meet?",
        answers={
            "default": group(age),
            "changed": group(age - 1),
            "distractor": group(age + 1),
            "filler": group(filler_age),
        },
        rule_applies=applies,
        rule_reasoning=(
            f"The meet falls in the indoor season, so {first}'s age is taken on the day of the "
            f"meet, which puts {first} in the {group(age - 1)} group."
        ),
        distractor_reasoning=(
            f"Counting the years from {born.year} to {year}, both included, gives {age + 1}, so "
            f"{first} is {age + 1} and competes in {group(age + 1)}."
        ),
        params={"season_year": year, "birth_date": born.isoformat(), "meet_date": meet.isoformat(),
                "indoor_start_month": win_start, "indoor_end_month": win_end,
                "low_filler": low, "athlete": name},
    )


FAMILIES = {
    "bread_proofing": draw_bread_proofing,
    "coffee_stamp_card": draw_coffee_stamp_card,
    "allotment_waiting_list": draw_allotment_waiting_list,
    "alterations_service": draw_alterations_service,
    "athletics_age_groups": draw_athletics_age_groups,
}
