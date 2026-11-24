C: (transcribed from chat) (new convo): I'm currently debating with claude in another chat how to setup some experiment. The details don't matter for this. In this conversation it suggets moving the code to `projects` folder. I want to discuss this. I think the default is that this memony system is being used for multiple projects. Here however this is just a single project.

---

26-11-24, Claude Opus 5.5 — *where code lives: projects/ vs alternatives*

I have read README.md, CLAUDE.md, the project-structure section of `docs/CODING.md`, `convos/julian/26-11-24_mas_sim_plan_SUMMARY.md` and FEEDBACK.md. I have not read the other chat's current state beyond that SUMMARY.

**What the template means by `projects/`.** `docs/CODING.md` says "Each coding project lives in its own folder under `projects/`". The word "project" there means *one codebase* (its own `pyproject.toml`, `.venv`, `.env`, `data/`), not *one research project*. The template assumes one repo = one research effort that may contain several codebases. So the premise "the default assumes the memory system is shared across several projects" is not quite right [concluded: from the CODING.md wording and the per-folder pyproject/.env layout]. But the name is ambiguous, and that ambiguity is a fair complaint (see FEEDBACK entry of today).

**Does this repo need a container folder?** The current plan has two codebases: `mas_sim` (library) and `risk_experiments` (experiments, editable path dependency on `mas_sim`). `papers/tools/` is a third, small one that deliberately lives next to its data. With two or more codebases, a container folder earns its keep: it keeps `pyproject.toml`, `.venv`, `data/`, `logs/` etc. away from the memory system (`convos/`, `docs/`, `papers/`) at the root. [concluded]

**Options:**

1. **Keep `projects/`** (status quo). Zero cost, matches `docs/CODING.md`, and future agents reading the template docs find the code where the docs say. Downside: the misleading name stays.
2. **Rename the container** (e.g. `code/`). Cheap now, since nothing is implemented yet. Cost: one line in `docs/CODING.md`, the plan file's internal paths, the `mas_sim` plan SUMMARY. Its LOG is append-only, so old path mentions there stay and need an `OUTDATED` note. A deviation from the upstream template, so pulling template updates later needs a small manual merge.
3. **Flatten to the root** (`mas_sim/` and `risk_experiments/` next to `convos/`). Two Python projects then sit beside the memory folders at the top level, and the root gets crowded. I'd argue against it while there are two packages.
4. **One root-level Python project** (`pyproject.toml` at the repo root, `src/mas_sim/`, `src/risk_experiments/`). Natural for a single-research-project repo, but it makes the whole repo, including `convos/` and `papers/`, a Python package root, and it reverses the plan's two-package split. Only worth considering if the other chat collapses to one package.

**Recommendation:** keep a container folder (option 1 or 2). Between them, the choice is cosmetic. Keeping `projects/` is the lower-friction default. Renaming to `code/` is worth it if the name keeps bothering you, but do it *now*, before code exists, and update `docs/CODING.md` in the same change so the docs and the repo agree. [concluded]

Open for Julian: keep `projects/`, or rename (and to what)?

---

C: (transcribed from chat) Yes, please don't add cross-reference link right now. I'll tell the other chat once we have decided this. I think multiple .venv and pyproject.tomls is overkill actually

---

26-11-24, Claude Opus 5.5 — *one pyproject: what it changes*

Correction of the premise first: the current plan already uses one venv (`risk_experiments/.venv`, plan file line ~81). What it has twice is `pyproject.toml`: `mas_sim` and `risk_experiments` are separate distributions, and `risk_experiments` installs `mas_sim` as an editable path dependency. [verified: read the plan file 26-11-24]

**One pyproject with two import packages** (`src/mas_sim/`, `src/risk_experiments/`) is a reasonable simplification. [concluded]
- Kept: the library/experiment boundary. It becomes a package boundary instead of a distribution boundary. The rule "`mas_sim` never imports `risk_experiments` and holds no prompts, scenarios, scoring, keys or results" still holds. Without a second pyproject nothing enforces it mechanically, so it needs stating in the code (module docstring), and optionally a one-line test that greps `src/mas_sim/` for `risk_experiments` imports.
- Lost: separate dependency lists and separate installability of `mas_sim`. That only matters if `mas_sim` is to be published or reused outside this repo. Splitting it out later is a cheap move (folder plus a new pyproject), so there's no need to pay for it now.

