# mas-risks

This project builds small open-weight agents whose susceptibility to influence is controlled, then runs them in multi-agent risk scenarios. Julian and Ankush work on it.

This project uses the [Epistemic Memory](https://github.com/FlorianDietz/EpistemicMemory) conventions: all project memory lives in LOG/SUMMARY file pairs under `convos/`, governed by [CLAUDE.md](CLAUDE.md). Human guide: [docs/HOW_TO_USE.md](docs/HOW_TO_USE.md). Open ideas and deferred items: [FUTURE_WORK.md](FUTURE_WORK.md). Workflow problems and lessons: [FEEDBACK.md](FEEDBACK.md).

**Papers:** papers relevant to the project are stored as agent-readable markdown under [papers/](papers/README.md), one folder per paper. Each folder holds the converted text and, where we have one, a separate notes file with our own comments. The index and the procedure for adding a paper are in `papers/README.md`.

## Team

- Julian Bitterlich — `convos/julian/` (git user.name: `Julian Bitterlich`). Researcher B of the research plan (simulations S1–S3 and instrumental hooks); assumed by elimination, not yet confirmed by Julian.
- Ankush — `convos/ankush/` (git user.name: `Ankush7890`). Researcher A of the research plan (model organisms and their evals).

**Identifying the current user:** match `git config user.name` against this list. If it doesn't match anyone or the match is ambiguous, ask before proceeding.

## Current status and goals

The research plan is [docs/research_agenda.md](docs/research_agenda.md): four research questions, three simulations, two researchers, about 8 part-time weeks. The ordered steps for Researcher A's part (model organisms and their evals) are in [docs/work_plan_model_organisms.md](docs/work_plan_model_organisms.md), accepted by Ankush as the working plan on 26-11-25.

As of 26-11-24: the shared Python environment is defined but not yet installed or tested on any machine. Researcher A's work on the susceptibility eval, steering vectors and LoRAs is at the design-proposal stage, with no code written (see the model-organisms topic in the index below).

**Open for Julian:** three points need his agreement before code is written: the shared environment, a shared code package, and content reserved for his simulations. They are in [convos/ankush/26-11-24_note_for_julian.md](convos/ankush/26-11-24_note_for_julian.md).

## Environment

One Python environment at the repository root serves all code, so both researchers run the same library versions. `pyproject.toml` lists the direct dependencies, `uv.lock` pins every package, and `requirements.txt` is exported from the lock. Python 3.12 or newer; a Linux machine with an NVIDIA GPU for anything that loads a model.

With [uv](https://docs.astral.sh/uv/) (preferred, installs exactly what the lock says):

```bash
uv sync                      # creates .venv with runtime and dev packages, and installs src/mas_risks in editable mode
source .venv/bin/activate
```

With plain pip:

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pip install --no-deps -e .   # the project's own package, src/mas_risks
```

The tests of the item generator need no GPU and none of the large packages. On a laptop, this installs only pytest and ruff and runs them:

```bash
uv run --only-group dev pytest
```

The pushback wordings and rephrased arguments are written by Claude models through the Anthropic API. This needs the dependency group `wording` and `ANTHROPIC_API_KEY` in the environment or in `.env`; the results are stored under `data/`, so it is only needed to regenerate them:

```bash
uv run --only-group dev --only-group wording python -m mas_risks.wordings.generate --dry-run
```

Check that the GPU is visible:

```bash
python -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

To add or upgrade a dependency, edit `pyproject.toml`, then regenerate the other files and commit all of them together:

```bash
uv lock                      # add --upgrade to move everything to the newest versions
uv export --frozen --no-hashes --no-dev --no-emit-project --format requirements-txt -o requirements.txt
uv export --frozen --no-hashes --only-dev --format requirements-txt -o requirements-dev.txt
```

Keys such as a Hugging Face token go in a `.env` file at the repository root, which git ignores.

## Maintenance

Recurring tasks:

| Task | Last run | Due when | Notes |
|------|----------|----------|-------|
| Sync (LOG/SUMMARY drift) | — | After many LOG changes, or ~monthly | `!sync`; procedure: `docs/procedures/sync.md` |
| LLM-ism checklist refresh | — | ~Monthly while you publish regularly; otherwise before any high-stakes submission | Update the checklist and Known-screening sections of `docs/procedures/outward_text.md` from full primary sources (see the file's refresh rule); bump its refresh date |

## Conversation Index

All discussions live in `convos/{user}/`. **When starting a new topic, add a row here.** Read the SUMMARY first; open the LOG only if the SUMMARY is insufficient. Status cells describe current state only — rewrite them on update, don't append.

| Date | User | Topic | Status | SUMMARY | LOG |
|------|------|-------|--------|---------|-----|
| 26-11-21 | julian | Project setup (template configuration) | Done | [SUMMARY](convos/julian/26-11-21_project_setup_SUMMARY.md) | [LOG](convos/julian/26-11-21_project_setup_LOG.md) |
| 26-11-21 | julian | Papers library (`papers/` folder, conventions, converter) | Set up; 2 papers added | [SUMMARY](convos/julian/26-11-21_papers_library_SUMMARY.md) | [LOG](convos/julian/26-11-21_papers_library_LOG.md) |
| 26-11-21 | julian | Emergent MAS risks paper: workshop (OpenReview) vs arXiv v4 | Compared; v4 stored in papers/ | [SUMMARY](convos/julian/26-11-21_emergent_mas_risks_versions_SUMMARY.md) | [LOG](convos/julian/26-11-21_emergent_mas_risks_versions_LOG.md) |
| 26-11-24 | ankush | Local setup on Ankush's machine (clone, tool checks, git user.name) | Done | [SUMMARY](convos/ankush/26-11-24_local_setup_SUMMARY.md) | [LOG](convos/ankush/26-11-24_local_setup_LOG.md) |
| 26-11-24 | ankush | Model organisms: susceptibility eval, steering vectors, naive and discerning LoRAs; also the research plan and the shared environment | Plan and environment added; eval and data design settled on Ankush's side; work plan accepted (`docs/work_plan_model_organisms.md`); its steps 1 to 4 implemented and step 7 partly (package `src/mas_risks/`: item generator, split specification, leak checks, eval harness; 127 tests pass; no data generated, no model run); item design changed on 26-11-25 so that an argument's validity depends on the item; new items accepted by Ankush; pushback wordings written by two models and accepted; dev dialogues assembled; waiting for the GPU machine and Julian's answers | [SUMMARY](convos/ankush/26-11-24_model_organisms_SUMMARY.md) | [LOG](convos/ankush/26-11-24_model_organisms_LOG.md) |
