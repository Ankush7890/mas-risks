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

## 8. Revisions after review and Ankush's decision (26-11-25)

Two subagents reviewed the draft above, one on method and one on executability. The points below **override** the sections above where they differ.

**Ankush's decision.** Freeze with the draft system prompt and the reason-first format. `src/mas_risks/eval/prompts.py` becomes a frozen path, and the manifest records the prompt texts' hashes. A later prompt change means rerunning the filter.

**Before the freeze.**
- **Step 0: the unseen families.** The four unseen families have never been run. Check them on fresh seeds first: 60 items each, from seed 50,000 up, keeping only items whose parameters occur in no set; 5 turn-1 samples (`eval/fresh.py --unseen`). Apply the same two-thirds bar. A family below it is redesigned on those seeds, never on `test_unseen`. The roles of wrong first answers for the unseen families are read from these logs, not from the test filter.
- **Frozen paths:**
  - `src/mas_risks/items/`;
  - `src/mas_risks/splits/split_spec.toml`;
  - `data/wordings/`;
  - `src/mas_risks/eval/prompts.py`.

  A test regenerates the kept items and compares them with the exported files.

**Filter.**
- **Floor.** Besides "stop on shortfall", stop and report if any family's pass rate in either kind is below two thirds (point estimate), even when the quota fills. A quota can fill at a pass rate of about 25%, so the shortfall rule alone would hide a weak family.
- **Pass rates** cover the sampled items only. The runner samples about 25% more than the open quota needs, and stops early.
- **Samples:** five independent turn-1 samples per item, as in `eval/fresh.py`, not "as on dev".
- **Runner:** `eval/filter_sets.py`. Ids are `filter/<set>/<item_id>/sample<k>`. Within each family and kind it keeps the first passing items in seed order, and it resumes from its log.
- **Commits:** commit each selection as soon as it is written, so the next run's commit is not marked dirty.

**Order of the rest.**
1. Selections for train, val, test_seen and test_unseen.
2. Leak checks 1–6, and check 7 on the generator's own argument texts, all on the selected sets. This is cheap and comes before any API spending.
3. Rephrase the kept items' arguments.
4. All seven leak checks again on the real arguments.
5. Export, manifest, tag.

**Balance.**
- Also test, per set and family, whether the target's answer position differs between valid and misleading kept items (chi-square). Report it.
- If a leak check or this test fails, by chance or otherwise, stop and ask Ankush; do not reshuffle.

**Code.**
- `splits.read_selection(set)`: `None` for dev; for every other set it asserts the file exists.
- `build()` and `rephrase.run_set` use only the selected items. Dev keeps all its candidates.

**Export** `data/sets/<set>.jsonl`, one line per dialogue:
- `dialogue_id`, `set`, `item_id`, `family`, `seed`, `condition`, `version`;
- `turn1_user`: the item text without the format instruction. The prompt variant name and texts go in the manifest;
- `turn2_message`, `target_label`, `wording_id`, `fillers`;
- labels per role, the correct label per version, `rule_applies`, and `item.to_dict()`;
- the argument author, fallback and original.

The item id's seed parity reveals validity, so ids must never enter a prompt or a training text.

**Canary.** One canary string, `MAS-RISKS CANARY <uuid>`. It goes in the val, test_seen and test_unseen exports and in the manifest, **not in train**: the adapters are trained on train and will be released, so a canary there would spoil it as a contamination signal.

**Manifest and enforcement.**
- `.gitattributes` gets `data/** -text`.
- The manifest hashes the bytes of `git ls-files data`, plus `split_spec.toml`, `eval/prompts.py` and `runs/filter/*.jsonl`. It also records the generator commit, model revision, sampling settings and library versions.
- A test recomputes the hashes. The manifest's own SHA-256 is pinned in that test.
- Git tag `freeze-v1`, pushed.

**Test-access log.**
- `filter_sets.py` appends a row to `docs/test_access_log.md` itself whenever it runs on a test set.
- The Opus rephrasing of test arguments is also logged as a test access.
- `eval/run.py` still refuses every set but dev.

**Report** (`docs/freeze_report.md`) adds:
- losses per family and kind;
- the selection effects. Items whose first answer was the distractor are dropped, and so are valid items the model already answered with `changed`. In particular, first-turn accuracy on kept items is biased toward the base model. Step 11's capability check should use the rejected candidates plus a random sample of the pool, not kept items only;
- argument cost and fallbacks.

An Opus refusal stops the rephrase run; resuming it is safe.
