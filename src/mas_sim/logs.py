"""JSONL logs: one record per agent turn ("call"), per environment update ("env")
and per finished run ("run"). Analysis reads only these files.

Record formats (all records have "type" and "run_id"):

call: round, step, agent, agent_kind ("llm"|"scripted"|"replay"), model, temperature,
      max_tokens, normalization, policy, cache_hit, finish_reason,
      messages (exactly as sent to the model; for non-LLM agents the context they got),
      visible ([round, step, sender] of each transcript message the agent could see),
      raw, parsed (dict or null), parse_error (str or null)
env:  round, step, data (whatever the scenario's after_step returned)
run:  experiment, config, replicate, status ("ok"|"failed"), outcome (dict or null),
      error (str or null)
"""

import json
from pathlib import Path
from typing import Iterable


class LogWriter:
    """Appends records to a JSONL file and flushes after each, so a crash keeps everything written so far."""

    def __init__(self, path: Path) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        self._f = open(path, "a", encoding="utf-8")

    def write(self, record: dict) -> None:
        assert "type" in record and "run_id" in record, sorted(record)
        self._f.write(json.dumps(record, ensure_ascii=False) + "\n")
        self._f.flush()

    def close(self) -> None:
        self._f.close()


def read_log(path: Path) -> list[dict]:
    assert path.exists(), f"log file not found: {path}"
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def run_records(records: Iterable[dict]) -> list[dict]:
    return [r for r in records if r["type"] == "run"]


def format_run(records: list[dict], run_id: str) -> str:
    """Every context and reply of one run, with visible delimiters, for reading by eye."""
    recs = [r for r in records if r["run_id"] == run_id]
    assert recs, f"run {run_id!r} not in log"
    out: list[str] = []
    for r in recs:
        if r["type"] == "call":
            who = r["model"] if r["agent_kind"] == "llm" else r["policy"]
            out.append(
                f"\n{'=' * 100}\nCALL round={r['round']} step={r['step']} agent={r['agent']} "
                f"kind={r['agent_kind']} ({who}) temperature={r['temperature']} "
                f"normalization={r['normalization']} cache_hit={r['cache_hit']}\n"
                f"visible: {r['visible']}\n{'=' * 100}"
            )
            for i, m in enumerate(r["messages"]):
                out.append(f"<<<<< message {i}: {m['role']} >>>>>\n{m['content']}\n<<<<< end message {i} >>>>>")
            out.append(f"<<<<< REPLY (finish_reason={r['finish_reason']}) >>>>>\n{r['raw']}\n<<<<< end reply >>>>>")
            if r["parse_error"] is not None:
                out.append(f"!!!!! PARSE ERROR: {r['parse_error']}")
        elif r["type"] == "env":
            out.append(f"\n--- ENV round={r['round']} step={r['step']}: {json.dumps(r['data'], ensure_ascii=False)}")
        elif r["type"] == "run":
            out.append(
                f"\n{'#' * 100}\nRUN {run_id} status={r['status']} error={r['error']}\n"
                f"config={json.dumps(r['config'])}\noutcome={json.dumps(r['outcome'], ensure_ascii=False, indent=2)}"
            )
        else:
            raise ValueError(f"unknown record type {r['type']!r}")
    return "\n".join(out)
