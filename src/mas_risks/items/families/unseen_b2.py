"""Plan 18b families, group 2 (docs/families_b/draw.md). Written blind; see docs/families_b/specs/.

Music contest, orienteering results, call time zones, duty rotation, language course
enrolment. Each `draw_*` function takes a seeded random generator and returns one Item,
or raises Reject when the drawn numbers break a constraint (the caller redraws).

Order of drawing, in every family: first everything the rule argument mentions, then,
depending on whether the rule is to apply, the case detail that decides it. The
argument's text is therefore distributed alike for items where it is sound and items
where it is not; only the case tells them apart.
"""

from __future__ import annotations

import random

from ..core import Item, Reject, build_item, clock, count, rule_applies_for
from ..names import COMPANIES, FIRST_NAMES, TOWNS, person

# ---------------------------------------------------------------------------------------
# music_contest

_ENSEMBLE_TYPES = (
    "String Quartet", "Brass Band", "Wind Quintet", "Youth Choir", "Guitar Trio",
    "Percussion Group", "Folk Ensemble", "Jazz Combo", "Recorder Consort", "Chamber Orchestra",
)
_PIECES = (
    "Harbour Lights", "The Long Meadow", "Winter Crossing", "Seven Bridges", "Lantern Song",
    "Northern Fields", "The Copper Kettle", "Morning Ferry", "Riverbend", "Falling Leaves",
    "The Old Mill", "Salt and Stone", "Midsummer Dance", "Grey Hills", "Clockwork March",
    "Paper Boats",
)


