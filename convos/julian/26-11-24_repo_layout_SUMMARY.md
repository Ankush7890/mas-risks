# SUMMARY: Where code lives in the repo

**Last updated:** 26-11-24 (decided and implemented: one pyproject at the repo root, packages under `src/`)

Julian questioned the template convention of putting each codebase in `projects/<name>/` with its own pyproject, since this repo is one research project.

**Decision** [decided: Julian, transcribed chat comment in the LOG]: one `pyproject.toml` at the repo root, one uv-managed `.venv`, import packages under `src/` (`mas_sim`, `risk_experiments`).

How we got there: I first argued for keeping a container folder because the `mas_sim` plan had two codebases (two pyprojects, one shared venv). Julian found several pyprojects overkill. We looked at a middle ground: one root venv shared by several pyprojects, via pip editable installs or a uv workspace. It keeps per-package dependency lists but gives no import isolation, so Julian rejected it as overcomplicated. I mildly preferred a single top-level code folder over the repo root, mainly to avoid the clash with the memory system's `docs/`. Julian ran `uv init` at the root, which settled it.

Implemented [verified: `uv sync` + importing both packages under `uv run`, 26-11-24; Python 3.14.3]:
- `pyproject.toml` has a hatchling build backend with `packages = ["src/mas_sim", "src/risk_experiments"]`. Every new package under `src/` must be added there.
- Both packages exist with docstring-only `__init__.py`. `mas_sim` states the boundary rule: no experiment content, never imports `risk_experiments`. Nothing enforces it mechanically.
- `docs/CODING.md` § Project Structure now describes this layout. uv's hello-world `main.py` was deleted.

Follow-up done in the `mas_sim` plan topic (26-11-24): the plan was adapted to this layout and moved to `convos/julian/26-11-24_mas_sim_plan_DRAFT.md`; the `projects/` folder is deleted.

LOG: `convos/julian/26-11-24_repo_layout_LOG.md`
- See also: `convos/julian/26-11-24_mas_sim_plan_SUMMARY.md`: the plan defining `mas_sim` and `risk_experiments`, whose layout this topic changed.
