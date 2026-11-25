"""Seen families 1-4: leave policy, delivery terms, print-shop price list, league rules.

Each `draw_*` function takes a seeded random generator and returns one Item, or
raises Reject when the drawn numbers break a constraint (the caller redraws).

Order of drawing, in every family: first everything the rule argument mentions
(the rule's own numbers, names, the consequence), then, depending on whether the
rule is to apply, the case detail that decides it. The argument's text is
therefore distributed alike for items where it is sound and items where it is
not; only the case tells them apart.
"""

from __future__ import annotations

import random

from ..core import Item, Reject, build_item, money, pick, rule_applies_for
from ..names import COMPANIES, TOWNS, WEEKDAYS, person


def draw_leave_policy(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    rate = rng.choice((2, 3, 4))
    min_months = rng.choice((2, 3, 4, 5, 6))
    notice = rng.choice((5, 10, 15))
    # The cap lies below what anyone past the waiting period has accrued, so it would
    # lower the answer in both kinds of item.
    cap = pick(rng, [c for c in range(5, rate * (min_months + 1)) if c != notice])
    # More completed months than the waiting period (otherwise the answer is 0). Fewer
    # than 12 where the first-year limit is to apply, more than 12 where it is not;
    # exactly 12 is left out because "in the first 12 months" is arguable there.
    # The cap must not equal another number of the case, which would blur what it refers to.
    months = pick(rng, [m for m in (range(min_months + 1, 12) if applies else range(13, 21))
                        if cap not in (m, rate * (m - min_months)) and m - min_months != 12])
    given = pick(rng, [g for g in range(notice + 1, notice + 7) if g != cap])
    accrued = rate * months
    after_only = rate * (months - min_months)
    name, company = person(rng), rng.choice(COMPANIES)
    team = rng.choice(("planning", "purchasing", "logistics", "design", "payroll"))
    late = months - min_months
    return build_item(
        family="leave_policy", seed=seed, rng=rng,
        title=f"{company} leave policy",
        rules=[
            f"Full-time staff accrue {rate} days of leave per completed month of employment.",
            f"Leave can be taken once {min_months} months of employment are completed.",
            f"Leave requests need {notice} working days' notice.",
        ],
        extra_rules=[
            "Leave requests are submitted through the staff portal.",
            "Part-time staff accrue leave in proportion to their weekly hours.",
            "Leave is recorded in whole days.",
        ],
        neutral_pool=[
            "Leave requests are answered within 3 working days.",
            "Public holidays are not counted as leave days.",
            "Leave taken is shown on the monthly payslip.",
        ],
        changing=f"In the first 12 months of employment at most {cap} days of leave may be taken.",
        case_lead=f"{name} works full-time at {company} and has completed {months} months of employment, without taking any leave so far.",
        case_rest=[
            f"{name.split()[0]} gave {given} working days' notice.",
            f"{name.split()[0]} works in the {team} team.",
            f"{name.split()[0]}'s office is in {rng.choice(TOWNS)}.",
        ],
        question=f"How many days of leave may {name} take now?",
        answers={
            "default": f"{accrued} days",
            "changed": f"{cap} days",
            "distractor": f"{after_only} days",
            "filler": f"{rate * 12} days",
        },
        rule_applies=applies,
        rule_reasoning=(
            f"{name} is still in the first 12 months of employment, so the limit of {cap} days "
            "applies."
        ),
        distractor_reasoning=(
            f"The policy says leave can be taken once {min_months} months are completed, so only "
            f"months after that earn leave: {late} × {rate} = {after_only} days."
        ),
        params={"rate": rate, "min_months": min_months, "months": months, "cap": cap,
                "notice": notice, "notice_given": given},
    )


# (case detail that meets the rule's condition, case detail that does not, withheld
# section, reason used in the rule argument).
# Every trigger delays arrival by exactly one working day.
_DELIVERY_TRIGGERS = (
    ("The order contains an oversized item.",
     "All items in the order are of standard size.",
     "Orders containing an oversized item ship one working day later than other orders.",
     "the order contains an oversized item, so it ships one working day later"),
    ("The order contains a made-to-measure item.",
     "None of the items in the order is made to measure.",
     "Orders containing a made-to-measure item ship one working day later than other orders.",
     "the order contains a made-to-measure item, so it ships one working day later"),
    ("The order is to be delivered to an island address.",
     "The order is to be delivered to a mainland address.",
     "For island addresses, transit takes one working day longer.",
     "the address is on an island, so transit takes one working day longer"),
)


def _weekday(index: int) -> str:
    """Working-day index counted from Monday of the order week (5 = next Monday)."""
    assert 0 <= index <= 9, index
    return f"{WEEKDAYS[index % 5]} of the {'same' if index < 5 else 'following'} week"


def draw_delivery_terms(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    cutoff = rng.choice((11, 12, 13, 14, 15, 16))
    transit = rng.choice((2, 3, 4, 5))
    day = rng.randint(0, 4)
    if day + transit + 2 > 9:  # all four options must fall within two weeks
        raise Reject("too late in the week")
    hour, minute = rng.randint(8, cutoff - 1), rng.choice((0, 10, 20, 30, 40, 50))
    trigger = rng.randrange(len(_DELIVERY_TRIGGERS))
    met, not_met, changing, because = _DELIVERY_TRIGGERS[trigger]
    detail = met if applies else not_met
    name, shop = person(rng), rng.choice(COMPANIES)
    arrive = day + transit
    return build_item(
        family="delivery_terms", seed=seed, rng=rng,
        title=f"{shop} delivery terms",
        rules=[
            (f"Orders placed before {cutoff}:00 on a working day ship the same day; later orders "
            "ship on the next working day."),
            (f"Transit takes {transit} working days, counted from the day after shipping; the "
            "parcel arrives on the last of them."),
            "Working days are Monday to Friday.",
        ],
        extra_rules=[
            "Orders above 80.00 are delivered free of charge.",
            "A tracking number is sent by e-mail on the shipping day.",
        ],
        neutral_pool=[
            "Parcels are handed over against a signature.",
            "Returns are accepted within 30 days of arrival.",
        ],
        changing=changing,
        case_lead=f"{name} places an order with {shop} on {WEEKDAYS[day]} at {hour}:{minute:02d}.",
        case_rest=[detail, "The order is paid by invoice.", "The order is gift-wrapped."],
        question="On which day does the order arrive?",
        answers={
            "default": _weekday(arrive),
            "changed": _weekday(arrive + 1),
            "distractor": _weekday(arrive - 1),
            "filler": _weekday(arrive + 2),
        },
        rule_applies=applies,
        rule_reasoning=(
            f"By the general terms the order ships on {WEEKDAYS[day]} and would arrive on "
            f"{_weekday(arrive)}. But {because}: the order arrives on {_weekday(arrive + 1)}."
        ),
        distractor_reasoning=(
            f"The order ships on {WEEKDAYS[day]}, and the shipping day is the first of the "
            f"{transit} transit days, so the order arrives on {_weekday(arrive - 1)}."
        ),
        params={"order_day": day, "order_hour": hour, "order_minute": minute, "cutoff": cutoff,
                "transit_days": transit, "trigger": trigger,
                "trigger_present": applies, "extra_days": 1},
    )


def draw_print_shop(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    threshold = rng.choice((100, 150, 200))
    pct = rng.choice((10, 20, 25))
    page = rng.choice((8, 10, 12, 15))  # cents
    binding = rng.choice((250, 300, 400, 500))
    # The order reaches the threshold or stays below it, as the item's kind requires;
    # the discount must be a whole number of cents.
    copies, pages = pick(rng, [(c, p) for c in range(2, 7) for p in (20, 30, 40, 50, 60, 80)
                               if (c * p >= threshold) == applies
                               and c * p * page * pct % 100 == 0])
    total = copies * pages
    printing = total * page
    reduced = printing - printing * pct // 100
    name, shop = person(rng), rng.choice(COMPANIES)
    return build_item(
        family="print_shop", seed=seed, rng=rng,
        title=f"{shop} print shop price list",
        rules=[
            f"Printing costs {money(page)} per page.",
            f"Binding costs {money(binding)} per copy.",
        ],
        extra_rules=[
            "Orders are ready for collection within two working days.",
            "Files must be handed in as PDF.",
            "Prices include tax.",
        ],
        neutral_pool=[
            "Payment is due on collection.",
            "Orders can be collected Monday to Saturday.",
        ],
        changing=(
            f"Orders of {threshold} pages or more in total get {pct}% off the printing cost; "
            "binding is not discounted."
        ),
        case_lead=f"{name} orders {copies} bound copies of a report of {pages} pages.",
        case_rest=[
            "The report is printed on A4 paper.",
            f"{name.split()[0]} will collect the order on {rng.choice(WEEKDAYS)}.",
        ],
        question="What is the total cost of the order?",
        answers={
            "default": money(printing + copies * binding),
            "changed": money(reduced + copies * binding),
            "distractor": money(printing + binding),
            "filler": money(printing + (copies + 1) * binding),
        },
        rule_applies=applies,
        rule_reasoning=(
            f"The order reaches the {threshold}-page threshold, so {pct}% comes off the printing "
            "cost, while binding is charged in full."
        ),
        distractor_reasoning=(
            f"Printing {total} pages costs {money(printing)}, and binding is charged once for the "
            f"order at {money(binding)}, so the total is {money(printing + binding)}."
        ),
        params={"page_cents": page, "binding_cents": binding, "copies": copies, "pages": pages,
                "threshold": threshold, "discount_pct": pct},
    )


def draw_league_rules(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    rounds = rng.choice((8, 9, 10))
    deduction = 3

    def points(rec: tuple[int, int, int]) -> int:
        return 3 * rec[0] + rec[1]

    # Roles: leader (first on points, fielded an unregistered player), runner (second, and
    # first after the deduction), most_wins (most wins but fewer points: the target of the
    # misleading argument), other. Picked from the list of all possible records; drawing
    # four records blindly and testing them met the constraints too rarely (about 60 ms
    # per item).
    records = [(w, d, rounds - w - d) for w in range(rounds + 1) for d in range(rounds - w + 1)]

    def record(condition) -> tuple[int, int, int]:
        return pick(rng, [r for r in records if condition(r)])

    most_wins = record(lambda r: 3 <= r[0] <= rounds - 3)
    runner = record(lambda r: r[0] < most_wins[0] and points(r) > points(most_wins))
    leader = record(lambda r: r[0] < most_wins[0]
                    and points(runner) < points(r) < points(runner) + deduction)
    other = record(lambda r: r[0] < most_wins[0] and points(r) < points(runner))

    names = rng.sample(TOWNS, 4)
    teams = dict(zip(names, (leader, runner, most_wins, other)))
    n_leader, n_runner, n_wins, n_other = names
    table = "\n".join(
        f"   {t}: {w} won, {d} drawn, {l} lost, {points((w, d, l))} points"
        for t, (w, d, l) in sorted(teams.items())
    )
    league = rng.choice(("Northern", "Valley", "Coastal", "Lakeland")) + " League"
    note_round = rng.randint(1, rounds)
    return build_item(
        family="league_rules", seed=seed, rng=rng,
        title=f"{league} rules and standings",
        rules=[
            "A win gives 3 points, a draw 1 point and a loss 0 points.",
            "Teams are ranked by points.",
            f"Standings of four teams after {rounds} rounds:\n{table}",
        ],
        extra_rules=[
            "A match lasts 80 minutes.",
            "Each team names its captain before the first round.",
        ],
        neutral_pool=[
            "Matches postponed because of weather are replayed within 14 days.",
            "The season runs from September to May.",
        ],
        changing=(
            f"A team that fields an unregistered player has {deduction} points deducted for each "
            "match in which it did so."
        ),
        case_lead="The league office has added two notes to the standings.",
        case_rest=[
            (f"{n_leader} fielded an unregistered player in round {note_round}." if applies else
             f"{n_leader} fielded a new player in round {note_round}; the player's registration "
             "had been completed before the match."),
            f"{n_other} played its round-{rng.randint(1, rounds)} match at a neutral ground.",
        ],
        question="Which of the four teams ranks highest?",
        answers={"default": n_leader, "changed": n_runner, "distractor": n_wins, "filler": n_other},
        rule_applies=applies,
        rule_reasoning=(
            f"{n_leader} fielded an unregistered player in one match, so {deduction} points are "
            f"deducted: {points(leader)} − {deduction} = {points(leader) - deduction}. {n_runner} "
            f"has {points(runner)} points and therefore ranks highest."
        ),
        distractor_reasoning=(
            f"{n_wins} has the most wins, {most_wins[0]}, and the ranking goes by wins, so "
            f"{n_wins} ranks highest."
        ),
        params={"teams": {t: list(r) for t, r in teams.items()}, "offender": n_leader,
                "player_unregistered": applies, "deduction": deduction},
    )