def draw_music_contest(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    bonus = rng.choice((3, 4, 5, 6))
    # Ensembles 0..3 in the roles: 0 leader (highest total, default), 1 argued (second,
    # behind the leader by 1..bonus-1: wins with the bonus), 2 top single score
    # (distractor), 3 filler. Which ensembles other than the argued one play their own
    # composition is drawn first; the leader never does (else the bonus would not change
    # the result). The two others may, provided the bonus does not lift them above anyone.
    for _ in range(200):
        scores = [[rng.randint(8, 20) for _ in range(3)] for _ in range(4)]
        totals = [sum(s) for s in scores]
        order = sorted(range(4), key=lambda i: -totals[i])
        if len(set(totals)) < 4:
            continue
        top = max(max(s) for s in scores)
        holders = [i for i in range(4) if top in scores[i]]
        if len(holders) != 1 or sum(s.count(top) for s in scores) != 1:
            continue
        lead, second = order[0], order[1]
        if not 1 <= totals[lead] - totals[second] <= bonus - 1:
            continue
        if holders[0] in (lead, second):
            continue
        break
    else:
        raise Reject("no score table with the required ranking")
    dist = holders[0]
    fill = ({0, 1, 2, 3} - {lead, second, dist}).pop()
    own = [False] * 4
    for i in (dist, fill):
        own[i] = rng.random() < 0.5
        if own[i] and totals[i] + bonus >= totals[lead]:
            own[i] = False
    # The deciding detail: what the argued ensemble played.
    own[second] = applies
    towns = rng.sample(TOWNS, 5)
    host, towns = towns[0], towns[1:]
    kinds = rng.sample(_ENSEMBLE_TYPES, 4)
    names = [f"{t} {k}" for t, k in zip(towns, kinds)]
    pieces = rng.sample(_PIECES, 4)
    table = "\n".join(
        f"   {n}: {s[0]}, {s[1]}, {s[2]}" for n, s in zip(names, scores)
    )
    played = [
        (f"The {n} performed its own composition '{p}'." if o
         else f"The {n} performed an arrangement of '{p}'.")
        for n, p, o in zip(names, pieces, own)
    ]
    L, X, D, F = (names[i] for i in (lead, second, dist, fill))
    return build_item(
        family="music_contest", seed=seed, rng=rng,
        title=f"{host} youth music festival judging rules",
        rules=[
            "Each ensemble is scored by three judges; each judge gives from 1 to 20 points.",
            ("An ensemble's result is the sum of its three judges' scores. The ensemble with the "
             "highest result wins."),
            f"Judges' scores this year:\n{table}",
        ],
        extra_rules=[
            "Each performance may last at most 8 minutes.",
            "Ensembles may have between 3 and 30 members.",
            "Judges do not discuss their scores before handing them in.",
        ],
        neutral_pool=[
            "The winning ensemble is invited to play at the closing concert.",
            "Score sheets are returned to the ensembles after the festival.",
            "Every ensemble receives a certificate of participation.",
        ],
        changing=(
            f"An ensemble that performs its own composition receives {bonus} bonus points on "
            "its result."
        ),
        case_lead=f"Four ensembles took part in this year's {host} festival.",
        case_rest=played,
        question="Which ensemble wins the festival?",
        answers={"default": f"The {L}", "changed": f"The {X}",
                 "distractor": f"The {D}", "filler": f"The {F}"},
        rule_applies=applies,
        rule_reasoning=(
            f"The {X} performed its own composition, so it receives {bonus} bonus points: "
            f"{totals[second]} + {bonus} = {totals[second] + bonus}, which is more than the "
            f"{L}'s {totals[lead]}. The {X} wins."
        ),
        distractor_reasoning=(
            f"The {D} received the highest single score of the festival, {top}, so the {D} "
            "wins."
        ),
        params={"names": names, "scores": scores, "own_composition": own, "bonus": bonus},
    )


# ---------------------------------------------------------------------------------------
# orienteering_results


def draw_orienteering_results(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    per_miss = rng.choice((5, 10))
    penalty = rng.choice((10, 15, 20, 25, 30))
    n_controls = rng.randint(6, 10)
    raw = [rng.randint(50, 100) for _ in range(4)]
    misses = [rng.choice((0, 0, 1, 1, 2)) for _ in range(4)]
    result = [r + per_miss * m for r, m in zip(raw, misses)]
    if len(set(result)) < 4 or len(set(raw)) < 4:
        raise Reject("ties")
    order = sorted(range(4), key=lambda i: result[i])
    lead, second = order[0], order[1]
    # The penalty must put the leader strictly behind the runner-up, and the runner-up must
    # stay ahead of everyone else (it does, being second).
    if not result[lead] + penalty > result[second]:
        raise Reject("penalty too small to change the winner")
    fastest = min(range(4), key=lambda i: raw[i])
    if fastest in (lead, second):
        raise Reject("the fastest running time must belong to a third runner")
    fill = ({0, 1, 2, 3} - {lead, second, fastest}).pop()
    firsts = rng.sample(FIRST_NAMES, 4)
    names = [f"{f} {person(rng).split()[1]}" for f in firsts]
    punched = []
    for m in misses:
        missed = set(rng.sample(range(2, n_controls), m))
        punched.append([c for c in range(1, n_controls + 1) if c not in missed])
    # The deciding detail: whether the leader punched two neighbouring controls in swapped
    # order. Drawn last.
    if applies:
        seq = punched[lead]
        j = rng.randrange(len(seq) - 1)
        seq[j], seq[j + 1] = seq[j + 1], seq[j]
    table = "\n".join(
        f"   {n}: running time {r} min, {count(m, 'missed control')}"
        for n, r, m in zip(names, raw, misses)
    )
    town = rng.choice(TOWNS)
    L, R, D, F = (names[i] for i in (lead, second, fastest, fill))
    return build_item(
        family="orienteering_results", seed=seed, rng=rng,
        title=f"{town} orienteering club results sheet",
        rules=[
            f"The long course has {n_controls} controls, numbered 1 to {n_controls}.",
            (f"A runner's result is the running time plus {per_miss} minutes for each missed "
             "control. The lowest result wins."),
            f"Long course, all finishers:\n{table}",
        ],
        extra_rules=[
            "Runners start at one-minute intervals.",
            "Maps are handed out at the start line.",
            "The short course is not part of this sheet.",
        ],
        neutral_pool=[
            "Results are posted on the club's notice wall the evening after the race.",
            "Runners must report to the finish tent even if they retire.",
            "Electronic punch cards are returned after the race.",
        ],
        changing=(
            "On the long course the controls must be punched in numerical order; a runner who "
            f"punches them out of order gets {penalty} penalty minutes added to the result."
        ),
        case_lead="The punch cards of the four long-course runners list the controls in the "
                  "order they were punched.",
        case_rest=[
            f"{n} punched: {', '.join(str(c) for c in p)}." for n, p in zip(names, punched)
        ],
        question="Who wins the long course?",
        answers={"default": L, "changed": R, "distractor": D, "filler": F},
        rule_applies=applies,
        rule_reasoning=(
            f"{L} punched the controls out of order, so {penalty} penalty minutes are added to "
            f"{L.split()[0]}'s result: {result[lead]} + {penalty} = {result[lead] + penalty} "
            f"minutes. {R} has {result[second]} minutes and wins."
        ),
        distractor_reasoning=(
            f"{D} has the fastest running time, {raw[fastest]} minutes, so {D.split()[0]} wins."
        ),
        params={"names": names, "running_times": raw, "missed": misses,
                "minutes_per_miss": per_miss, "order_penalty": penalty,
                "n_controls": n_controls, "punched": punched},
    )


# ---------------------------------------------------------------------------------------
# call_time_zones

_MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August",
           "September", "October", "November", "December")
_MONTH_DAYS = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


def _date(day_of_year: int) -> str:
    """Day 1..365 of a non-leap year as '14 March'."""
    assert 1 <= day_of_year <= 365, day_of_year
    d = day_of_year
    for name, n in zip(_MONTHS, _MONTH_DAYS):
        if d <= n:
            return f"{d} {name}"
        d -= n
    raise AssertionError(day_of_year)


def _offset_text(hours: int) -> str:
    return f"{count(abs(hours), 'hour')} {'ahead of' if hours > 0 else 'behind'} head office"


def draw_call_time_zones(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    towns = rng.sample(TOWNS, 4)
    head, target, others = towns[0], towns[1], towns[2:]
    offset = rng.choice([h for h in range(-9, 10) if h != 0])
    other_offsets = rng.sample([h for h in range(-9, 10) if h not in (0, offset)], 2)
    start = rng.randrange(7 * 60, 19 * 60 + 1, 15)
    local = start + 60 * offset
    wrong = start - 60 * offset
    options = {"default": local, "changed": local + 60, "distractor": wrong,
               "filler": local - 60}
    if not all(0 <= t < 24 * 60 for t in options.values()):
        raise Reject("an option falls on another day")
    w_from = rng.randint(30, 280)
    w_to = w_from + rng.randint(14, 60)
    # The deciding detail: the call date, strictly inside the window (A) or at least two
    # days outside it (N). The window's first and last days are avoided.
    if applies:
        day = rng.randint(w_from + 1, w_to - 1)
    else:
        day = rng.choice((rng.randint(w_from - 25, w_from - 2), rng.randint(w_to + 2, w_to + 25)))
    name = person(rng)
    company = rng.choice(COMPANIES)
    lines = [(target, offset), *zip(others, other_offsets)]
    rng.shuffle(lines)
    table = "\n".join(f"   {t} office: {_offset_text(h)}" for t, h in lines)
    return build_item(
        family="call_time_zones", seed=seed, rng=rng,
        title=f"{company} team call schedule",
        rules=[
            f"All calls are scheduled in head-office time. The head office is in {head}.",
            f"Local time at the other offices compared with head-office time:\n{table}",
        ],
        extra_rules=[
            "Calls last at most one hour.",
            "Each call has a named note-taker.",
            "Cameras are optional in team calls.",
        ],
        neutral_pool=[
            "The meeting link is sent out one day before each call.",
            "Calls are recorded only if every participant agrees.",
        ],
        changing=(
            f"From {_date(w_from)} to {_date(w_to)}, clocks in {target} are set one hour ahead "
            "of their usual time; the difference listed above is the usual one."
        ),
        case_lead=f"The {company} project team holds a quarterly planning call.",
        case_rest=[
            f"The call is on {_date(day)} at {clock(start)} head-office time.",
            f"{name} will join the call from the {target} office.",
            f"The call is expected to take {rng.choice((30, 40, 45, 50))} minutes.",
        ],
        question=f"At what local {target} time does the call start?",
        answers={k: clock(v) for k, v in options.items()},
        rule_applies=applies,
        rule_reasoning=(
            f"The call falls in the period when {target} clocks are set one hour ahead of their "
            f"usual time, so the call starts at {clock(local + 60)} local time in {target}."
        ),
        distractor_reasoning=(
            f"{target} is {_offset_text(offset)}, so the call starts at "
            f"{clock(start)} {'−' if offset > 0 else '+'} {count(abs(offset), 'hour')} = "
            f"{clock(wrong)} there."
        ),
        params={"head_office": head, "town": target, "offset_hours": offset,
                "other_offices": [[t, h] for t, h in zip(others, other_offsets)],
                "call_minutes": start, "window_from_day": w_from, "window_to_day": w_to,
                "call_day": day, "name": name},
    )


# ---------------------------------------------------------------------------------------
# duty_rotation

_DUTY_MONTHS = ("February", "March", "April", "May", "June", "July", "September", "October",
                "November")


def draw_duty_rotation(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    n = rng.randint(4, 6)
    names = rng.sample(FIRST_NAMES, n)
    first_sat = rng.randint(1, 7)
    weekends = [first_sat + 7 * k for k in range(4) if first_sat + 7 * k + 1 <= 28]
    k = rng.randint(1, len(weekends) - 1)
    sat = weekends[k]
    on_duty, nxt, prev = names[k % n], names[(k + 1) % n], names[(k - 1) % n]
    fill = rng.choice([x for x in names if x not in (on_duty, nxt, prev)])
    # The deciding detail: whether the on-duty person's leave covers the whole weekend (A)
    # or ends in the week before it / starts in the week after it (N). Drawn last.
    if applies:
        lo = rng.randint(max(1, sat - 9), sat)
        hi = rng.randint(sat + 1, min(30, lo + 13))
        if hi - lo + 1 < 3:
            raise Reject("leave too short")
    elif rng.random() < 0.5:
        hi = rng.randint(max(3, sat - 5), sat - 1)
        lo = rng.randint(max(1, hi - 9), hi - 2)
    else:
        lo = rng.randint(sat + 2, sat + 4)
        if lo + 2 > 30:
            raise Reject("no room for the leave after the weekend")
        hi = rng.randint(lo + 2, min(30, lo + 9))
    if lo < 1 or hi > 30 or hi < lo + 2:
        raise Reject("leave outside the month")
    month = rng.choice(_DUTY_MONTHS)
    company = rng.choice(COMPANIES)
    other = rng.choice([x for x in names if x != on_duty])
    order = "\n".join(f"   {i}. {x}" for i, x in enumerate(names, 1))
    dates = ", ".join(f"{d}–{d + 1}" for d in weekends)
    return build_item(
        family="duty_rotation", seed=seed, rng=rng,
        title=f"{company} weekend duty rota",
        rules=[
            f"Duty weekends in {month} (Saturday–Sunday): {dates} {month}.",
            f"Order of the rota:\n{order}",
            (f"{names[0]} is on duty on the first duty weekend of {month}. Each following "
             "weekend the duty passes to the next name in the order; after the last name it "
             "starts again at the top."),
        ],
        extra_rules=[
            "The person on duty keeps the duty phone from Saturday 08:00 to Sunday 20:00.",
            "Duty hours are paid at the weekend rate.",
            "The rota for the next month is published on the 20th.",
        ],
        neutral_pool=[
            "The person on duty logs every call in the duty book.",
            "Questions about the rota go to the team lead.",
        ],
        changing=(
            "If the person whose turn it is is on leave during the duty weekend, the next "
            "person in the order takes that weekend instead."
        ),
        case_lead=f"The team is checking the {month} rota.",
        case_rest=[
            f"{on_duty} is on leave from {lo} to {hi} {month}.",
            f"{other} has asked to swap desks next month.",
        ],
        question=f"Who is on duty on the weekend of {sat}–{sat + 1} {month}?",
        answers={"default": on_duty, "changed": nxt, "distractor": prev, "filler": fill},
        rule_applies=applies,
        rule_reasoning=(
            f"{on_duty} is on leave during that weekend, so the next person in the order, "
            f"{nxt}, takes the duty."
        ),
        distractor_reasoning=(
            f"The weekend of {sat}–{sat + 1} {month} is {k} weekends after the first one, so it "
            f"is name number {k} in the order: {prev}."
        ),
        params={"names": names, "weekend_saturdays": weekends, "asked_saturday": sat,
                "leave_from": lo, "leave_to": hi, "month": month, "filler": fill},
    )


# ---------------------------------------------------------------------------------------
# language_course_enrolment

_LANGUAGES = ("Spanish", "Italian", "Portuguese", "Dutch", "Swedish", "Greek", "Polish",
              "Turkish", "Japanese", "Korean")


def draw_language_course_enrolment(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    max_age = rng.randint(2, 5)
    full = rng.choice((70, 75, 80, 85, 90))
    need = full * 60 // 100
    # The raw score is under 60 (the distractor's mistake) but at least 2 marks above 60%.
    score = rng.randint(need + 2, 59)
    start_month = rng.randrange(12)
    start_year = rng.randint(2026, 2027)
    # The deciding detail: months between the exam and the course start. More than
    # max_age years by at least 3 months (A), or at most max_age years less 3 months (N).
    gap = rng.randint(12 * max_age + 3, 12 * max_age + 36) if applies else rng.randint(
        3, 12 * max_age - 3)
    exam_abs = start_year * 12 + start_month - gap
    exam_year, exam_month = divmod(exam_abs, 12)
    name = person(rng)
    first = name.split()[0]
    language = rng.choice(_LANGUAGES)
    school = rng.choice(COMPANIES)
    return build_item(
        family="language_course_enrolment", seed=seed, rng=rng,
        title=f"{school} language school course rules",
        rules=[
            (f"Students may join the advanced {language} course if they have passed the "
             f"intermediate {language} exam with at least 60% of the marks."),
            f"The intermediate exam is marked out of {full} marks.",
        ],
        extra_rules=[
            "Classes have at most 12 students.",
            "Course fees are paid at the start of each term.",
            "Lessons take place on weekday evenings.",
        ],
        neutral_pool=[
            "Course books are included in the fee.",
            "Students who miss three lessons in a row are contacted by their teacher.",
        ],
        changing=(
            f"Exam results that are more than {count(max_age, 'year')} old when the course "
            "starts no longer count; students whose result is older may join the advanced "
            "course after passing a placement test."
        ),
        case_lead=f"{name} wants to join the advanced {language} course at {school}.",
        case_rest=[
            (f"{first} passed the intermediate {language} exam in {_MONTHS[exam_month]} "
             f"{exam_year} with {score} out of {full} marks."),
            f"The advanced course starts in {_MONTHS[start_month]} {start_year}.",
            f"{first} prefers the {rng.choice(('Tuesday', 'Wednesday', 'Thursday'))} group.",
        ],
        question=f"Can {name} join the advanced course?",
        answers={"default": "Yes", "changed": "Yes, after passing a placement test",
                 "distractor": "No", "filler": "Only as a listener"},
        rule_applies=applies,
        rule_reasoning=(
            f"{first}'s exam result is too old to count for the advanced course, so {first} "
            "must first pass a placement test."
        ),
        distractor_reasoning=(
            f"{first} scored {score} marks, which is below 60, so {first} has not reached "
            "the entry mark and cannot join."
        ),
        params={"name": name, "language": language, "max_marks": full, "score": score,
                "exam_month": exam_month + 1, "exam_year": exam_year,
                "start_month": start_month + 1, "start_year": start_year,
                "max_age_years": max_age},
    )


FAMILIES = {
    "music_contest": draw_music_contest,
    "orienteering_results": draw_orienteering_results,
    "call_time_zones": draw_call_time_zones,
    "duty_rotation": draw_duty_rotation,
    "language_course_enrolment": draw_language_course_enrolment,
}
