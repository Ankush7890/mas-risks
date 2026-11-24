"""Scenario: the experiment-specific part of a run (who speaks when, who sees what,
environment logic, outcome). Subclasses live in the experiments package.

Contract with the runner (mas_sim.runner):
- `schedule()` yields Steps in order. Agents within one Step speak in parallel: all
  their contexts are built before any of them replies, so they never see each
  other's current-step messages.
- `build_context()` is the ONLY place that decides what an agent sees. It must be
  a pure function of (agent, step, transcript, scenario config/state).
- `after_step()` runs after the step's messages are appended; it holds
  deterministic environment logic and may return a dict that is logged.
- `outcome()` computes per-run metrics from parsed fields only.
A new Scenario instance is created for every run, so instance state never leaks
between runs.
"""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass

from mas_sim.agents import Agent, Context
from mas_sim.transcript import Transcript


@dataclass(frozen=True)
class Step:
    round: int
    index: int  # global step counter within the run, starting at 0
    agents: tuple[Agent, ...]

    def __post_init__(self) -> None:
        ids = [a.id for a in self.agents]
        assert ids, "a step needs at least one agent"
        assert len(set(ids)) == len(ids), f"agent listed twice in one step: {ids}"


class Scenario[ConfigT](ABC):
    """ConfigT: the experiment's config dataclass (frozen; hashed into run ids)."""

    #: Experiment name written into run records.
    name: str

    def __init__(self, config: ConfigT, replicate: int) -> None:
        self.config = config
        self.replicate = replicate

    @abstractmethod
    def schedule(self) -> Iterator[Step]: ...

    @abstractmethod
    def build_context(self, agent: Agent, step: Step, transcript: Transcript, run_id: str) -> Context: ...

    def after_step(self, step: Step, transcript: Transcript) -> dict | None:
        return None

    @abstractmethod
    def outcome(self, transcript: Transcript) -> dict: ...
