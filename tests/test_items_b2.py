"""Independent oracles for ten of the families_b item families.

Written only from the plain-language specs in docs/families_b/specs/, without
reading the generators. Each oracle recomputes from `item.params`, by step-by-step
simulation where possible:
  default    - the option text reached from the visible text
  changed    - the option text reached by applying the withheld changing rule
  applies    - whether the case meets the changing rule's condition
  distractor - the option text reached by the family's documented mistake
"""

import itertools
from datetime import date, timedelta
from fractions import Fraction

import pytest

from mas_risks.items import generate

N_SEEDS = 300
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]


def _money(cents) -> str:
    cents = Fraction(cents)
    assert cents.denominator == 1, f"amount {cents} is not a whole number of cents"
    c = int(cents)
    assert c >= 0
    return f"{c // 100}.{c % 100:02d}"


def _clock(minutes: int) -> str:
    assert 0 <= minutes < 24 * 60
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def _day_month(d: date) -> str:
    return f"{d.day} {MONTHS[d.month - 1]}"


def _plural(n: int, noun: str) -> str:
    return f"{n} {noun}" if n == 1 else f"{n} {noun}s"


# --- paint_estimate ---------------------------------------------------------

def oracle_paint_estimate(p):
    def tins(area):
        # Open tins one at a time until the paint covers the area.
        n, covered = 0, 0
        while covered < area:
            n += 1
            covered += p["tin_coverage_m2"]
        return n

    net = p["gross_area_m2"]
    for _door in range(p["doors"]):
        net -= p["door_area_m2"]
    for _window in range(p["windows"]):
        net -= p["window_area_m2"]
    assert p["door_area_m2"] == 2
    one_coat = tins(net)
    two_coats = tins(net + net)
    applies = p["current_colour"] in p["two_coat_colours"]
    return (_plural(one_coat, "tin"), _plural(two_coats, "tin"), applies,
            _plural(tins(p["gross_area_m2"]), "tin"))


# --- pallet_stacking --------------------------------------------------------

def oracle_pallet_stacking(p):
    positions = 0
    for _row in range(p["rows"]):
        positions += p["per_row"]
    # Stack whole pallets while the next one still stays within the height limit.
    layers, height = 0, 0
    while height + p["pallet_height_dm"] <= p["height_limit_dm"]:
        height += p["pallet_height_dm"]
        layers += 1
    assert height != p["height_limit_dm"], "exact fit"
    weight = p["empty_pallet_kg"] + sum(p["carton_kg"] for _c in range(p["cartons"]))
    assert weight != p["max_stack_kg"]
    applies = weight > p["max_stack_kg"]
    fmt = lambda n: _plural(n, "pallet")
    return fmt(positions * layers), fmt(positions), applies, fmt(positions * (layers + 1))


# --- parking_charges --------------------------------------------------------

def oracle_parking_charges(p):
    # Charge each hour that has started.
    started, elapsed = 0, 0
    while elapsed < p["duration_minutes"]:
        started += 1
        elapsed += 60
    full = p["duration_minutes"] // 60
    assert p["duration_minutes"] % 60 != 0
    entry = p["entry_minutes"]
    exit_ = entry + p["duration_minutes"]
    assert entry != 18 * 60
    applies = entry > 18 * 60
    if applies:
        # Stay must end before 08:00 the next morning for the flat rate to cover it.
        assert exit_ <= 24 * 60 + 8 * 60
    return (_money(started * p["rate_cents"]), _money(p["evening_cents"]), applies,
            _money(full * p["rate_cents"]))


# --- pool_guest_passes ------------------------------------------------------

def oracle_pool_guest_passes(p):
    visit = date.fromisoformat(p["visit_date"])
    assert WEEKDAYS[visit.weekday()] == p["no_guest_weekday"]
    morning_ban = p["visit_minutes"] < 12 * 60
    assert not morning_ban
    earlier = [date.fromisoformat(d) for d in p["this_month_dates"] + p["previous_month_dates"]]
    m = sum(1 for d in earlier if (d.year, d.month) == (visit.year, visit.month) and d < visit)
    visit_number = m + 1
    applies = visit_number > p["quota"]
    return ("Yes, and the guest swims free of charge",
            f"Yes, but the guest pays {_money(p['fee_cents'])}",
            applies,
            f"No, guests are not allowed on {p['no_guest_weekday']}s")


# --- returns_window ---------------------------------------------------------

def oracle_returns_window(p):
    purchase = date.fromisoformat(p["purchase_date"])
    # Count days after the purchase day.
    last = purchase
    for _day in range(p["return_days"]):
        last += timedelta(days=1)
    start, end = date.fromisoformat(p["sale_start"]), date.fromisoformat(p["sale_end"])
    extended = date.fromisoformat(p["extended_until"])
    applies = start <= purchase <= end
    assert extended > last
    return (_day_month(last), _day_month(extended), applies,
            _day_month(last - timedelta(days=1)))


# --- seed_lot_grading -------------------------------------------------------

GRADES = ["Grade A", "Grade B", "Grade C", "Rejected"]


def _seed_grade(pct) -> int:
    if pct >= 90:
        return 0
    if pct >= 80:
        return 1
    if pct >= 70:
        return 2
    return 3


