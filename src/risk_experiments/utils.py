"""Paths, .env loading and project-wide defaults for the experiments."""

from pathlib import Path

from dotenv import load_dotenv

PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parents[1]
SCENARIOS_DIR = PACKAGE_DIR / "scenarios"
DATA_DIR = REPO_ROOT / "data"
RESULTS_DIR = DATA_DIR / "results"
LLM_CACHE_DIR = DATA_DIR / "cache" / "llm"
ENV_PATH = REPO_ROOT / ".env"

# Default model for all LLM agents: a Mistral model (decided 26-11-24; selectable
# per run and per agent role). The specific model name is a working assumption until
# the first live run: "mistral-small-latest" is Mistral's alias for its current small
# model, chosen because sweeps are large and cost scales with calls.
DEFAULT_MODEL = "mistral:mistral-small-latest"

# Expected keys in .env: MISTRAL_API_KEY (default model); OPENAI_API_KEY only for
# openai: models; VLLM_BASE_URL / OLLAMA_BASE_URL only for local models.


def load_env() -> None:
    """Load the repo's .env into os.environ. Fails if the file is missing."""
    assert ENV_PATH.exists(), f"{ENV_PATH} not found; create it with MISTRAL_API_KEY=..."
    load_dotenv(ENV_PATH, override=False)
