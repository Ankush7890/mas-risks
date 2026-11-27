# Test-access log

Every run that touches `test_seen` or `test_unseen` adds a row here (work plan step 9). Code that runs on a test set appends its own row (`eval/filter_sets.py`); anything else must be added by hand in the same commit as its log. The test files do not change after the freeze (`data/MANIFEST.json`, tag `freeze-v1`).

| date (UTC) | set | variant | purpose | log | git commit |
|---|---|---|---|---|---|
| 2026-11-25T19:55:56+00:00 | test_seen | base_filter | step-9 filter: turn 1 only, 5 samples per item, pre-registered keep rule; no other use | `runs/filter/test_seen.jsonl` | `1c5a0fc5ceaa` |
| 2026-11-25T20:04:31+00:00 | test_unseen | base_filter | step-9 filter: turn 1 only, 5 samples per item, pre-registered keep rule; no other use | `runs/filter/test_unseen.jsonl` | `a81479a2e679` |
| 2026-11-25T20:30:14+00:00 | test_seen | argument rephrasing (claude-opus-5-5) | step 9: rephrase the kept items' arguments; the model sees only the argument text, not the case or the base model's answers | `data/arguments/test_seen.jsonl` | `52df77117bd2` |
| 2026-11-25T20:30:14+00:00 | test_unseen | argument rephrasing (claude-opus-5-5) | step 9: rephrase the kept items' arguments; the model sees only the argument text, not the case or the base model's answers | `data/arguments/test_unseen.jsonl` | `52df77117bd2` |
| 2026-11-27T09:33:43+00:00 | test_unseen | base | step 18: pre-registered test run | `runs/test/test_unseen.jsonl` | `1a74fd715110` |
| 2026-11-27T09:53:02+00:00 | test_unseen | persona_yield_2 | step 18: pre-registered test run | `runs/test/test_unseen.jsonl` | `c973d955b03e` |
| 2026-11-27T10:14:05+00:00 | test_unseen | persona_hold_2 | step 18: pre-registered test run | `runs/test/test_unseen.jsonl` | `93b6ada7eb6b` |
| 2026-11-27T10:37:35+00:00 | test_unseen | persona_warning | step 18: pre-registered test run | `runs/test/test_unseen.jsonl` | `93b6ada7eb6b` |
| 2026-11-27T10:58:40+00:00 | test_unseen | steer_L18_1 | step 18: pre-registered test run | `runs/test/test_unseen.jsonl` | `0c7912f8d2b0` |
| 2026-11-27T11:17:45+00:00 | test_unseen | steer_L18_-0.5 | step 18: pre-registered test run | `runs/test/test_unseen.jsonl` | `c4c60a8b904e` |
| 2026-11-27T11:41:49+00:00 | test_unseen | steer_random_L18_1 | step 18: pre-registered test run | `runs/test/test_unseen.jsonl` | `9b0165374ff0` |
| 2026-11-27T12:16:12+00:00 | test_unseen | naive_s0_c75 | step 18: pre-registered test run | `runs/test/test_unseen.jsonl` | `4785a43bc43d` |
| 2026-11-27T12:37:36+00:00 | test_unseen | naive_s1_c100 | step 18: pre-registered test run | `runs/test/test_unseen.jsonl` | `4785a43bc43d` |
| 2026-11-27T13:02:32+00:00 | test_unseen | naive_s2_c50 | step 18: pre-registered test run | `runs/test/test_unseen.jsonl` | `1ef722c2f328` |
| 2026-11-27T13:22:08+00:00 | test_unseen | discerning_s0_c100 | step 18: pre-registered test run | `runs/test/test_unseen.jsonl` | `523cc03965c7` |
| 2026-11-27T13:42:05+00:00 | test_unseen | discerning_s1_c100 | step 18: pre-registered test run | `runs/test/test_unseen.jsonl` | `88d0e872d411` |
| 2026-11-27T14:05:14+00:00 | test_unseen | discerning_s2_c100 | step 18: pre-registered test run | `runs/test/test_unseen.jsonl` | `88d0e872d411` |
| 2026-11-27T14:23:04+00:00 | test_seen | base | step 18: pre-registered test run | `runs/test/test_seen.jsonl` | `f6cd9fc7b023` |
| 2026-11-27T14:37:38+00:00 | test_seen | persona_yield_2 | step 18: pre-registered test run | `runs/test/test_seen.jsonl` | `f6cd9fc7b023` |
