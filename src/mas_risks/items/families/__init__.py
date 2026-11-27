"""The item families: eight seen in training, four reserved for the test-unseen set, and the
families of plan 18b (UNSEEN_B), reserved for dev_b and test_unseen_b."""

from .seen_a import draw_delivery_terms, draw_league_rules, draw_leave_policy, draw_print_shop
from .seen_b import (
    draw_lab_storage,
    draw_library_lending,
    draw_warranty_terms,
    draw_workshop_sheet,
)
from .unseen import draw_grant_budget, draw_parcel_sorting, draw_sensor_log, draw_train_timetable

SEEN = {
    "leave_policy": draw_leave_policy,
    "delivery_terms": draw_delivery_terms,
    "print_shop": draw_print_shop,
    "league_rules": draw_league_rules,
    "library_lending": draw_library_lending,
    "lab_storage": draw_lab_storage,
    "workshop_sheet": draw_workshop_sheet,
    "warranty_terms": draw_warranty_terms,
}
UNSEEN = {
    "train_timetable": draw_train_timetable,
    "grant_budget": draw_grant_budget,
    "sensor_log": draw_sensor_log,
    "parcel_sorting": draw_parcel_sorting,
}

# Plan 18b. Filled in by unseen_b*.py; see docs/plan_18b_families_samples.md.
UNSEEN_B: dict = {}
