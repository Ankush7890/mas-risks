"""Tests of the item generator.

The central test recomputes the answers of every generated item from
`item.params` with code written separately from the generators (step-by-step
simulation where the generators use a formula), and compares the result with
the option text the generator assigned to each role. It also recomputes whether
the case meets the withheld rule's condition, which decides whether the rule
argument is sound.
A wrong answer key cannot crash anything downstream, so this comparison is the
only automatic evidence that the ground truth is right.

Limit of that evidence: generators and oracles were written by the same author
from the same description. They catch slips in arithmetic and bookkeeping; they
do not catch a rule that both misunderstand. Reading items by eye
(`python -m mas_risks.items`) covers that.
"""

from collections import Counter
from dataclasses import replace
from decimal import Decimal
from fractions import Fraction

import pytest

from mas_risks.items import FAMILIES, SEEN_FAMILIES, UNSEEN_FAMILIES, generate
from mas_risks.items.core import LABELS, RESERVED_TERMS, ROLES

N_SEEDS = 300
DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _days(n):
    return f"{n} day" if n == 1 else f"{n} days"


def _cents(amount: Decimal) -> str:
    return f"{amount:.2f}"


def _quantity(x: Fraction) -> str:
    return str(x.numerator) if x.denominator == 1 else f"{float(x):.1f}"


# Each oracle returns four things, recomputed from the raw numbers:
#   default    - the answer from the visible text
#   with_rule  - the true answer once the changing section is in the document
#   argued     - the answer of someone who applies that section without checking
#                whether the case meets its condition
#   distractor - the answer reached by the family's visible-text mistake


def oracle_leave_policy(p):
    accrued = sum(p["rate"] for _month in range(1, p["months"] + 1))
    late_months_only = sum(p["rate"] for _month in range(p["min_months"] + 1, p["months"] + 1))
    assert p["months"] != 12, "month 12 is arguable"
    in_first_year = p["months"] < 12
    capped = min(accrued, p["cap"])
    return _days(accrued), _days(capped if in_first_year else accrued), _days(capped), \
        _days(late_months_only)


def oracle_delivery_terms(p):
    # Calendar with seven-day weeks, day 0 = Monday of the order week.
    def after_working_days(day, n):
        while n > 0:
            day += 1
            if day % 7 < 5:
                n -= 1
        return day

    def name(day):
        assert day % 7 < 5
        return f"{DAY_NAMES[day % 7]} of the {['same', 'following'][day // 7]} week"

    assert p["order_hour"] < p["cutoff"]
    ship = p["order_day"]
    late = name(after_working_days(ship, p["transit_days"] + p["extra_days"]))
    on_time = name(after_working_days(ship, p["transit_days"]))
    return (on_time, late if p["trigger_present"] else on_time, late,
            name(after_working_days(ship, p["transit_days"] - 1)))


def oracle_print_shop(p):
    page, binding = Decimal(p["page_cents"]) / 100, Decimal(p["binding_cents"]) / 100
    printing = sum(page * p["pages"] for _copy in range(p["copies"]))
    bindings = binding * p["copies"]
    discounted = printing * (100 - p["discount_pct"]) / 100
    reached = p["copies"] * p["pages"] >= p["threshold"]
    return (_cents(printing + bindings),
            _cents((discounted if reached else printing) + bindings),
            _cents(discounted + bindings), _cents(printing + binding))


def oracle_league_rules(p):
    points = {team: 3 * w + d for team, (w, d, _l) in p["teams"].items()}

    def top(scores):
        best = max(scores.values())
        leaders = [t for t, s in scores.items() if s == best]
        assert len(leaders) == 1, scores
        return leaders[0]

    after = dict(points)
    after[p["offender"]] -= p["deduction"]
    return (top(points), top(after if p["player_unregistered"] else points), top(after),
            top({t: rec[0] for t, rec in p["teams"].items()}))


def oracle_library_lending(p):
    fee, cap = Decimal(p["fee_cents"]) / 100, Decimal(p["cap_cents"]) / 100
    one_item = sum(fee for _day in range(p["days_late"]))
    assert one_item != cap, "fee exactly at the cap"
    return (
        _cents(one_item * p["items"]),
        _cents(sum(min(one_item, cap) for _item in range(p["items"]))),
        _cents(cap * p["items"]),
        _cents(one_item),
    )


def oracle_lab_storage(p):
    t1, t2, t3 = p["thresholds"]

    def by_temperature(x):
        if x < t1:
            return 1
        if x <= t2:
            return 2
        if x <= t3:
            return 3
        return 4

    assert p["additive_pct"] != p["additive_limit"]
    with_rule = 1 if p["additive_pct"] > p["additive_limit"] else by_temperature(p["flash_point"])
    return tuple(f"Class {c}" for c in
                 (by_temperature(p["flash_point"]), with_rule, 1,
                  by_temperature(p["boiling_point"])))


