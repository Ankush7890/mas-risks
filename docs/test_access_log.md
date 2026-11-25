# Test-access log

Every run that touches `test_seen` or `test_unseen` adds a row here (work plan step 9). Code that runs on a test set appends its own row (`eval/filter_sets.py`); anything else must be added by hand in the same commit as its log. The test files do not change after the freeze (`data/MANIFEST.json`, tag `freeze-v1`).

| date (UTC) | set | variant | purpose | log | git commit |
|---|---|---|---|---|---|
