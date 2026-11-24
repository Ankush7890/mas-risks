"""Structured agent output: the JSON instruction given to agents and the strict parser.

Every agent (LLM, scripted or replayed) must return one JSON object that validates
against its output schema. Parse failures raise `ParseError`; the runner then marks
the run as failed. There are no repair heuristics.
"""

import json

from pydantic import BaseModel, ConfigDict, ValidationError


class OutputSchema(BaseModel):
    """Base class for agent output schemas. Unknown fields are rejected."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class ParseError(Exception):
    pass


def schema_instruction(schema: type[BaseModel]) -> str:
    """Text appended to an agent's system prompt telling it the output format."""
    js = json.dumps(schema.model_json_schema(), indent=2)
    return (
        "Respond with a single JSON object and nothing else (no prose before or after it). "
        "The object must match this JSON Schema:\n" + js
    )


def extract_json_text(raw: str) -> str:
    """Return the JSON text of an agent reply.

    Accepted: the reply is exactly a JSON object, or exactly one Markdown code fence
    (```json ... ``` or ``` ... ```) around it, with only whitespace outside the fence.
    Intentionally this narrow: many models wrap JSON in a fence even when told not
    to, and unwrapping a fence that encloses the whole reply cannot change meaning.
    Anything else (prose around the JSON, several objects) is a parse error, not
    something to repair.
    """
    s = raw.strip()
    if s.startswith("```"):
        if not s.endswith("```") or s == "```":
            raise ParseError("reply starts with a code fence but does not end with one")
        first_newline = s.find("\n")
        if first_newline == -1:
            raise ParseError("code fence without content")
        lang = s[3:first_newline].strip()
        if lang not in ("", "json"):
            raise ParseError(f"code fence with unexpected language tag {lang!r}")
        s = s[first_newline + 1 : -3].strip()
        if "```" in s:
            raise ParseError("more than one code fence in reply")
    if not (s.startswith("{") and s.endswith("}")):
        raise ParseError("reply is not a single JSON object")
    return s


def parse_output(raw: str, schema: type[BaseModel]) -> BaseModel:
    """Parse and validate an agent reply. Raises ParseError with the reason."""
    assert isinstance(raw, str), type(raw)
    text = extract_json_text(raw)
    try:
        return schema.model_validate_json(text)
    except ValidationError as e:
        raise ParseError(f"schema validation failed: {e}") from e
