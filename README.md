# mas-risks

This project builds small open-weight agents whose susceptibility to influence is controlled, then runs them in multi-agent risk scenarios. Julian Bitterlich and Ankush work on it; Ankush is Researcher A of the research plan (model organisms and their evals).

**This branch (`res_A_remote_run`) is for running the work on a machine with a 24 GB GPU.** It holds the code, the data built so far, the run logs under `runs/`, and these documents:

- [docs/REMOTE_AGENT_BRIEF_2.md](docs/REMOTE_AGENT_BRIEF_2.md): what to do next on that machine. Start here. The first brief, [docs/REMOTE_AGENT_BRIEF.md](docs/REMOTE_AGENT_BRIEF.md), is carried out; its description of the eval and its working rules still hold.
- [docs/remote_run_report.md](docs/remote_run_report.md): report of the first run of the base model on dev.
- [docs/work_plan_model_organisms.md](docs/work_plan_model_organisms.md): all steps of Researcher A's part, with their state.
- [docs/research_agenda.md](docs/research_agenda.md): the research plan of the whole project.

The project's working records (design log, notes for Julian, stored papers, and the conventions for keeping them) are on the branch `res_A_work_branch` and are not needed here.

## State

As of 26-11-25: the item generator, the split specification, the leak checks, the eval harness with scoring, the pushback wordings and the assembly of dialogues are written and tested (129 tests). The base model was run on the dev set once (report above). After it, the output format was decided (reason before decision) and three families were changed; the dev set as rebuilt has 1,568 dialogues from 392 items and has not been run.

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
