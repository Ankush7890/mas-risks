"""Agents: stateless policies that map a Context to a text reply.

Three kinds share one interface, so any agent in a scenario can be swapped for
another kind without touching anything else:
- LLMAgent: calls a chat model.
- ScriptedAgent: a Python policy (fixed text, lookup table or rule). Used inside
  experiments, not only in tests, e.g. to hold one agent's message constant.
- ReplayAgent: returns what an agent said in an earlier logged run.

Agents hold no prompts and no memory. The system prompt and history are part of
the Context, which the scenario's `build_context` builds; that way a scripted
agent receives (and the log records) exactly what an LLM in its seat would see.
Every reply, from any kind of agent, is parsed with the agent's output schema by
the runner.
"""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel

from mas_sim.llm import NORMALIZATIONS, LLMClient, split_model
from mas_sim.logs import read_log
from mas_sim.transcript import Message


@dataclass(frozen=True)
class Context:
    """What one agent receives for one turn.

    messages: chat messages (system first), as an LLM in this seat would receive them.
    visible: the transcript messages this agent may see, so rule-based policies can
        read parsed fields instead of text. Both are produced by `build_context`.
    """

    run_id: str
    replicate: int
    round: int
    step: int
    agent_id: str
    messages: list[dict]
    visible: tuple[Message, ...]


@dataclass(frozen=True)
class AgentOutput:
    raw: str
    kind: str  # "llm" | "scripted" | "replay"
    sent_messages: list[dict]  # what an LLM received (normalized); ctx.messages for others
    model: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    normalization: str | None = None
    policy: str | None = None  # scripted: policy name; replay: source run id
    cache_hit: bool | None = None
    finish_reason: str | None = None


class Agent(Protocol):
    # Read-only properties, not plain attributes: a plain attribute in a Protocol
    # means "writable", which the frozen-dataclass agents are not.
    @property
    def id(self) -> str: ...
    @property
    def schema(self) -> type[BaseModel]: ...

    async def respond(self, ctx: Context) -> AgentOutput: ...


@dataclass(frozen=True)
class LLMAgent:
    id: str
    schema: type[BaseModel]
    model: str  # "provider:model_name"
    temperature: float
    client: LLMClient
    max_tokens: int = 1500
    normalization: str = "none"

    def __post_init__(self) -> None:
        split_model(self.model)
        assert self.normalization in NORMALIZATIONS, self.normalization

    async def respond(self, ctx: Context) -> AgentOutput:
        assert ctx.agent_id == self.id, (ctx.agent_id, self.id)
        c = await self.client.complete(
            self.model, ctx.messages, self.temperature, self.max_tokens, ctx.replicate, self.normalization
        )
        return AgentOutput(
            raw=c.text,
            kind="llm",
            sent_messages=c.sent_messages,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            normalization=self.normalization,
            cache_hit=c.cache_hit,
            finish_reason=c.finish_reason,
        )


@dataclass(frozen=True)
class ScriptedAgent:
    """A Python policy in an agent's seat.

    policy(ctx) -> reply text. The reply must be valid JSON for `schema`, exactly as
    an LLM's would have to be, so a typo in a scripted text fails loudly.
    policy_name is recorded in the log (e.g. "fixed_plan_b_v1").
    """

    id: str
    schema: type[BaseModel]
    policy: Callable[[Context], str]
    policy_name: str

    @classmethod
    def fixed(cls, id: str, schema: type[BaseModel], text: str, policy_name: str) -> ScriptedAgent:
        """Always replies with `text`."""
        return cls(id, schema, lambda ctx: text, policy_name)

    @classmethod
    def from_model(cls, id: str, schema: type[BaseModel], output: BaseModel, policy_name: str) -> ScriptedAgent:
        """Always replies with `output` serialized as JSON (validated against schema now)."""
        assert isinstance(output, schema), (type(output), schema)
        return cls.fixed(id, schema, output.model_dump_json(), policy_name)

    async def respond(self, ctx: Context) -> AgentOutput:
        assert ctx.agent_id == self.id, (ctx.agent_id, self.id)
        raw = self.policy(ctx)
        assert isinstance(raw, str), f"policy {self.policy_name} returned {type(raw)}"
        return AgentOutput(raw=raw, kind="scripted", sent_messages=ctx.messages, policy=self.policy_name)


class ReplayAgent:
    """Replays the replies agent `source_agent` gave in run `source_run_id` of a log.

    Replies are matched by (round, step), so the current scenario must schedule this
    agent at the same positions as the source run did; a missing position is an error.
    """

    def __init__(
        self, id: str, schema: type[BaseModel], log_path: Path, source_run_id: str, source_agent: str | None = None
    ) -> None:
        self.id = id
        self.schema = schema
        self.source_run_id = source_run_id
        src = source_agent if source_agent is not None else id
        calls = [
            r for r in read_log(log_path) if r["type"] == "call" and r["run_id"] == source_run_id and r["agent"] == src
        ]
        assert calls, f"no calls by {src!r} in run {source_run_id!r} of {log_path}"
        self._by_pos = {(r["round"], r["step"]): r["raw"] for r in calls}
        assert len(self._by_pos) == len(calls), "duplicate (round, step) in source run"

    async def respond(self, ctx: Context) -> AgentOutput:
        pos = (ctx.round, ctx.step)
        assert pos in self._by_pos, f"source run {self.source_run_id} has no reply at round/step {pos}"
        return AgentOutput(raw=self._by_pos[pos], kind="replay", sent_messages=ctx.messages, policy=self.source_run_id)