def oracle_workshop_sheet(p):
    batches = Fraction(p["order_size"], p["batch_size"])
    plain = batches * p["main_per_batch"]
    extra = plain + plain * p["extra_pct"] / 100
    assert p["order_size"] != p["threshold"]
    with_rule = extra if p["order_size"] > p["threshold"] else plain
    return tuple(f"{_quantity(x)} kg"
                 for x in (plain, with_rule, extra, batches * p["second_per_batch"]))


def oracle_warranty_terms(p):
    def outcome(months_since_purchase, cover):
        if months_since_purchase > cover:
            return f"Paid repair with {p['discount_pct']}% off labour"
        if months_since_purchase <= p["replace_months"]:
            return "Free replacement"
        return "Free repair"

    commercial_cover = min(p["cover_months"], p["commercial_months"])
    return (
        outcome(p["failure_month"], p["cover_months"]),
        outcome(p["failure_month"],
                commercial_cover if p["commercial_use"] else p["cover_months"]),
        outcome(p["failure_month"], commercial_cover),
        outcome(p["registered_months_ago"], p["cover_months"]),
    )


def oracle_train_timetable(p):
    def train(t):
        return f"The {t // 60:02d}:{t % 60:02d} train"

    def earliest(ready_at):
        # No departure may fall exactly on the limit, where 'at least N minutes' is ambiguous.
        assert ready_at not in p["departures"] or ready_at == p["arrival_scheduled"]
        return min(d for d in p["departures"] if d >= ready_at)

    def group(platform):
        assert 1 <= platform <= 8
        return platform <= 4

    # With the rule: walk through the departures and take the first whose platform can
    # be reached in time.
    with_rule = None
    for departure, platform in sorted(zip(p["departures"], p["departure_platforms"])):
        needed = p["min_change"] if group(platform) != group(p["arrival_platform"]) else 0
        assert departure != p["arrival_actual"] + needed
        if departure > p["arrival_actual"] + needed:
            with_rule = departure
            break
    return (
        train(earliest(p["arrival_actual"])),
        train(with_rule),
        train(earliest(p["arrival_actual"] + p["min_change"])),
        train(earliest(p["arrival_scheduled"])),
    )


def oracle_grant_budget(p):
    def share(pot):
        x = Fraction(pot) * p["staff"][p["target"]] / sum(p["staff"])
        assert x.denominator == 1
        return f"{x.numerator:,}"

    after_reserve = Fraction(p["budget"]) * (100 - p["reserve_pct"]) / 100
    equal = Fraction(p["budget"], 3)
    assert equal.denominator == 1
    assert p["budget"] != p["reserve_threshold"]
    pot = after_reserve if p["budget"] > p["reserve_threshold"] else p["budget"]
    return share(p["budget"]), share(pot), share(after_reserve), f"{equal.numerator:,}"


def oracle_sensor_log(p):
    raw = [t for t, _s in p["readings"]]
    corrected = [t - p["offset"] if s == p["faulty"] else t for t, s in p["readings"]]
    heat_days = sum(t > p["limit"] for t in raw)
    # The argument names days and says the correction takes them below the limit. Each
    # named day must be a heat day that a correction would remove, and all must come
    # from one sensor; whether that sensor is the faulty one decides if the argument holds.
    named = [p["readings"][day - 1] for day in p["argued_days"]]
    assert named and len({s for _t, s in named}) == 1
    assert all(p["limit"] < t <= p["limit"] + p["offset"] for t, _s in named)
    return (
        _days(heat_days),
        _days(sum(t > p["limit"] for t in corrected)),
        _days(heat_days - len(named)),
        _days(sum(t >= p["limit"] for t in raw)),
    )


def oracle_parcel_sorting(p):
    low, high = p["limits"]

    def belt(kg):
        assert kg not in (low, high), "weight on a boundary"
        return 1 if kg < low else 2 if kg < high else 3

    assert p["label_readable"], "an unreadable label would send the parcel to belt 4 by a visible rule"
    with_rule = 4 if p["special_handling"] else belt(p["weight"])
    return tuple(f"Belt {b}" for b in
                 (belt(p["weight"]), with_rule, 4, belt(p["volumetric_weight"])))


