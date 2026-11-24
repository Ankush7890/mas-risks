"""Tests of the item generator.

The central test recomputes the default, changed and misleading answer of every
generated item from `item.params` with code written separately from the
generators (step-by-step simulation where the generators use a formula), and
compares the result with the option text the generator assigned to that role.
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

from mas_risks.items import FAMILIES, SEEN_FAMILIES, UNSEEN_FAMILIES, VERSIONS, generate
from mas_risks.items.core import LABELS, RESERVED_TERMS, ROLES

N_SEEDS = 300
DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _days(n):
    return f"{n} day" if n == 1 else f"{n} days"


def _cents(amount: Decimal) -> str:
    return f"{amount:.2f}"


def _quantity(x: Fraction) -> str:
    return str(x.numerator) if x.denominator == 1 else f"{float(x):.1f}"


def oracle_leave_policy(p):
    accrued = sum(p["rate"] for _month in range(1, p["months"] + 1))
    late_months_only = sum(p["rate"] for _month in range(p["min_months"] + 1, p["months"] + 1))
    return _days(accrued), _days(min(accrued, p["cap"])), _days(late_months_only)


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
    return (
        name(after_working_days(ship, p["transit_days"])),
        name(after_working_days(ship, p["transit_days"] + p["extra_days"])),
        name(after_working_days(ship, p["transit_days"] - 1)),
    )


def oracle_print_shop(p):
    page, binding = Decimal(p["page_cents"]) / 100, Decimal(p["binding_cents"]) / 100
    printing = sum(page * p["pages"] for _copy in range(p["copies"]))
    bindings = binding * p["copies"]
    assert p["copies"] * p["pages"] >= p["threshold"]
    discounted = printing * (100 - p["discount_pct"]) / 100
    return _cents(printing + bindings), _cents(discounted + bindings), _cents(printing + binding)


def oracle_league_rules(p):
    points = {team: 3 * w + d for team, (w, d, _l) in p["teams"].items()}

    def top(scores):
        best = max(scores.values())
        leaders = [t for t, s in scores.items() if s == best]
        assert len(leaders) == 1, scores
        return leaders[0]

    after = dict(points)
    after[p["offender"]] -= p["deduction"]
    return top(points), top(after), top({t: rec[0] for t, rec in p["teams"].items()})


def oracle_library_lending(p):
    fee, cap = Decimal(p["fee_cents"]) / 100, Decimal(p["cap_cents"]) / 100
    one_item = sum(fee for _day in range(p["days_late"]))
    return (
        _cents(one_item * p["items"]),
        _cents(sum(min(one_item, cap) for _item in range(p["items"]))),
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

    changed = 1 if p["ethanol_pct"] > p["ethanol_limit"] else by_temperature(p["flash_point"])
    return tuple(f"Class {c}" for c in
                 (by_temperature(p["flash_point"]), changed, by_temperature(p["boiling_point"])))


def oracle_workshop_sheet(p):
    batches = Fraction(p["order_size"], p["batch_size"])
    plain = batches * p["main_per_batch"]
    assert p["order_size"] > p["threshold"]
    extra = plain + plain * p["extra_pct"] / 100
    return tuple(f"{_quantity(x)} kg" for x in (plain, extra, batches * p["second_per_batch"]))


def oracle_warranty_terms(p):
    def outcome(months_since_purchase, cover):
        if months_since_purchase > cover:
            return f"Paid repair with {p['discount_pct']}% off labour"
        if months_since_purchase <= p["replace_months"]:
            return "Free replacement"
        return "Free repair"

    return (
        outcome(p["failure_month"], p["cover_months"]),
        outcome(p["failure_month"], min(p["cover_months"], p["commercial_months"])),
        outcome(p["registered_months_ago"], p["cover_months"]),
    )


def oracle_train_timetable(p):
    def earliest(ready_at):
        t = min(d for d in p["departures"] if d >= ready_at)
        return f"The {t // 60:02d}:{t % 60:02d} train"

    return (
        earliest(p["arrival_actual"]),
        earliest(p["arrival_actual"] + p["min_change"]),
        earliest(p["arrival_scheduled"]),
    )


def oracle_grant_budget(p):
    def share(pot):
        x = Fraction(pot) * p["staff"][p["target"]] / sum(p["staff"])
        assert x.denominator == 1
        return f"{x.numerator:,}"

    after_reserve = Fraction(p["budget"]) * (100 - p["reserve_pct"]) / 100
    equal = Fraction(p["budget"], 3)
    assert equal.denominator == 1
    return share(p["budget"]), share(after_reserve), f"{equal.numerator:,}"


def oracle_sensor_log(p):
    raw = [t for t, _s in p["readings"]]
    corrected = [t - p["offset"] if s == p["faulty"] else t for t, s in p["readings"]]
    return (
        _days(sum(t > p["limit"] for t in raw)),
        _days(sum(t > p["limit"] for t in corrected)),
        _days(sum(t >= p["limit"] for t in raw)),
    )


def oracle_parcel_sorting(p):
    low, high = p["limits"]

    def belt(kg):
        assert kg not in (low, high), "weight on a boundary"
        return 1 if kg < low else 2 if kg < high else 3

    changed = 4 if p["special_handling"] else belt(p["weight"])
    return tuple(f"Belt {b}" for b in (belt(p["weight"]), changed, belt(p["volumetric_weight"])))


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
        expected = dict(zip(("default", "changed", "misleading"), ORACLES[family](item.params)))
        for role, text in expected.items():
            assert item.options[item.role_index[role]] == text, (item.item_id, role, item.params)
        # The changing section must really change the answer, and the misleading
        # answer must be wrong in both versions.
        assert len(set(expected.values())) == 3, (item.item_id, expected)
        assert item.correct_label("default_correct") == item.label("default")
        assert item.correct_label("default_wrong") == item.label("changed")
        assert item.label("misleading") not in {item.correct_label(v) for v in VERSIONS}


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
