"""Append-only record of everything agents said in one run.

The transcript is the only conversation state in a run: agents keep no memory,
and every agent's context is rebuilt from the transcript by the scenario's
`build_context`. Written by the runner, read by scenarios.
"""

from collections.abc import Iterator
from dataclasses import dataclass

from pydantic import BaseModel


@dataclass(frozen=True)
class Message:
    """One agent turn.

    round, step: position in the schedule (step index is global within the run).
    sender: agent id.
    raw: the agent's text output, exactly as returned.
    parsed: the same output validated against the agent's output schema.

    Deliberately no `visible_to` field: who sees a message is decided only by the
    scenario's `build_context`, so visibility lives in one place.
    """

    round: int
    step: int
    sender: str
    raw: str
    parsed: BaseModel

    def ref(self) -> tuple[int, int, str]:
        return (self.round, self.step, self.sender)

    def parsed_as[T: BaseModel](self, schema: type[T]) -> T:
        """`parsed`, checked to be an instance of `schema` (typed access to its fields)."""
        assert isinstance(self.parsed, schema), f"{self.sender}'s output is {type(self.parsed)}, not {schema}"
        return self.parsed


class Transcript:
    """Append-only list of Messages, ordered by (step, order of agents within the step)."""

    def __init__(self) -> None:
        self._messages: list[Message] = []

    def append(self, msg: Message) -> None:
        assert isinstance(msg, Message), type(msg)
        if self._messages:
            assert msg.step >= self._messages[-1].step, (
                f"transcript is append-only in step order: got step {msg.step} after step {self._messages[-1].step}"
            )
        self._messages.append(msg)

    def __iter__(self) -> Iterator[Message]:
        return iter(tuple(self._messages))

    def __len__(self) -> int:
        return len(self._messages)

    def by_sender(self, sender: str) -> list[Message]:
        return [m for m in self._messages if m.sender == sender]

    def in_step(self, step: int) -> list[Message]:
        return [m for m in self._messages if m.step == step]

    def before_step(self, step: int) -> list[Message]:
        return [m for m in self._messages if m.step < step]

    def last_from(self, sender: str) -> Message:
        msgs = self.by_sender(sender)
        assert msgs, f"no message from {sender!r} in transcript"
        return msgs[-1]

    def last_parsed[T: BaseModel](self, sender: str, schema: type[T]) -> T:
        return self.last_from(sender).parsed_as(schema)
