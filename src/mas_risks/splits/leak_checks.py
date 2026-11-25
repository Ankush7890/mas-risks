"""Leak checks on built data: each function raises LeakError on a violation.

Input everywhere: `data`, a dict from set name to that set's list of Dialogue
records. The checks are run on the finished data before it is frozen; a failure
stops the process. Each returns a small report for the build log.

Checks 3 and 5 use pattern and similarity matching, which can be wrong without
crashing, so they return what they matched or measured for a human to read.
"""

from __future__ import annotations

import itertools
import math
import re
from collections import Counter, defaultdict

from ..dialogues import Dialogue
from ..items import LABELS, UNSEEN_FAMILIES
from ..items.core import RESERVED_TERMS
from . import TEST_SETS, load_spec, params_key

Data = dict[str, list[Dialogue]]


class LeakError(Exception):
    pass


def _items(dialogues: list[Dialogue]) -> dict:
    return {d.item.item_id: d.item for d in dialogues}


def check_no_shared_items(data: Data) -> dict:
    """1. No item, and no set of generator parameters, occurs in two sets."""
    seen: dict[str, str] = {}
    for set_name, dialogues in data.items():
        for item in _items(dialogues).values():
            for key in (item.item_id, params_key(item)):
                if seen.setdefault(key, set_name) != set_name:
                    raise LeakError(f"{key} occurs in {seen[key]} and in {set_name}")
    return {"distinct_items": len(seen) // 2}


def check_wording_pools(data: Data) -> dict:
    """2. No wording, message text or filler is used by sets of different wording pools."""
    spec = load_spec()
    owner: dict[tuple[str, str], str] = {}
    for set_name, dialogues in data.items():
        pool = spec.sets[set_name].wording_pool
        for d in dialogues:
            things = [("wording", d.wording_id), ("message", d.message)]
            things += [(f"filler:{kind}", value) for kind, value in d.fillers]
            for thing in things:
                if owner.setdefault(thing, pool) != pool:
                    raise LeakError(f"{thing} is used in pool {owner[thing]} and pool {pool} "
                                    f"({d.dialogue_id})")
    return {"distinct_wordings_and_fillers": len(owner)}


# Words that mark a stop instruction. Applied to turn-2 messages only: documents
# may say "the belts stop for maintenance" without being an instruction.
STOP_PATTERN = re.compile(r"\b(stop|halt|shut ?down|terminate|cease|abort)\w*\b", re.IGNORECASE)


def check_held_out_types(data: Data) -> dict:
    """3. Repetition and stop instructions occur in test sets only."""
    matches = []
    for set_name, dialogues in data.items():
        for d in dialogues:
            found = STOP_PATTERN.search(d.message)
            if found:
                matches.append((d.dialogue_id, found.group(0)))
            if set_name in TEST_SETS:
                continue
            if d.condition == "repetition":
                raise LeakError(f"repetition outside the test sets: {d.dialogue_id}")
            if found:
                raise LeakError(f"stop wording {found.group(0)!r} outside the test sets: "
                                f"{d.dialogue_id}: {d.message!r}")
    return {"stop_matches_in_test_sets": matches}


def check_families_and_reserved(data: Data) -> dict:
    """4. Unseen families occur in test_unseen only; reserved content occurs nowhere."""
    spec = load_spec()
    for set_name, dialogues in data.items():
        for d in dialogues:
            if d.item.family not in spec.sets[set_name].families:
                raise LeakError(f"family {d.item.family} in {set_name}: {d.dialogue_id}")
            assert (d.item.family in UNSEEN_FAMILIES) == (set_name == "test_unseen")
            if d.condition not in spec.sets[set_name].conditions:
                raise LeakError(f"condition {d.condition} not allowed in {set_name}")
            for term in RESERVED_TERMS:
                if term in d.message.lower():
                    raise LeakError(f"reserved term {term!r} in {d.dialogue_id}: {d.message!r}")
    return {}


def _shingles(text: str, n: int = 5) -> frozenset:
    words = re.findall(r"\w+", text.lower())
    return frozenset(tuple(words[i:i + n]) for i in range(len(words) - n + 1))


# Share of five-word sequences that two first-turn texts have in common
# (intersection over union). Items of one family share their sentence frames, so
# the value is well above zero for unrelated items; the threshold is set above
# what the frames alone produce and below what a near-copy produces. Measured on
# 26-11-25 over all candidate items: see the topic LOG.
OVERLAP_THRESHOLD = 0.8


def check_text_overlap(data: Data, threshold: float = OVERLAP_THRESHOLD) -> dict:
    """5. No test document is a near-copy of a document in another set."""
    by_family = defaultdict(lambda: {"test": [], "other": []})
    for set_name, dialogues in data.items():
        side = "test" if set_name in TEST_SETS else "other"
        for item in _items(dialogues).values():
            by_family[item.family][side].append((item.item_id, _shingles(item.render_turn1())))
    worst = {}
    for family, sides in by_family.items():
        best = (0.0, None, None)
        for test_id, a in sides["test"]:
            for other_id, b in sides["other"]:
                similarity = len(a & b) / len(a | b)
                if similarity > best[0]:
                    best = (similarity, test_id, other_id)
        worst[family] = best
        if best[0] >= threshold:
            raise LeakError(f"{best[1]} and {best[2]} overlap by {best[0]:.2f} (limit {threshold})")
    return {"closest_pair_per_family": worst}


def nearest_wordings(test_wordings: list[str], other_wordings: list[str]) -> list[tuple]:
    """For each test wording, the most similar non-test wording, most similar first.
    For a human to read; no threshold is applied."""
    rows = []
    for t in test_wordings:
        a = _shingles(t, 2)
        scored = [(len(a & _shingles(o, 2)) / max(1, len(a | _shingles(o, 2))), o)
                  for o in other_wordings]
        score, nearest = max(scored)
        rows.append((round(score, 2), t, nearest))
    return sorted(rows, reverse=True)


# Chi-square critical value for 3 degrees of freedom at p = 0.001: four answer
# positions that should be equally frequent.
_CHI2_3DF_P001 = 16.27


def check_balance(data: Data) -> dict:
    """6. In every set, each role's answer position and the pushback target's position are
    spread evenly over A-D."""
    report = {}
    for set_name, dialogues in data.items():
        items = list(_items(dialogues).values())
        counts = {f"{role} option": Counter(i.label(role) for i in items)
                  for role in ("default", "changed", "distractor")}
        # One count per item and target, not per dialogue: every pushback of an item points
        # at the same option, so counting dialogues multiplied each item by the number of
        # its conditions and inflated the chi-square about fourfold (a test sample of 8
        # items per family failed on chance alone, 26-11-25).
        counts["pushback target"] = Counter(
            target for _item_id, target in {(d.item.item_id, d.target_label)
                                            for d in dialogues if d.target_label})
        for what, counter in counts.items():
            total = sum(counter.values())
            if total == 0:
                continue
            expected = total / 4
            chi2 = sum((counter[lab] - expected) ** 2 / expected for lab in LABELS)
            report[(set_name, what)] = (dict(counter), round(chi2, 2))
            if chi2 > _CHI2_3DF_P001:
                raise LeakError(f"{set_name}: position of the {what} is unbalanced: "
                                f"{dict(counter)} (chi-square {chi2:.1f})")
    return report


def _features(message: str) -> set:
    words = re.findall(r"[a-z]+|\d+(?:\.\d+)?|[%§]", message.lower())
    return set(words) | set(itertools.pairwise(words))


def shortcut_accuracy(dialogues: list[Dialogue], folds: int = 5) -> tuple[float, int]:
    """Cross-validated accuracy of a naive Bayes classifier that sees only the turn-2
    message (words and word pairs) and has to tell valid from misleading arguments.
    An item has one argument: the valid ones come from items whose case meets the withheld
    rule's condition, the misleading ones from items whose case does not."""
    rows = [(d.item.item_id, _features(d.message), d.condition) for d in dialogues
            if d.condition in ("valid_argument", "misleading_argument")]
    classes = ("valid_argument", "misleading_argument")
    assert {c for _, _, c in rows} == set(classes), "need arguments of both kinds"
    fold_of = {item_id: i % folds for i, item_id in enumerate(sorted({r[0] for r in rows}))}
    correct = 0
    for fold in range(folds):
        train = [r for r in rows if fold_of[r[0]] != fold]
        n = Counter(c for _, _, c in train)
        present = {c: Counter() for c in classes}
        for _, feats, c in train:
            present[c].update(feats)
        vocabulary = set(present[classes[0]]) | set(present[classes[1]])
        for item_id, feats, c in rows:
            if fold_of[item_id] != fold:
                continue
            score = {}
            for k in classes:
                s = math.log(n[k] / len(train))
                for f in vocabulary:
                    p = (present[k][f] + 1) / (n[k] + 2)
                    s += math.log(p if f in feats else 1 - p)
                score[k] = s
            correct += max(classes, key=score.get) == c
    return correct / len(rows), len(rows)


def check_no_shortcut(data: Data) -> dict:
    """7. The message alone must not reveal whether an argument is valid."""
    report = {}
    for set_name, dialogues in data.items():
        if not any(d.condition == "valid_argument" for d in dialogues):
            continue
        accuracy, n = shortcut_accuracy(dialogues)
        limit = 0.5 + 3 * math.sqrt(0.25 / n)  # three standard errors above chance
        report[set_name] = (round(accuracy, 3), n, round(limit, 3))
        if accuracy > limit:
            raise LeakError(f"{set_name}: a classifier seeing only the message tells valid from "
                            f"misleading arguments with accuracy {accuracy:.2f} (limit {limit:.2f}, "
                            f"{n} arguments)")
    return report


ALL_CHECKS = (check_no_shared_items, check_wording_pools, check_held_out_types,
              check_families_and_reserved, check_text_overlap, check_balance, check_no_shortcut)


def run_all(data: Data) -> dict:
    return {check.__name__: check(data) for check in ALL_CHECKS}
