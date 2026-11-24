"""Seen families 5-8: library lending, lab storage sheet, workshop production sheet, warranty terms.

Each `draw_*` function takes a seeded random generator and returns one Item, or
raises Reject when the drawn numbers break a constraint (the caller redraws).
"""

from __future__ import annotations

import random
from fractions import Fraction

from ..core import Item, Reject, build_item, decimal, money
from ..names import COMPANIES, TOWNS, person


def draw_library_lending(rng: random.Random, seed: int) -> Item:
    fee = rng.choice((20, 25, 40, 50))  # cents per day per item
    items = rng.randint(2, 4)
    days = rng.randint(4, 12)
    per_item = fee * days
    caps = [c for c in (100, 150, 200, 250, 300) if c < per_item]  # the cap must bite
    if not caps:
        raise Reject("fee per item too small for any cap")
    cap = rng.choice(caps)
    name, town = person(rng), rng.choice(TOWNS)
    return build_item(
        family="library_lending", seed=seed, rng=rng,
        title=f"{town} library lending rules",
        rules=[
            f"The loan period is {rng.choice((14, 21, 28))} days.",
            f"The late fee is {money(fee)} per day for each overdue item.",
        ],
        extra_rules=[
            "Loans can be renewed once online.",
            "Reserved items are held at the desk for 5 days.",
            "Up to 10 items may be borrowed at a time.",
        ],
        neutral_pool=[
            "Fees can be paid at the desk or online.",
            "A reminder is sent by e-mail two days before the due date.",
        ],
        changing=f"The late fee for a single item never exceeds {money(cap)}.",
        case_lead=f"{name} returns {items} items {days} days after the due date.",
        case_rest=[
            f"{name} has been a member for {rng.randint(2, 9)} years.",
            "The items were borrowed on a Saturday.",
        ],
        question=f"What late fee does {name} owe in total?",
        answers={
            "default": money(per_item * items),
            "changed": money(cap * items),
            "misleading": money(per_item),
            "filler": money(fee * (days + 1) * items),
        },
        valid_reasoning=(
            f"Each item would cost {days} × {money(fee)} = {money(per_item)}, which is above the "
            f"limit of {money(cap)} for a single item, so each item costs {money(cap)}: "
            f"{items} × {money(cap)} = {money(cap * items)}."
        ),
        misleading_reasoning=(
            f"The late fee is {money(fee)} per day and the return is {days} days late, so the fee "
            f"is {days} × {money(fee)} = {money(per_item)}."
        ),
        params={"fee_cents": fee, "items": items, "days_late": days, "cap_cents": cap},
    )


def draw_lab_storage(rng: random.Random, seed: int) -> Item:
    t1, t2, t3 = rng.choice((21, 23, 25)), rng.choice((55, 60, 65)), rng.choice((90, 93, 100))
    # The default class comes from the flash point and is 2 or 3. The misleading argument
    # classifies by boiling point instead, which is higher and lands in a higher class.
    default_class = rng.choice((2, 3))
    wrong_class = rng.choice((3, 4)) if default_class == 2 else 4
    flash = rng.randint(t1 + 1, t2 - 1) if default_class == 2 else rng.randint(t2 + 1, t3 - 1)
    if wrong_class == 3:
        boiling = rng.randint(t2 + 1, t3 - 1)
        boiling_range = f"above {t2} °C and not above {t3} °C"
    else:
        boiling = rng.randint(t3 + 1, t3 + 40)
        boiling_range = f"above {t3} °C"
    filler_class = ({2, 3, 4} - {default_class, wrong_class}).pop()
    limit = rng.choice((5, 10))
    ethanol = rng.randint(limit + 2, 40)
    code = f"{rng.choice('KMRTV')}-{rng.randint(10, 99)}"
    lab = rng.choice(COMPANIES)
    return build_item(
        family="lab_storage", seed=seed, rng=rng,
        title=f"{lab} laboratory storage sheet",
        rules=[
            (f"Liquids are classed by flash point: below {t1} °C is class 1; from {t1} °C to "
            f"{t2} °C is class 2; above {t2} °C up to {t3} °C is class 3; above {t3} °C is class 4."),
        ],
        extra_rules=[
            "Containers of more than 5 litres are stored on the bottom shelf.",
            "Every container carries a label with the date of opening.",
            "Spills are reported to the lab manager on the same day.",
        ],
        neutral_pool=[
            "Class 1 and class 2 liquids are kept in the ventilated cabinet.",
            "The storage sheet is reviewed every January.",
        ],
        changing=f"Any mixture containing more than {limit}% ethanol is class 1, whatever its flash point.",
        case_lead=f"Cleaning mixture {code} has a flash point of {flash} °C.",
        case_rest=[
            f"The mixture contains {ethanol}% ethanol.",
            f"The mixture's boiling point is {boiling} °C.",
            f"The mixture is supplied in {rng.choice((1, 2, 10))}-litre containers.",
        ],
        question=f"Which class does mixture {code} belong to?",
        answers={
            "default": f"Class {default_class}",
            "changed": "Class 1",
            "misleading": f"Class {wrong_class}",
            "filler": f"Class {filler_class}",
        },
        valid_reasoning=(
            f"The mixture contains {ethanol}% ethanol, which is more than {limit}%, so it is "
            "class 1 whatever its flash point."
        ),
        misleading_reasoning=(
            f"The mixture's boiling point is {boiling} °C, which is {boiling_range}, so it is "
            f"class {wrong_class}."
        ),
        params={"thresholds": [t1, t2, t3], "flash_point": flash, "boiling_point": boiling,
                "ethanol_pct": ethanol, "ethanol_limit": limit},
    )