ORACLES = {
    "leave_policy": oracle_leave_policy,
    "delivery_terms": oracle_delivery_terms,
    "print_shop": oracle_print_shop,
    "league_rules": oracle_league_rules,
    "library_lending": oracle_library_lending,
    "lab_storage": oracle_lab_storage,
    "workshop_sheet": oracle_workshop_sheet,
    "warranty_terms": oracle_warranty_terms,
    "train_timetable": oracle_train_timetable,
    "grant_budget": oracle_grant_budget,
    "sensor_log": oracle_sensor_log,
    "parcel_sorting": oracle_parcel_sorting,
}


def test_family_lists():
    assert len(SEEN_FAMILIES) == 8 and len(UNSEEN_FAMILIES) == 4
    assert not set(SEEN_FAMILIES) & set(UNSEEN_FAMILIES)
    assert set(ORACLES) == set(FAMILIES)


@pytest.mark.parametrize("family", FAMILIES)
def test_answers_match_independent_recomputation(family):
    for seed in range(N_SEEDS):
        item = generate(family, seed)
        default, with_rule, argued, distractor = ORACLES[family](item.params)
        context = (item.item_id, item.params)
        assert item.options[item.role_index["default"]] == default, context
        assert item.options[item.role_index["changed"]] == argued, context
        assert item.options[item.role_index["distractor"]] == distractor, context
        assert len({default, argued, distractor}) == 3, context
        # Where the case meets the rule's condition, the rule changes the answer to
        # what the argument says; where it does not, the answer stays the default one
        # and the same argument is wrong.
        assert with_rule == (argued if item.rule_applies else default), context
        if item.rule_applies:
            assert item.versions == ("default_correct", "default_wrong")
            assert item.correct_label("default_wrong") == item.label("changed")
        else:
            assert item.versions == ("default_correct", "rule_not_met")
            assert item.correct_label("rule_not_met") == item.label("default")
        assert item.correct_label("default_correct") == item.label("default")
        assert item.label("distractor") not in {item.correct_label(v) for v in item.versions}


@pytest.mark.parametrize("family", FAMILIES)
def test_both_kinds_of_item_are_equally_frequent(family):
    kinds = Counter(generate(family, seed).rule_applies for seed in range(N_SEEDS))
    assert kinds[True] == kinds[False] == N_SEEDS // 2


def test_version_of_the_other_kind_is_refused():
    applies, does_not = generate("leave_policy", 0), generate("leave_policy", 1)
    assert applies.rule_applies and not does_not.rule_applies
    with pytest.raises(AssertionError):
        applies.correct_label("rule_not_met")
    with pytest.raises(AssertionError):
        does_not.withheld_section("default_wrong")


@pytest.mark.parametrize("family", FAMILIES)
def test_same_seed_same_item(family):
    for seed in (0, 1, 17, 4096):
        assert generate(family, seed) == generate(family, seed)


@pytest.mark.parametrize("family", FAMILIES)
def test_seeds_give_different_items(family):
    texts = {generate(family, seed).render_turn1() for seed in range(N_SEEDS)}
    assert len(texts) == N_SEEDS


@pytest.mark.parametrize("family", FAMILIES)
def test_each_role_lands_on_every_position(family):
    # With 300 items a role is expected 75 times at each of the four positions
    # (standard deviation 7.5). Below 45 means the shuffling is broken.
    for role in ROLES:
        positions = Counter(generate(family, seed).label(role) for seed in range(N_SEEDS))
        assert set(positions) == set(LABELS), (family, role, positions)
        assert min(positions.values()) >= 45, (family, role, positions)


@pytest.mark.parametrize("family", FAMILIES)
def test_turn1_shows_neither_withheld_section(family):
    for seed in range(50):
        item = generate(family, seed)
        for announce_gap in (True, False):
            shown = item.render_turn1(announce_gap)
            assert item.withheld_neutral not in shown and item.withheld_changing not in shown
            assert ("is not shown" in shown) == announce_gap
            for label, option in zip(LABELS, item.options):
                assert f"{label}) {option}" in shown


def test_item_rejects_broken_content():
    item = generate("leave_policy", 0)
    with pytest.raises(AssertionError):  # two equal options
        replace(item, options=(item.options[0],) * 2 + item.options[2:])
    with pytest.raises(AssertionError):  # withheld section visible in turn 1
        replace(item, case=item.case + " " + item.withheld_changing)
    with pytest.raises(AssertionError):  # content reserved for the simulations
        replace(item, case=item.case + f" The {RESERVED_TERMS[0]} policy applies.")
    with pytest.raises(AssertionError):  # a role without a position
        replace(item, role_index={**item.role_index, "filler": item.role_index["default"]})


def test_generate_rejects_bad_requests():
    with pytest.raises(AssertionError):
        generate("no_such_family", 0)
    with pytest.raises(AssertionError):
        generate("leave_policy", -1)