def oracle_seed_lot_grading(p):
    pct = Fraction(p["germinated"] * 100, p["tested"])
    assert pct.denominator == 1
    grade = _seed_grade(pct)
    lowered = min(grade + 1, 3)
    assert p["moisture_tenths"] != 10 * p["max_moisture_pct"]
    applies = p["moisture_tenths"] > 10 * p["max_moisture_pct"]
    return GRADES[grade], GRADES[lowered], applies, GRADES[_seed_grade(p["purity_pct"])]


# --- tide_departure ---------------------------------------------------------

def oracle_tide_departure(p):
    heights = p["heights_tenths"]
    assert all(a < b for a, b in itertools.pairwise(heights))

    def first_time(needed):
        for i, h in enumerate(heights):
            if h >= needed:
                return _clock(p["start_minutes"] + p["step_minutes"] * i)
        raise AssertionError("no row high enough")

    d = p["draft_tenths"]
    assert p["engine_hp"] != p["hp_limit"]
    applies = p["engine_hp"] < p["hp_limit"]
    return (first_time(d + p["margin_tenths"]), first_time(d + p["margin_small_engine_tenths"]),
            applies, first_time(d))


# --- translation_rates ------------------------------------------------------

def oracle_translation_rates(p):
    job = p["job_pair"]
    src, tgt = p["pairs"][job]
    # Find the reverse pair in the table by language, not by index.
    reverse = [i for i, pair in enumerate(p["pairs"]) if pair == [tgt, src] or pair == (tgt, src)]
    assert len(reverse) == 1
    rate, rev_rate = p["rates_cents"][job], p["rates_cents"][reverse[0]]

    def invoice(amount):
        return max(amount, p["minimum_cents"])

    base = sum(rate for _w in range(p["words"]))
    rushed = Fraction(base) * (100 + p["rush_pct"]) / 100
    gap = 0
    day, hour = p["order_day"], p["order_hour"]
    while (day, hour) != (p["due_day"], p["due_hour"]):
        hour += 1
        if hour == 24:
            day, hour = day + 1, 0
        gap += 1
        assert gap < 24 * 7
    assert gap not in (47, 48, 49)
    applies = gap < 48
    return (_money(invoice(base)), _money(invoice(rushed)), applies,
            _money(invoice(p["words"] * rev_rate)))


# --- water_tariff -----------------------------------------------------------

def oracle_water_tariff(p):
    def bill(band, standing=True):
        total = p["standing_cents"] if standing else 0
        for m3 in range(1, p["used_m3"] + 1):
            total += p["low_rate_cents"] if m3 <= band else p["high_rate_cents"]
        return total

    applies = len(p["residents"]) >= 5
    assert p["big_household_min"] == 5
    return (_money(bill(p["band_m3"])), _money(bill(p["big_band_m3"])), applies,
            _money(bill(p["band_m3"], standing=False)))


# --- watering_restrictions --------------------------------------------------

def oracle_watering_restrictions(p):
    today = date.fromisoformat(p["today"])
    start = date.fromisoformat(p["start"])
    odd_set, even_set = {0, 2, 4}, {1, 3, 5}

    def parity_set(n):
        return odd_set if n % 2 else even_set

    def next_day(number, with_rule):
        d = today
        for _ in range(30):
            d += timedelta(days=1)
            if with_rule and d >= start:
                new_day = p["new_odd_day"] if number % 2 else p["new_even_day"]
                ok = d.weekday() == new_day
            else:
                ok = d.weekday() in parity_set(number) and d.weekday() != 6
            if ok:
                return d
        raise AssertionError("no watering day")

    assert p["house"] % 2 != p["flat"] % 2
    default = next_day(p["house"], False)
    with_rule = next_day(p["house"], True)
    applies = with_rule != default
    changed_day = p["new_odd_day"] if p["house"] % 2 else p["new_even_day"]
    if applies:
        assert with_rule.weekday() == changed_day
    return (WEEKDAYS[default.weekday()], WEEKDAYS[changed_day], applies,
            WEEKDAYS[next_day(p["flat"], False).weekday()])


ORACLES = {
    "paint_estimate": oracle_paint_estimate,
    "pallet_stacking": oracle_pallet_stacking,
    "parking_charges": oracle_parking_charges,
    "pool_guest_passes": oracle_pool_guest_passes,
    "returns_window": oracle_returns_window,
    "seed_lot_grading": oracle_seed_lot_grading,
    "tide_departure": oracle_tide_departure,
    "translation_rates": oracle_translation_rates,
    "water_tariff": oracle_water_tariff,
    "watering_restrictions": oracle_watering_restrictions,
}


@pytest.mark.parametrize("family", sorted(ORACLES))
def test_oracle_matches_generator(family):
    failures = []
    for seed in range(N_SEEDS):
        item = generate(family, seed)
        default, changed, applies, distractor = ORACLES[family](item.params)
        got = {role: item.options[item.role_index[role]]
               for role in ("default", "changed", "distractor")}
        want = {"default": default, "changed": changed, "distractor": distractor}
        if got != want or applies != item.rule_applies:
            failures.append((seed, want, got, applies, item.rule_applies))
    assert not failures, f"{len(failures)} mismatches, first: {failures[:3]}"