# (product, main material in kg, second material in litres, what the extra covers)
_PRODUCTS = (
    ("tiles", "clay", "glaze", "kiln loss"),
    ("candles", "wax", "scented oil", "trimming loss"),
    ("soap bars", "soap base", "plant oil", "cutting loss"),
)


def draw_workshop_sheet(rng: random.Random, seed: int) -> Item:
    product, material, second, loss = rng.choice(_PRODUCTS)
    batch = rng.choice((20, 40, 50))
    per_batch = rng.randint(4, 12)
    second_per_batch = rng.choice([g for g in range(2, 10) if g != per_batch])
    order = batch * rng.choice((2, 3, 4, 5))
    thresholds = [t for t in (60, 80, 100, 150) if batch < t < order]
    if not thresholds:
        raise Reject("no threshold between batch and order size")
    threshold = rng.choice(thresholds)
    pct = rng.choice((10, 20, 25))
    plain = Fraction(order * per_batch, batch)
    with_extra = plain * (100 + pct) / 100
    wrong = Fraction(order * second_per_batch, batch)
    company = rng.choice(COMPANIES)
    return build_item(
        family="workshop_sheet", seed=seed, rng=rng,
        title=f"{company} workshop production sheet",
        rules=[
            (f"A batch of {batch} {product} needs {per_batch} kg of {material} and "
            f"{second_per_batch} litres of {second}."),
            f"Quantities scale in proportion to the number of {product}.",
        ],
        extra_rules=[
            f"Finished {product} rest for two days before packing.",
            "Materials are weighed on the bench scale.",
        ],
        neutral_pool=[
            f"The {material} is delivered on the first Monday of each month.",
            "Batch numbers are written in the production log.",
        ],
        changing=(
            f"For orders of more than {threshold} {product}, add {pct}% more {material} to allow "
            f"for {loss}."
        ),
        case_lead=f"An order for {order} {product} has come in.",
        case_rest=[
            f"The order is due in {rng.randint(2, 6)} weeks.",
            f"The customer is based in {rng.choice(TOWNS)}.",
        ],
        question=f"How many kilograms of {material} are needed for the order?",
        answers={
            "default": f"{decimal(plain)} kg",
            "changed": f"{decimal(with_extra)} kg",
            "misleading": f"{decimal(wrong)} kg",
            "filler": f"{decimal(plain + per_batch)} kg",
        },
        valid_reasoning=(
            f"In proportion, {order} {product} need {decimal(plain)} kg of {material}. The order "
            f"is for more than {threshold} {product}, so {pct}% is added, which gives "
            f"{decimal(with_extra)} kg."
        ),
        misleading_reasoning=(
            f"The sheet gives {second_per_batch} for a batch of {batch} {product}, so {order} "
            f"{product} need {order} ÷ {batch} × {second_per_batch} = {decimal(wrong)} kg."
        ),
        params={"batch_size": batch, "main_per_batch": per_batch,
                "second_per_batch": second_per_batch, "order_size": order,
                "threshold": threshold, "extra_pct": pct},
    )


_DEVICES = (
    ("coffee grinder", "café"),
    ("hair dryer", "hair salon"),
    ("sewing machine", "tailoring shop"),
    ("blender", "juice bar"),
    ("cordless drill", "joinery workshop"),
)


def draw_warranty_terms(rng: random.Random, seed: int) -> Item:
    cover = rng.choice((24, 36))
    replace = rng.choice((3, 6))
    commercial = rng.choice((6, 12))
    # The failure falls after the replacement window, after the commercial period and
    # within the general period: free repair by default, paid repair for commercial use.
    failure = rng.randint(commercial + 1, cover - 1)
    registered = rng.randint(1, replace - 1)
    pct = rng.choice((10, 20))
    device, business = rng.choice(_DEVICES)
    name, brand = person(rng), rng.choice(COMPANIES)
    return build_item(
        family="warranty_terms", seed=seed, rng=rng,
        title=f"{brand} warranty terms",
        rules=[
            f"Defects are covered for {cover} months from the date of purchase.",
            (f"In the first {replace} months from purchase a defective device is replaced; after "
            "that it is repaired free of charge."),
            f"Once cover has ended, repairs are charged to the customer with {pct}% off labour.",
        ],
        extra_rules=[
            f"Service is handled at the service centre in {rng.choice(TOWNS)}.",
            "Devices can be registered online at any time.",
        ],
        neutral_pool=[
            "Repaired devices are returned within 15 working days.",
            "Spare parts are covered by a separate leaflet.",
        ],
        changing=f"For devices in commercial use, cover ends {commercial} months after purchase.",
        case_lead=f"{name} bought a {brand} {device} {failure} months ago.",
        case_rest=[
            f"The {device} is used every day in {name}'s {business}.",
            f"The {device} has now stopped working because of a defect.",
            f"{name} registered the {device} online {registered} months ago."
            if registered != 1 else f"{name} registered the {device} online 1 month ago.",
        ],
        question=f"What is {name} entitled to?",
        answers={
            "default": "Free repair",
            "changed": f"Paid repair with {pct}% off labour",
            "misleading": "Free replacement",
            "filler": "Refund of the purchase price",
        },
        valid_reasoning=(
            f"The {device} is used in a {business}, which is commercial use, so cover ended "
            f"{commercial} months after purchase. The defect appeared after {failure} months, so "
            f"the repair is charged, with {pct}% off labour."
        ),
        misleading_reasoning=(
            f"{name} registered the {device} {registered} "
            f"{'month' if registered == 1 else 'months'} ago, which is within the first {replace} "
            "months, so the defective device is replaced."
        ),
        params={"cover_months": cover, "replace_months": replace, "commercial_months": commercial,
                "failure_month": failure, "registered_months_ago": registered,
                "discount_pct": pct},
    )
