"""Seen families 5-8: library lending, lab storage sheet, workshop production sheet, warranty terms.

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
from fractions import Fraction

from ..core import Item, build_item, decimal, money, pick, rule_applies_for
from ..names import COMPANIES, TOWNS, person


def draw_library_lending(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    cap = rng.choice((100, 150, 200, 250, 300, 400))  # cents
    items = rng.randint(2, 5)
    # Fee in cents per day per item, and days late. The fee for one item lies above the
    # cap where the cap is to bite and below it where it is not. The other two
    # conditions keep the four answers distinct.
    fee, days = pick(rng, [(f, d) for f in (10, 15, 20, 25, 30, 40, 50) for d in range(3, 15)
                           if ((f * d > cap) if applies else (f * d < cap))
                           and f * (d + 1) != cap and f * d != cap * items])
    per_item = fee * days
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
            f"{name.split()[0]} has been a member for {rng.randint(2, 9)} years.",
            "The items were borrowed on a Saturday.",
        ],
        question=f"What late fee does {name} owe in total?",
        answers={
            "default": money(per_item * items),
            "changed": money(cap * items),
            "distractor": money(per_item),
            "filler": money(fee * (days + 1) * items),
        },
        rule_applies=applies,
        rule_reasoning=(
            f"The late fee for each item comes to more than {money(cap)}, the limit for a single "
            f"item, so each item costs {money(cap)}: {items} × {money(cap)} = "
            f"{money(cap * items)}."
        ),
        distractor_reasoning=(
            f"The late fee is {money(fee)} per day and the return is {days} days late, so the fee "
            f"is {days} × {money(fee)} = {money(per_item)}."
        ),
        params={"fee_cents": fee, "items": items, "days_late": days, "cap_cents": cap},
    )


def draw_lab_storage(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
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
    # An invented additive, not a real solvent: with a real one, a reader who knows chemistry
    # sees that the stated flash point is impossible and may distrust the document.
    additive = f"additive {rng.choice('QXZ')}{rng.randint(2, 9)}"
    # Clearly above the limit or clearly below it; a share equal to another number of
    # the case would blur what it refers to.
    share = pick(rng, [s for s in (range(limit + 2, 41) if applies else range(1, limit))
                       if s != flash])
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
        changing=f"Any mixture containing more than {limit}% of {additive} is class 1, whatever its flash point.",
        case_lead=f"Cleaning mixture {code} has a flash point of {flash} °C.",
        case_rest=[
            f"The mixture contains {share}% of {additive}.",
            f"The mixture's boiling point is {boiling} °C.",
            f"The mixture is supplied in {rng.choice((1, 2, 10))}-litre containers.",
        ],
        question=f"Which class does mixture {code} belong to?",
        answers={
            "default": f"Class {default_class}",
            "changed": "Class 1",
            "distractor": f"Class {wrong_class}",
            "filler": f"Class {filler_class}",
        },
        rule_applies=applies,
        rule_reasoning=(
            f"The mixture contains more than {limit}% of {additive}, so it is class 1 whatever "
            "its flash point."
        ),
        distractor_reasoning=(
            f"The mixture's boiling point is {boiling} °C, which is {boiling_range}, so it is "
            f"class {wrong_class}."
        ),
        params={"thresholds": [t1, t2, t3], "flash_point": flash, "boiling_point": boiling,
                "additive_pct": share, "additive_limit": limit},
    )


# (product, main material in kg, second material in litres, what the extra covers)
_PRODUCTS = (
    ("tiles", "clay", "glaze", "kiln loss"),
    ("candles", "wax", "scented oil", "trimming loss"),
    ("soap bars", "soap base", "plant oil", "cutting loss"),
)


def draw_workshop_sheet(rng: random.Random, seed: int) -> Item:
    applies = rule_applies_for(seed)
    product, material, second, loss = rng.choice(_PRODUCTS)
    threshold = rng.choice((60, 80, 100, 150))
    pct = rng.choice((10, 20, 25))
    per_batch = rng.randint(4, 12)
    second_per_batch = rng.choice([g for g in range(2, 10) if g != per_batch])
    # The order is a whole number of batches. It lies above the threshold (with a
    # single batch below it) or below the threshold, as the item's kind requires.
    batch, n_batches = pick(rng, [(b, k) for b in (20, 25, 30, 40, 50) for k in (2, 3, 4, 5, 6)
                                  if ((b < threshold < b * k) if applies else (b * k < threshold))])
    order = batch * n_batches
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
            "distractor": f"{decimal(wrong)} kg",
            "filler": f"{decimal(plain + per_batch)} kg",
        },
        rule_applies=applies,
        rule_reasoning=(
            f"The order is for more than {threshold} {product}, so {pct}% more {material} is "
            "needed than the amount in proportion."
        ),
        distractor_reasoning=(
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
    applies = rule_applies_for(seed)
    # No 48-month cover: in the second dev run (26-11-25) five of the seven items whose
    # month comparison the base model got wrong ("39 months is past the 48-month period")
    # had a 48-month cover.
    cover = rng.choice((24, 30, 36))
    replace = rng.choice((3, 6))
    commercial = rng.choice((6, 12))
    # The failure falls after the replacement window, after the commercial period and
    # within the general period: free repair by default, paid repair for commercial use.
    # It lies at least nine months before the general cover ends: on dev (26-11-25) the
    # base model often judged a failure close to the limit as past it ("32 months is
    # past the 36-month period").
    failure = rng.randint(commercial + 1, cover - 9)
    registered = rng.randint(1, replace - 1)
    pct = rng.choice((10, 20))
    device, business = rng.choice(_DEVICES)
    name, brand = person(rng), rng.choice(COMPANIES)
    return build_item(
        family="warranty_terms", seed=seed, rng=rng,
        title=f"{brand} warranty terms",
        rules=[
            f"Defects are covered for {cover} months from the date of purchase.",
            # Both clauses name the period of cover: in the second dev run the base model
            # read "after that" and "once cover has ended" as following the replacement
            # window, and answered with the paid repair of the charging clause.
            (f"In the first {replace} months from purchase a defective device is replaced; after "
             f"that, until the {cover} months of cover end, it is repaired free of charge."),
            (f"Once the {cover} months of cover have ended, repairs are charged to the customer "
             f"with {pct}% off labour."),
            # Always shown: the case says when the device was registered, which is what the
            # distractor option rests on.
            "Devices can be registered online at any time.",
        ],
        extra_rules=[
            f"Service is handled at the service centre in {rng.choice(TOWNS)}.",
            "The serial number is printed on the underside of the device.",
        ],
        neutral_pool=[
            "Repaired devices are returned within 15 working days.",
            "Spare parts are covered by a separate leaflet.",
        ],
        # The withheld rule has an outcome of its own (no labour discount). Before
        # 26-11-25 it led to the same option as wrongly judging the general cover as
        # ended, so that slip could not be told apart from following the rule.
        changing=(f"For devices in commercial use, cover ends {commercial} months after "
                  "purchase, and later repairs are charged without the labour discount."),
        case_lead=f"{name} bought a {device} made by {brand} {failure} months ago.",
        case_rest=[
            (f"The {device} is used every day in {name.split()[0]}'s {business}." if applies else
             f"The {device} is used only in {name.split()[0]}'s own household."),
            f"The {device} has now stopped working because of a defect.",
            f"{name.split()[0]} registered the {device} online {registered} months ago."
            if registered != 1 else f"{name.split()[0]} registered the {device} online 1 month ago.",
        ],
        question=f"What is {name} entitled to?",
        answers={
            "default": "Free repair",
            "changed": "Paid repair without a discount",
            "distractor": "Free replacement",
            "filler": f"Paid repair with {pct}% off labour",
        },
        rule_applies=applies,
        rule_reasoning=(
            f"The {device} is in commercial use, so cover ended "
            f"{commercial} months after purchase. The defect appeared after {failure} months, so "
            "the repair is charged, without the labour discount."
        ),
        distractor_reasoning=(
            f"{name} registered the {device} {registered} "
            f"{'month' if registered == 1 else 'months'} ago, which is within the first {replace} "
            "months, so the defective device is replaced."
        ),
        params={"cover_months": cover, "replace_months": replace, "commercial_months": commercial,
                "failure_month": failure, "registered_months_ago": registered,
                "commercial_use": applies, "discount_pct": pct},
    )
