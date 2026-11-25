"""The record for one planned eval or training dialogue: an item, a pushback condition and the
turn-2 message. Written by the data-building code; read by the leak checks and the eval harness."""

from __future__ import annotations

from dataclasses import dataclass

from .items import LABELS, Item
from .splits import CONDITIONS, SET_NAMES


@dataclass(frozen=True)
class Dialogue:
    set_name: str
    item: Item
    condition: str
    # None when the model sees the same prompt in both versions of the item, which
    # is the case whenever the message does not cite the withheld section. Such a
    # dialogue is run once, not once per version. The two argument conditions cite
    # the changing section, so they carry the version in which it is in the document.
    version: str | None
    # The option the message pushes toward; None for the neutral control.
    target_label: str | None
    message: str
    # Identifies the wording template (for arguments: the framing template).
    wording_id: str
    # (kind, value) pairs of the fillers used, e.g. ("majority", "4 of 5").
    fillers: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        assert self.set_name in SET_NAMES, self.set_name
        assert self.condition in CONDITIONS, self.condition
        assert self.version is None or self.version in self.item.versions, self.dialogue_id
        assert self.target_label is None or self.target_label in LABELS, self.target_label
        assert (self.target_label is None) == (self.condition == "neutral"), self.dialogue_id
        assert self.message.strip() and self.wording_id, self.dialogue_id
        # Both argument conditions use the same argument, "the withheld rule applies
        # to this case", for the "changed" option. It is valid for an item whose case
        # meets the rule's condition and misleading for one whose case does not, so an
        # item has exactly one of the two conditions.
        if self.condition == "valid_argument":
            assert self.version == "default_wrong", self.dialogue_id
        if self.condition == "misleading_argument":
            assert self.version == "rule_not_met", self.dialogue_id
        if self.condition in ("valid_argument", "misleading_argument"):
            assert self.target_label == self.item.label("changed"), self.dialogue_id

    @property
    def dialogue_id(self) -> str:
        return f"{self.set_name}/{self.item.item_id}/{self.condition}/{self.version or 'both'}"
