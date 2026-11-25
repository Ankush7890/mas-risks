# Progress log of the remote GPU run (REMOTE_AGENT_BRIEF.md)

Kept by the agent on the GPU machine (RTX 3090, 24 GB) so that a successor can continue if the machine dies. Newest entries at the bottom. Pushed at least hourly.

## 26-11-25

- Task A (environment): `uv sync` installed the lock unchanged (torch 2.15.0+cu132, transformers 5.24.0). GPU check OK (RTX 3090). `uv run pytest`: 127 passed. Nothing had to be changed.
- Model revision: `Qwen/Qwen3-4B-Instruct-2507` @ `cdbee75f17c01a7cc42f958dc650907174af0554`. Sampling: temperature 0.7 (research plan), top_p 0.8, top_k 20, min_p 0 (model card); max_new_tokens 1024.
- Task B: wrapper `src/mas_risks/models.py` (`QwenChat`): bf16, chat template, thread-safe `generate` that batches concurrent calls. Runner `python -m mas_risks.eval.run` (resumable: skips dialogue ids already in the log; metadata in `<log>.meta.json`).
- Printed one full templated prompt (`--show-prompt`) and read it: layout is fine.
- Next: smoke run of 20 dialogues (`runs/smoke_base.jsonl`).
- Smoke run (`runs/smoke_base.jsonl`, 20 dialogues, all read): JSON valid 40/40, no cut-offs. Main problem: with `decision` first in the JSON the model states a letter, then reasons in `reason` to another letter (e.g. "decision C ... so correct answer is D"), and the neutral pushback then "flips" it. Added format variant `reason_first` in `eval/prompts.py` (same keys, reason first).
- Batch 64 overflowed 24 GB (WSL spills to RAM, very slow); batch 32 uses ~18 GB, ~115 s per 64 dialogues.
- Full dev run with draft prompts started: `runs/dev_base.jsonl` (variant `base`, prompts `draft`; started at commit with run.py of 3337384+). Then planned: extra turn-1 pass `runs/dev_base_turn1_extra.jsonl`; same two with `--prompts reason_first --variant base_reason_first`.
- Analysis script: `python -m mas_risks.eval.report --log <log> --extra <extra> --variant <v>`.
