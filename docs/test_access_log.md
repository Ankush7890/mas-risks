# Test-access log

Every run that touches `test_seen` or `test_unseen` adds a row here (work plan step 9). Code that runs on a test set appends its own row (`eval/filter_sets.py`); anything else must be added by hand in the same commit as its log. The test files do not change after the freeze (`data/MANIFEST.json`, tag `freeze-v1`).

| date (UTC) | set | variant | purpose | log | git commit |
|---|---|---|---|---|---|
| 2026-11-25T19:55:56+00:00 | test_seen | base_filter | step-9 filter: turn 1 only, 5 samples per item, pre-registered keep rule; no other use | `runs/filter/test_seen.jsonl` | `1c5a0fc5ceaa` |
| 2026-11-25T20:04:31+00:00 | test_unseen | base_filter | step-9 filter: turn 1 only, 5 samples per item, pre-registered keep rule; no other use | `runs/filter/test_unseen.jsonl` | `a81479a2e679` |
