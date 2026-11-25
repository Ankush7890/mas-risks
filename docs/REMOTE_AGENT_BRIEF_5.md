# Fifth brief for the agent on the 24 GB GPU machine: step 9, freeze and generate

**Written:** 26-11-25 by Claude Opus 5.5 (the agent on the GPU machine) after Ankush asked to "do the next steps" following `docs/remote_run_report_4.md`, which recommended the freeze. Carried out by the same agent. Step 9 of `docs/work_plan_model_organisms.md`:

> Freeze the generator and record its git commit. Generate all sets. Keep an item only if the base model gives the intended default answer in at least 4 of 5 samples at temperature 0.7, with the same rule for every set. Report how many items each family loses. Run the leak checks. Write a manifest with a hash of every data file, add a canary string, and commit data and manifest together. Done when: the leak checks pass, the manifest is committed, and a test-access log exists. From here the test files do not change, and every run on a test set is recorded in that log with date, variant and purpose.

**Stop after step 9.** Step 10 (the base-model baseline on val) is the next decision.

## 1. Freeze

- The generator is frozen at the commit that starts this brief's runs. Record it in the manifest and in `docs/work_plan_model_organisms.md`.
- From then on, any change under `src/mas_risks/items/`, `src/mas_risks/splits/split_spec.toml` or `data/wordings/` invalidates the sets. A test compares the generated items with the frozen files and fails on any difference.

## 2. Selection: filter, quota, balance

For each set except dev (dev was for tuning and is discarded) and each family:

- **Order and balance.** Take the set's candidates (`splits.candidates`) in seed order, separately for the two kinds of item (`rule_applies` true: the argument is valid; false: misleading).
- **Samples.** Ask turn 1 five times per item (reason-first format, the draft system prompt, temperature 0.7), exactly as on dev.
- **The rule.** An item passes with at least 4 default answers. An invalid reply counts as not default.
- **Quota.** Keep the first passing items of each kind until the family's quota is filled: half of each kind; with an odd quota, the extra item goes to the valid kind. The base model is asked about further items only while the quota is unfilled. Candidates beyond that point are never sampled, which saves about two thirds of the GPU time.
- **Shortfall.** If a family runs out of candidates before its quota, report it and stop. Do not lower the bar or add seeds without Ankush.
- **Records.** The filter log goes to `runs/filter/<set>.jsonl`, one line per sample with prompts and raw output, as for every run. The selection goes to `data/sets/<set>.selection.json`:
  - per family, the kept item ids in order;
  - per family, the number sampled, passed and lost.

The test sets (`test_seen`, `test_unseen`) are filtered in the same way. These are turn-1 runs on test items and the first entries of the test-access log (section 5). No decision other than the pre-registered keep rule may be drawn from them, and the logs are not read for anything else.

## 3. Arguments

- Rephrase the arguments of the kept items only:
  - `train` and `val` with `claude-sonnet-5-5`;
  - `test_seen` and `test_unseen` with `claude-opus-5-5`.

  This is the author assignment in `wordings/generate.py`. The work plan marks the model names as assumed and not confirmed; the report says so.
- Use `python -m mas_risks.wordings.rephrase --set <set>`, restricted to the selection.
- Read a sample of 20 per set before going on. Report fallbacks per family.

## 4. Build, export, checks

- `build(<set>)` uses the selection when it exists, so each set has exactly its quota of items.
- Run the leak checks (`splits.leak_checks.run_all`) on all five sets together. Dev is included as built, since it is still a set in the split spec.
- Export every set except dev to `data/sets/<set>.jsonl`, one line per dialogue with everything a run needs:
  - the turn-1 text and the turn-2 message;
  - labels, roles, target, condition, version and wording id;
  - the item's parameters;
  - the canary string.

## 5. Manifest, canary, test-access log

- **Canary.** A fresh UUID with a fixed prefix (`MAS-RISKS CANARY …`), written into every exported line and into the manifest.
- **Manifest** `data/MANIFEST.json`:
  - generator commit, date and canary;
  - the SHA-256 of every file under `data/` (except the manifest itself) and of `split_spec.toml`;
  - per set, the item and dialogue counts.

  A test recomputes the hashes.
- **Test-access log** `docs/test_access_log.md`: one row per run that touches a test set, with date, set, variant, purpose and log file. Its first rows are the filter runs of section 2.
- Commit data, selection, manifest and log together.

## 6. Report

Write `docs/freeze_report.md`. At the top, state what was run. Then cover:

- per set and family: candidates sampled, passed, lost, kept, and the pass rate with interval;
- whether every quota was filled;
- the unseen families: their pass rates, since they were never run before, and the roles of their wrong first answers. These are counts only, not read for decisions;
- argument fallbacks per set and family;
- the leak-check report;
- the manifest summary.

## 7. Limits

- Nothing on the test sets beyond the turn-1 filter, and that is logged.
- No change to generators, wordings or the split spec. If something forces one (a shortfall, a leak-check failure), stop and report.
- Every number comes from a file by code in the repository.
- Commit on `res_A_remote_run`, push after each milestone, and keep `docs/remote_run_progress.md` current.