**This changes the folder question.** With one codebase, `projects/<name>/` is nesting with a single child, so options 1/2 from the previous entry collapse to:
- (a) **One top-level code folder** (e.g. `code/` or `experiments/`) holding `pyproject.toml`, `src/mas_sim/`, `src/risk_experiments/`, `scripts/`, `data/`, `.env`, `.venv`.
- (b) **Repo root as the Python project**: `pyproject.toml`, `src/`, `scripts/`, `data/`, `.venv` next to `convos/`, `docs/`, `papers/`. This is workable: a src layout only packages `src/`, so `convos/`/`papers/` don't get swept in. Costs: the root mixes the memory system with build artifacts, and `docs/` already means "memory-system docs", which will confuse anyone who expects code docs there.

Recommendation: (a), mildly. It keeps the root readable as "memory system + one code folder" and avoids the `docs/` clash. (b) is fine if you value `pip install -e .` from the root more. Either way `docs/CODING.md` § Project Structure should be updated to describe this repo's actual layout. [concluded]

Open for Julian: (a) or (b); if (a), the folder name.

---

C: (transcribed from chat) So I can have a single .venv in the repo root and multiple toml's?

---

26-11-24, Claude Opus 5.5 — *one venv, several pyprojects*

Yes. A venv is just an environment; any number of packages can be installed into it, each from its own `pyproject.toml`.
- pip: `python -m venv .venv` at the root, then `pip install -e projects/mas_sim -e projects/risk_experiments`. [concluded: standard pip behaviour, not tried here]
- uv: a "workspace". A root `pyproject.toml` lists the members (`[tool.uv.workspace] members = ["projects/*"]`); uv then keeps one `uv.lock` and one `.venv` at the root, and `risk_experiments` declares `mas_sim` as a workspace dependency (`[tool.uv.sources] mas_sim = { workspace = true }`). I believe the root file can be a pure workspace file without its own package, but I haven't verified that against the current uv docs. [assumed]
- `.gitignore` already ignores `.venv/` at any depth, so nothing changes there.

What the two tomls still buy with a shared venv: each package declares its own dependencies, and `mas_sim` stays installable on its own. What they don't buy: isolation. In one venv, either package can import anything installed, including the other package, so the "`mas_sim` never imports `risk_experiments`" rule is still only enforced by convention or a test, exactly as with one toml. [concluded]

So this is a middle ground: one environment to manage (the part that is actually tedious), at the cost of a second `pyproject.toml` (and, with uv, a third root file). It is worth it if you expect `mas_sim` to be reused or published; otherwise one toml is simpler. With this variant `projects/` keeps a reason to exist (it holds two codebases), so the earlier options 1/2 (keep or rename `projects/`) apply again.

---

C: (transcribed from chat) ok, let's not overcomplicate. Just a simple src with the different packages and one pyproject.toml. I have already run `uv init` and `uv sync`

---

26-11-24, Claude Opus 5.5 — *root layout implemented*

[decided] (per the transcribed comment above): one `pyproject.toml`, several import packages under `src/`. Julian ran `uv init` at the repo root, so the root is the Python project (option (b) of the entry *one pyproject: what it changes*, not the separate code folder I'd mildly recommended).

What `uv init` produced: `pyproject.toml` (application mode, no build backend, `requires-python >=3.14`), `.python-version` (3.14), `uv.lock`, `.venv`, a hello-world `main.py`. Without a build backend `uv sync` does not install the project, so packages under `src/` would not be importable.

What I did:
- `pyproject.toml`: added `[build-system]` hatchling and `[tool.hatch.build.targets.wheel] packages = ["src/mas_sim", "src/risk_experiments"]`. Hatchling must be told explicitly because the project name `mas-risks` matches neither package. Replaced uv's placeholder description.
- Created `src/mas_sim/__init__.py` and `src/risk_experiments/__init__.py`, docstrings only; the `mas_sim` docstring states the boundary rule (no experiment content, never imports `risk_experiments`). Package names are still the plan's placeholders; renaming an empty folder is trivial.
- Deleted uv's hello-world `main.py` (no content beyond the template print).
- Rewrote `docs/CODING.md` § Project Structure to describe this layout instead of the template's `projects/<name>/`.
- [verified: `uv sync` + `uv run python -c "import mas_sim, risk_experiments"` 26-11-24] Python 3.14.3; both packages import from `src/` (editable install).

Noticed: the shell has `VIRTUAL_ENV` pointing at another project's venv (`~/projects/ARENA_2026/.venv`). `uv run` ignores it (with a warning), but a bare `python` in that shell would use the wrong environment.

Not done, left for the `mas_sim` plan chat: the `projects/` folder now holds only plan documents (`projects/mas_sim/PLAN.md`, `projects/risk_experiments/IMPLEMENTATION_PLAN_mas_sim_and_risk_experiments.md`), and the plan's file tree and setup section still describe two pyprojects under `projects/`. Both need updating to this layout, and the plan files need a new home once `projects/` goes. Cross-reference to that topic's SUMMARY still withheld at Julian's request.
