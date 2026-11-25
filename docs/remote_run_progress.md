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
- Full dev run, draft prompts, done: `runs/dev_base.jsonl` (1,576 dialogues, 57 min, 3,155 calls, 74.6 new tok/s at batch 32, 3 replies hit 1,024 tokens). Extra turn-1 pass done: `runs/dev_base_turn1_extra.jsonl` (394 items).
- Findings so far (draft): JSON valid 100% after retry (3 first-attempt failures). Default first answer 55% overall; 4-of-5 filter passes 55% of items, five families at or below ~half (delivery 31%, lab 31%, print 38%, workshop 37%, leave 51%). The per-item default count is bimodal (0 or 5): the letter is fixed at the first token, before the reason; the reason often names another letter (14%; workshop 49%). Neutral flips (30%) are mostly the model correcting that letter, not yielding (0% to target). At turn 2 the decision often follows the argument's letter while the reason rejects it.
- Q5: almost no hedging; confidence 100 in 1,575/1,576 first answers. Q6: trigger details mostly named to be dismissed; one delivery_terms item guesses "oversized items take extra day". Q7 (draft): league_rules accepts false "unregistered player" claim in reasons; lab/print/workshop reasons reject the claim but the decision follows it.
- Running: `runs/dev_reason_first.jsonl` (variant `base_reason_first`), then its extra pass. Queue script: ~/queue.sh (not in repo; it just runs the four commands in order).
- Reason-first runs done: `runs/dev_reason_first.jsonl` and `runs/dev_reason_first_turn1_extra.jsonl` (1,824 s for the full set). Filter 80%, neutral 2%, majority 2%, authority 9%, valid 95%, misleading 53% (family-dependent: rejected in lab/print/workshop, accepted in league/delivery/library).
- Report written: `docs/remote_run_report.md` (task F). **All tasks of the brief are done; stopped as instructed before step 9.** Waiting for Ankush's decisions (format order, warranty_terms redesign, the other recommendations in the report).

## 26-11-25, second brief (`docs/REMOTE_AGENT_BRIEF_2.md`)

- Pulled `e3c5290` (three families changed, second brief). Two subagents reviewed the brief (design; executability); the brief was revised on their findings (its section 6). Added `eval/compare.py` (two runs side by side, items matched by turn-1 text hash, paired run-to-run movement), `report.py --list`, an `--extra` guard, `eval/position_cues.py`; 132 tests pass.
- Ran dev in full with reason-first: `runs/dev2_reason_first.jsonl` (1,568 dialogues, 1,202 s) and `runs/dev2_reason_first_turn1_extra.jsonl`.
- Report: `docs/remote_run_report_2.md`. Filter 80% → 88%; delivery 55% → 84%, print 81% → 100%, warranty 47% → 52% [38–66] (month slip persists as a "cover" confusion). Unchanged families move ≤ 8 points. Recommendation: not ready to freeze; reword warranty's charging clause, then fix option-position cues before training. Stopped before step 9 as instructed.

## 26-11-25, third brief (`docs/REMOTE_AGENT_BRIEF_3.md`)

- Brief written by this agent at Ankush's request; reviewed by two subagents; revised (its section 7). Ankush supplied an Anthropic key (`ANT` in `.env`, exported as `ANTHROPIC_API_KEY` for the rephrase command).
- Changes made (commit b51d9bd): warranty clauses name the cover period, cover drawn from 24/30/36 (dev warranty arguments rephrased again: 42 items, 0 fallbacks); print_shop case sentence; fillers on both sides (delivery, 3-day transit only; print_shop one bound copy). Snapshot of dev before the edits: `runs/snapshots/dev_before_brief3.json`. Dev now 388 items / 1,552 dialogues (warranty 42).
- Finding before the run: the pushback target's rank separates valid from misleading items in library_lending (valid rank 1–2, misleading rank 3–4) and partly in leave_policy (`position_cues.py`).
- Running: `runs/dev3_reason_first.jsonl` + extra pass, variant `base_reason_first_v3`, all 8 families.
- Run 3 done (`runs/dev3_*`, commit 70bbad0). Report: `docs/remote_run_report_3.md`. warranty_terms meets the pre-registered criterion (filter 88% [75–95], filler 0%, changed 0%, valid flips 100%). Unchanged families reproduce (248/248 filter verdicts). Recommendation: filter ready; freeze blocked on Ankush's decision about library_lending/leave_policy, where the target's rank separates valid from misleading arguments. Stopped before step 9 as instructed.
