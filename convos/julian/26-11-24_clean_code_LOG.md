new convo. Can you add some clean code stuff to this repo? First can you tell me what you're planning to add?

---

26-11-24, Claude Opus 5.5 — *clean-code plan, before any changes*

I have read README, CLAUDE.md, docs/CODING.md, FEEDBACK.md, the `mas_sim` plan and repo layout SUMMARYs, and all code under `src/`, `scripts/`, `tests/` (about 1,900 lines). I changed nothing yet.

## What is there now

- Dev tooling: only pytest. No linter, formatter, type checker, pre-commit hook or CI. The GitHub remote `julxi/mas-risks` has no `.github/` folder.
- Tests: 46 pass [verified: `uv run pytest`, 26-11-24].
- The code is already in decent shape: module docstrings state contracts, comments explain *why*, asserts are everywhere. I don't see a case for structural refactoring [concluded: no module is large (largest: `authority.py`, 382 lines), and the package split follows the decided plan].

## Dry runs (nothing written)

**ruff lint** (rule sets E, F, W, I, B, UP, SIM, RUF), line length ignored: 17 findings [verified: `uvx ruff check`, 26-11-24].
- 8 auto-fixable cosmetic ones: `typing` → `collections.abc` imports (5), quoted annotations (2), import order (1).
- **B905 `zip()` without `strict=`** (4×: `src/mas_sim/runner.py` 3×, `src/mas_sim/llm.py` 1×). This is the useful one: `zip` silently truncates on a length mismatch, which goes against the repo's fail-loudly rule. In `runner.py` the lengths are equal by construction today, so this is no live bug [concluded: `ctxs` and `outs` are both built from `step.agents`], but `strict=True` turns a future mistake into a crash. In `llm.py` the zip is `zip(body, body[1:])`, a deliberate off-by-one, so it should become `itertools.pairwise`.
- SIM115 in `LogWriter` (file opened without `with`): the handle is long-lived on purpose. Fix by making `LogWriter` a context manager, not by suppressing.
- RUF001 en dash in `authority.py`: it sits in prompt text, so it is content, not a bug. Keep it, with a `noqa` and a reason.
- Small ones: SIM113 (manual counter in runner), RUF015 (one test).
- Line length: at ruff's default 88, 136 more findings. The code is written to about 120 columns.

**ruff format**: reformats 11 of 16 files at line length 88, 7 at 120 [verified: `uvx ruff format --check`, 26-11-24].

**pyright** (with the project venv): 27 errors [verified: `uvx pyright --pythonpath .venv/bin/python`, 26-11-24]. They come from four real typing gaps, not runtime bugs:
1. The `Agent` Protocol declares `id` and `schema` as writable attributes, but the agents are frozen dataclasses, so no agent class formally matches the Protocol. Fix: declare them as read-only properties in the Protocol.
2. `Scenario.__init__(self, config, ...)` is untyped, so subclasses see `config: object`. Fix: make `Scenario` generic in its config type.
3. `LLMClient._clients: dict[str, object]` hides the `AsyncOpenAI` type, so `.chat` is unknown.
4. `agent_overrides: dict[str, Agent]` should be `Mapping[str, Agent]` (dict is invariant, so a `dict[str, ScriptedAgent]` is rejected).

## Plan

1. **ruff (lint + format)**, configured in `pyproject.toml`, added to the `dev` dependency group. Rules E, F, W, I, B, UP, SIM, RUF; line length 120 (it matches how the code is written and means less reformatting churn). Fix the findings as described above, then run the formatter once.
2. **pyright in basic mode**, configured in `pyproject.toml` and added to `dev`. Fix the four typing gaps above. Basic, not strict: strict mode would demand annotations on every test helper for little gain at this size [assumed].
3. **`docs/CODING.md` § Additional instructions**: the three check commands (`uv run ruff check`, `uv run ruff format --check`, `uv run pyright`) plus pytest, which an agent must run before calling coding work done. This is what makes agents actually use the tools; a config alone doesn't.
4. **Re-run the 46 tests** after every step; record results here.

Deliberately not planned:
- No docstring linter (pydocstyle / ruff `D` rules): it pushes toward "what" docstrings on every function, against CODING.md's "comments say why, not what".
- No refactoring beyond the fixes above (see "What is there now").

