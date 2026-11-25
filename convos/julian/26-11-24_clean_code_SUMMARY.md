# SUMMARY: Code-quality tooling (`make check`: ruff, pyright, pytest)

**Last updated:** 26-11-24 (implemented; `make check` green; pre-commit/CI still open)

Julian asked for "clean code stuff", meaning tooling plus a `make check` [decided: transcribed chat comment in the LOG]. No refactoring beyond what the checks required.

**How to use:** `make check` runs lint, format check, type check, and tests, all read-only. `make fix` applies ruff's safe fixes and formats (review the diff). Agents must run `make check` before calling coding work done (`docs/CODING.md` § Additional instructions).

Setup [concluded; line length 120 not yet confirmed by Julian]:
- ruff: rules E, F, W, I, B, UP, SIM, RUF; line length 120 (matches how the code was written); no docstring rules (they conflict with CODING.md's "why, not what").
- pyright basic mode against the project `.venv`.
- Config in `pyproject.toml`; targets in `Makefile`.

Code changes worth knowing (details in the LOG entry *tooling implemented, make check green*):
- `zip(..., strict=True)` throughout `mas_sim` (a silent truncation would break fail-loudly); `itertools.pairwise` for successive pairs.
- `Scenario[ConfigT]` and `run_sweep[C]` are generic in the config type.
- `Agent` Protocol members are read-only properties.
- New `Message.parsed_as(Schema)` / `Transcript.last_parsed(sender, Schema)`: typed access to parsed output that asserts the schema. `AuthorityScenario.outcome` uses them. This is the only behaviour change.
- `LogWriter` is a context manager.

Verified: `make check` green, 47 tests; a seeded bare `zip()` makes it fail [verified: 26-11-24]. No live API run.

Open: pre-commit hook (my lean: ruff only), GitHub Actions CI, line length 120 vs 88. Nothing committed yet.

LOG: `convos/julian/26-11-24_clean_code_LOG.md`
- See also: `convos/julian/26-11-24_mas_sim_plan_SUMMARY.md`: the code these checks cover; this topic changed some of its interfaces (generic `Scenario`, typed parsed access).
