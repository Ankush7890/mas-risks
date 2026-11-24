"""General multi-agent simulation library: agents, LLM client, transcripts,
scenario base class, runner, logging.

Boundary rule: this package holds no experiment content (no prompts, scenario
texts, scoring, API keys or results) and must never import `risk_experiments`.
Experiment-specific code lives in `risk_experiments`; a helper moves here only
once two experiments need it. Both packages share one pyproject and one venv,
so the import rule is enforced by a test (tests/mas_sim/test_mas_sim_core.py).

Modules: agents (LLMAgent, ScriptedAgent, ReplayAgent), llm (providers, message
normalization, cache), output (JSON instruction and strict parser), transcript,
scenario (Scenario base class, Step), runner (run loop, sweeps), logs (JSONL).
"""