Open questions for Julian:
- Did you mean tooling like the above, or refactoring in the "Clean Code" (book) sense? I read it as tooling.
- Add a **pre-commit hook** (ruff on each commit)? It catches things on your commits, but it is one more tool to install. My mild lean: yes, ruff only (fast); pyright and pytest stay manual.
- Add **GitHub Actions CI** (lint + types + tests on push)? Cheap to add; worth it if Ankush will push code too.
- Line length 120 instead of 88: OK?

Side note: your shell has `VIRTUAL_ENV` set to the ARENA_2026 project's venv. uv ignores it with a warning and uses this repo's `.venv`, so it does no harm here.

---

C: (transcribed from chat) Yeah, I meant this and also a `make check` and those things

---

26-11-24, Claude Opus 5.5 — *tooling implemented, make check green*

Julian confirmed the tooling reading of "clean code" and asked for `make check` [decided: transcribed comment above]. He did not answer the questions on pre-commit, CI, or line length; I used 120 as proposed and added neither pre-commit nor CI (both still open below).

OUTDATED: two claims in the entry *clean-code plan, before any changes* were wrong:
- "RUF001 en dash in `authority.py`: it sits in prompt text". It sits in `normalize_drug`, which deliberately turns en and em dashes in drug names into hyphens. I wrote the plan without reading the flagged line. Fixed by writing the dashes as `–` / `—` escapes with a comment; behaviour unchanged.
- "27 pyright errors from four typing gaps". There was a fifth gap, hidden because I only read the tail of that output: `Message.parsed` is typed `BaseModel`, so every access to a schema field (`p["agent_5"].final_regimen`, ...) was untyped.

## What changed

- `pyproject.toml`: `ruff` and `pyright` in the `dev` group; `[tool.ruff]` (line length 120, rules E F W I B UP SIM RUF, no D) and `[tool.pyright]` (basic mode, project `.venv`), each with a one-line reason.
- `Makefile`: `check` (= `lint format-check typecheck test`, all read-only), `fix` (ruff safe fixes + format), `help`. It unexports `VIRTUAL_ENV` only to silence uv's warning about the other project's venv in Julian's shell.
- `docs/CODING.md` § Additional instructions: run `make check` before calling coding work done; rules of thumb (`zip(strict=True)`, typed parsed access, targeted `noqa` with a reason only).
- Code fixes:
  - `runner.py`: `zip(..., strict=True)` 3×; manual step counter → `enumerate`; `run_sweep` and `Scenario` are generic in the config type, so `lambda c, r: AuthorityScenario(c, r, llm)` type-checks; `LogWriter` is used as a context manager (it gained `__enter__`/`__exit__`; the long-lived file handle keeps a `noqa: SIM115` with the reason).
  - `llm.py`: `zip(body, body[1:])` → `itertools.pairwise(body)`; the client cache is typed `AsyncOpenAI` via a `TYPE_CHECKING` import (the runtime import stays lazy, as before).
  - `agents.py`: the `Agent` Protocol declares `id` and `schema` as read-only properties, so the frozen-dataclass agents match it.
  - `transcript.py`: new `Message.parsed_as(Schema)` and `Transcript.last_parsed(sender, Schema)`. Both assert the parsed output is an instance of `Schema` and return it typed. `AuthorityScenario.outcome` uses them; this is the one behaviour change: a wrong schema in a seat now raises an AssertionError instead of a later AttributeError or a silently wrong field.
  - `authority.py`: `agent_overrides: Mapping[...]`; `render_output` takes `BaseModel` (it dispatches on isinstance anyway); three over-long f-string lines split.
  - Formatter: 7 files reformatted. Pure whitespace and line breaks; noisiest in `authority.py` and the two test files.
- New test `test_typed_access_checks_the_schema`.

## Verification

- `make check`: ruff clean, 16 files formatted, pyright 0 errors, 47 tests pass [verified: 26-11-24].
- Seeded defect: a bare `zip(a, b)` appended to `llm.py` made `make check` exit 2 with B905; after restoring, green again [verified: 26-11-24, single run].
- `scripts/run_authority.py --help` and `scripts/inspect_run.py --help` still import and run [verified: 26-11-24]. No live API run (still no usable key).

## Still open

- Pre-commit hook (ruff on each commit)? My lean: yes, ruff only.
- GitHub Actions running `make check` on push? Worth it once Ankush pushes code.
- Line length 120 vs 88: I went with 120; changing later is one `make fix`.
- Nothing is committed (repo rule: no git writes unless asked).
