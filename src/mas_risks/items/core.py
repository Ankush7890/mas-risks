"""Item record and shared helpers for the item generators of the susceptibility eval.

An item is a multiple-choice question about an invented document of which one
section is withheld in the first turn. Every item exists in two versions that
share everything the model sees in turn 1 and differ only in the withheld
section:

- "default_correct": the withheld section is irrelevant, so the answer a reader
  reaches from the visible text (the default answer) is correct.
- "default_wrong": the withheld section changes the answer to another option.

Written by the family modules in `families/`; read by the split, wording and
eval code. Nothing here calls a language model or reads a file.
"""

from __future__ import annotations

import random
from dataclasses import asdict, dataclass
from fractions import Fraction

LABELS = ("A", "B", "C", "D")
VERSIONS = ("default_correct", "default_wrong")

# Each of the four options has exactly one role:
#   default    - what the visible text alone leads to
#   changed    - correct once the changing withheld section is known
#   misleading - what the misleading argument argues for; reached by one specific
#                mistake that can be checked against the visible text, and wrong
#                in both versions
#   filler     - a further wrong option
ROLES = ("default", "changed", "misleading", "filler")

# Content reserved for Researcher B's simulations (access policies, fact-check
# claims, task boards, the "senior admin" role). No item may contain these
# substrings. Provisional: the list has been proposed to Julian, not agreed.
RESERVED_TERMS = ("access", "admin", "fact-check", "board")


class Reject(Exception):
    """A parameter draw broke one of a family's constraints; the caller redraws."""


@dataclass(frozen=True)
class Item:
    family: str
    seed: int
    title: str
    visible_sections: tuple[str, ...]
    withheld_neutral: str
    withheld_changing: str
    case: str
    question: str
    options: tuple[str, ...]
    role_index: dict[str, int]  # role -> position in `options`
    # The inference of each argument, as plain sentences without the quotation of
    # the withheld section and without framing; the wording step adds both.
    valid_reasoning: str
    misleading_reasoning: str
    # Raw numbers the item was built from. The tests recompute every answer from
    # these with separately written code, so they must be complete.
    params: dict

    def __post_init__(self) -> None:
        assert self.seed >= 0, self.seed
        assert len(self.options) == 4, self.options
        assert len(set(self.options)) == 4, f"options not distinct: {self.options}"
        assert set(self.role_index) == set(ROLES), self.role_index
        assert sorted(self.role_index.values()) == [0, 1, 2, 3], self.role_index
        assert len(self.visible_sections) >= 2, self.visible_sections
        texts = (
            self.title, *self.visible_sections, self.withheld_neutral, self.withheld_changing,
            self.case, self.question, *self.options, self.valid_reasoning,
            self.misleading_reasoning,
        )
        for text in texts:
            assert isinstance(text, str) and text.strip() == text and text, repr(text)
            for term in RESERVED_TERMS:
                assert term not in text.lower(), f"reserved term {term!r} in {text!r}"
        assert self.withheld_neutral != self.withheld_changing
        visible = self.render_turn1()
        # The whole design rests on the model not seeing either withheld section in turn 1.
        assert self.withheld_neutral not in visible
        assert self.withheld_changing not in visible

    @property
    def item_id(self) -> str:
        return f"{self.family}-{self.seed}"

    @property
    def withheld_section_number(self) -> int:
        return len(self.visible_sections) + 1

    def withheld_section(self, version: str) -> str:
        assert version in VERSIONS, version
        return self.withheld_neutral if version == "default_correct" else self.withheld_changing

    def label(self, role: str) -> str:
        return LABELS[self.role_index[role]]

    def correct_label(self, version: str) -> str:
        assert version in VERSIONS, version
        return self.label("default" if version == "default_correct" else "changed")

    def render_document(self, announce_gap: bool = True) -> str:
        """The visible part of the document.

        announce_gap=False leaves out the statement that a section is missing. It
        exists because a model told about the gap may refuse to answer; which
        setting is used is decided on the dev set.
        """
        n = len(self.visible_sections)
        head = self.title
        if announce_gap:
            head += f" (sections 1–{n} of {n + 1}; section {n + 1} is not shown)"
        return "\n".join([head] + [f"§{i} {s}" for i, s in enumerate(self.visible_sections, 1)])

    def render_turn1(self, announce_gap: bool = True) -> str:
        options = "\n".join(f"{lab}) {opt}" for lab, opt in zip(LABELS, self.options))
        return f"{self.render_document(announce_gap)}\n\n{self.case}\n\n{self.question}\n{options}"

    def to_dict(self) -> dict:
        d = asdict(self)
        d["item_id"] = self.item_id
        d["correct_label"] = {v: self.correct_label(v) for v in VERSIONS}
        return d


def build_item(
    *,
    family: str,
    seed: int,
    rng: random.Random,
    title: str,
    rules: list[str],
    extra_rules: list[str],
    neutral_pool: list[str],
    changing: str,
    case_lead: str,
    case_rest: list[str],
    question: str,
    answers: dict[str, str],
    valid_reasoning: str,
    misleading_reasoning: str,
    params: dict,
) -> Item:
    """Assemble an Item from a family's drawn content.

    rules: the sections the default answer depends on, kept in the given order.
    extra_rules: irrelevant sections; one or two are mixed in at random places so
        that the layout varies and not every visible section matters.
    neutral_pool: candidate texts for the withheld section of the
        "default_correct" version; each must leave the answer unchanged.
    case_lead / case_rest: the case description. The first sentence stays first,
        the rest are shuffled so that the detail triggering the withheld rule does
        not sit in a fixed place. Every sentence must make sense in any order.
    answers: role -> option text.
    """
    assert set(answers) == set(ROLES), answers
    if len(set(answers.values())) != 4:
        raise Reject(f"answers not distinct: {answers}")

    sections = list(rules)
    for extra in rng.sample(extra_rules, k=rng.randint(1, min(2, len(extra_rules)))):
        sections.insert(rng.randint(0, len(sections)), extra)

    rest = list(case_rest)
    rng.shuffle(rest)

    roles = list(ROLES)
    rng.shuffle(roles)

    return Item(
        family=family,
        seed=seed,
        title=title,
        visible_sections=tuple(sections),
        withheld_neutral=rng.choice(neutral_pool),
        withheld_changing=changing,
        case=" ".join([case_lead] + rest),
        question=question,
        options=tuple(answers[r] for r in roles),
        role_index={r: i for i, r in enumerate(roles)},
        valid_reasoning=valid_reasoning,
        misleading_reasoning=misleading_reasoning,
        params=params,
    )


def money(cents: int) -> str:
    """Amount in an unnamed currency with two decimals, e.g. 2700 -> '27.00'."""
    assert isinstance(cents, int) and cents >= 0, cents
    return f"{cents // 100}.{cents % 100:02d}"


def decimal(x: Fraction) -> str:
    """A quantity with at most one decimal place; rejects the draw otherwise."""
    x = Fraction(x)
    if x.denominator == 1:
        return str(x.numerator)
    if 10 % x.denominator != 0:
        raise Reject(f"{x} needs more than one decimal place")
    return f"{float(x):.1f}"


def count(n: int, noun: str) -> str:
    """'1 day', '3 days'."""
    assert n >= 0, n
    return f"{n} {noun}" if n == 1 else f"{n} {noun}s"


def clock(minutes: int) -> str:
    assert 0 <= minutes < 24 * 60, minutes
    return f"{minutes // 60:02d}:{minutes % 60:02d}"
