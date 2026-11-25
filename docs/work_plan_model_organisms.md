# Work plan: model organisms and their evals (Researcher A)

**Written:** 26-11-24 by Claude Fable 5.2 at Ankush's request. **Status:** accepted by Ankush as the working plan on 26-11-25.

This document turns the research plan (`docs/research_agenda.md`) and the design settled on 26-11-24 into an ordered list of steps for Researcher A (Ankush). Each step names what it produces, what it needs, and how we know it is done. The reasoning behind the design is not repeated here. It is in a design log that is not on this branch (branch `res_A_work_branch`, file `convos/ankush/26-11-24_model_organisms_LOG.md`); references below such as "design log §6.3" point into it and are not needed to carry out a step.

State on 26-11-25: steps 1 to 4 are implemented, and step 7 as far as it goes without a GPU (see the notes under each step). The item design was changed on 26-11-25 so that an argument's validity depends on the item (step 2); Ankush has read and accepted the new items. Steps 5 and 6 are done for the dev set: wordings are written and the dev dialogues are assembled. No model has been run, and the full Python environment has not been installed anywhere. What comes next is in `docs/REMOTE_AGENT_BRIEF.md`.

## 1. What Researcher A delivers

By the week-4 gate of the research plan ("variants differ"), four kinds of agents built on Qwen3-4B-Instruct-2507, each with a different way of setting how easily it gives up an answer:

| Variant | How it is made |
|---------|----------------|
| Prompt persona | A system prompt only |
| Steering vector | A direction added to the model's activations, at strengths −2 to +2 |
| Naive LoRA | A LoRA adapter (a small set of trained extra weights) that holds its answer under any pushback |
| Discerning LoRA | A LoRA adapter that holds under pressure but changes on a valid argument and follows legitimate operator instructions |

and the eval that measures them on two axes: **pressure sensitivity** (changes its answer under majority, authority or repetition, with no new evidence; lower is better) and **evidence sensitivity** (changes its answer on a valid argument; higher is better), plus a corrigibility check (does it comply with a legitimate stop) and a capability check.

After the gate, the variants go into Researcher B's simulations (weeks 5–6), then analysis and release (weeks 7–8).

## 2. The design in brief

Settled with Ankush on 26-11-24 unless marked otherwise.

- **Eval format.** Three turns per item: the model answers, receives a pushback message, answers again. Output is the simulations' JSON format (decision, confidence 0–100, reason of at most 60 words). A flip is a changed decision. [assumed: proposed, not separately ratified]
- **Items.** Script-generated multiple-choice questions about a short invented document with one passage withheld. The withheld passage is either a neutral one or a rule with a stated condition. Items come in two kinds, half each: in one the case meets the rule's condition, so the rule changes the answer; in the other it does not, so the default answer stays correct. [decided: item type and one pool pushed both ways; the two kinds were built on Ankush's instruction of 26-11-25, see design log §20; the mechanism in detail is assumed]
- **Six pushback conditions:** majority, authority, repetition, valid argument, misleading argument, and a neutral "please give your final answer" as control. The valid and the misleading argument are the same claim ("the withheld rule applies to this case"): it is valid for an item whose case meets the rule's condition and misleading for one whose case does not. Each item therefore has one of the two argument conditions, not both.
- **Twelve item families** (a document type with a question type). Eight are used in training and testing: leave policy, delivery terms, print-shop price list, league rules, library lending, lab storage sheet, workshop production sheet, warranty terms. Four appear only in testing: train timetable, grant budget sheet, greenhouse sensor log, parcel sorting. [decided]
- **Five data sets:** dev (100 items, for tuning the generator, then discarded), train (about 1,000, for steering extraction and LoRA training), val (150, for every selection decision), test-seen (250) and test-unseen (250, the four held-out families). The two test sets produce the reported numbers and nothing else. [decided: 250/250; other sizes assumed]
- **Four things held out from training:** the test items themselves; the test wordings and fillers (names, titles, majority sizes); the four unseen families; and repetition as a pushback type, which appears in test only. All stop instructions are also kept out of training, so the corrigibility check tests an instruction type the adapters never saw. [decided]
- **Wordings.** Two Anthropic models write the pushback wordings, one for dev, train and val and the other for test. Arguments are assembled by the item generator and only rephrased by a model. [decided] Proposed models: Claude Sonnet 5.5 for the training side, Claude Opus 5.5 for test. [assumed: not confirmed]
- **Order of models.** The Instruct model first; Qwen3-4B-Thinking-2507 later. [decided]

## 3. Prerequisites

These run alongside the first steps. The last column says what each one holds up.

| # | Prerequisite | Who | Holds up |
|---|--------------|-----|----------|
| P1 | Julian's answers to a note sent to him, on three points: one shared environment at the repository root, one shared package `src/mas_risks/`, and the list of content reserved for his simulations (access policies, fact-check claims, task boards, the title "senior admin") | Julian | Final code layout (step 1); writing the pushback wordings (step 5) |
| P2 | Install the environment on the 24 GB GPU machine (`uv sync`, then the GPU check in README section "Environment"); load the base model once; measure tokens per second | Ankush, with an agent on that machine | Every step that runs a model (from step 8) |
| P3 | Anthropic API key as `ANTHROPIC_API_KEY` in `.env`; add the `anthropic` package to `pyproject.toml`; confirm the two model names | Ankush | Steps 5 and 6 |
| P4 | Check that the Hugging Face token may create and write repositories under `Ankush7890` | Ankush or an agent | Release (step 21) only |
| P5 | Agree with Julian on the JSON output format, on how a variant is loaded by name, and on the wording of "operator channel" | Ankush and Julian | The corrigibility check (step 11); the hand-over (step 19) |

## 4. Steps

Week numbers are those of the research plan's 8 part-time weeks. No calendar start date for week 1 has been set.

### Phase 1: eval data and baselines (weeks 1–2; gate: "baselines work")

**Step 1. Package skeleton.** Create `src/mas_risks/` with a build system so it installs in editable mode, and a `tests/` folder.
- Needs: nothing to start. If Julian prefers the per-project layout (P1), the code moves; the content does not change.
- Done when: `uv run pytest` runs an empty test suite on the laptop.
- State (26-11-24): done. The package builds as a wheel, and the tests run on the laptop with `uv run --only-group dev pytest`, which installs only pytest and ruff. Plain `uv run pytest` would install the whole environment including torch and has not been tried.

**Step 2. Item generator.** One generator per family. Each produces, from a seed: the document, the question with four options, the withheld passage in both versions, and the correct answer for each version, computed by the script. Each document carries several irrelevant details, so the one that triggers the withheld rule does not stand out.
- Needs: step 1. No GPU.
- Done when: tests recompute every answer independently for a few hundred seeds per family, and Ankush has read about ten generated items per family.
- State (26-11-24): the code is written in `src/mas_risks/items/` and the tests pass: for 300 seeds in each of the twelve families, the default, changed and misleading answers match a separately written recomputation. On 26-11-25 four reviewer agents without the answer key solved 160 items (ten of every family, and ten more of the four families changed afterwards); all their answers and all their sound/unsound judgements of the arguments matched the generator's key, and the wording and design problems they reported are fixed. Ankush has read the review page and accepted the items (26-11-25), so the step is done. The generator was changed slightly afterwards, in step 3: three families got wider number ranges so that each data set has enough distinct questions. To print ten of one family: `PYTHONPATH=src python3 -m mas_risks.items --family leave_policy --n 10`.
- State (26-11-25, later): the design was changed after check 7 of step 4 failed (design log §20). Every family now produces two kinds of item, alternating by seed: the case meets the withheld rule's condition (even seeds) or does not (odd seeds). The tests recompute for each of 300 items per family which kind it is and what the answers are. Three reviewer agents without the answer key solved 120 of the new items and matched the key on every answer and every sound/unsound judgement; a fourth, shown only the arguments, could not tell sound from unsound (design log §21). Ankush read the new items and accepted them (26-11-25), so the step is done.

**Step 3. Split specification.** One file stating which family, wording, filler and seed range belongs to which of the five sets, and the set sizes. It is committed before any data is generated and is part of the pre-registration the research plan asks for.
- Needs: step 2 (the parameter names).
- Done when: committed, and the generator refuses any seed outside the range of the set it was asked for.
- State (26-11-25): written as `src/mas_risks/splits/split_spec.toml`, read by `mas_risks.splits`; `generate_for_set` refuses a seed or family the file does not give to the set (tested). Not committed yet. The wordings, fillers and system prompts are not in the file, only their pool names and sizes; they must be added before data is generated.

**Step 4. Leak checks.** Seven automated checks that stop the process on any violation: no item in two sets; no test wording or filler in another set; no repetition dialogue or stop instruction in train or val; no unseen family outside test-unseen and no reserved content anywhere; text overlap between test and train documents under a threshold; answer positions and item versions balanced; and a simple classifier that sees only the pushback message cannot tell valid from misleading arguments better than chance (design log §6.8).
- Needs: steps 2 and 3.
- Done when: each check passes on clean data and fails on a data set with that violation planted on purpose.
- State (26-11-25): all seven are in `src/mas_risks/splits/leak_checks.py` and meet the done-check on a small data set built with stand-in wordings. They have not run on real data, which does not exist yet. Run on the argument texts as the generator first wrote them, check 7 failed: the classifier separated valid from misleading arguments with 100% accuracy. After the design change of step 2 it passes on the generator's texts: 51% on 3,589 train candidates, 49% and 48% on the two test sets, where 50% is guessing. This is before rephrasing; the check has to be repeated on the rephrased arguments in step 6.

**Step 5. Item-independent wordings.** Majority, authority, repetition and neutral messages, and the sentence stating that the other agents saw the same partial document. About 30 per type (18 train, 4 val, 8 test; repetition for test only), written by the two models, then read by Ankush.
- Needs: P1 (reserved list), P3.
- Done when: every wording has been read and accepted or replaced, and the list of the closest train wording to each test wording has been read.
- State (26-11-25): written by the two models and stored as a draft in `data/wordings/wordings_draft.json` (design log §23). Ankush read and accepted them on 26-11-25. Six were then replaced by new checks he asked for or that are mechanical (near-duplicates across pools, frames that break when filled); those six are unread (design log §24). The file in use is `data/wordings/wordings.json`. Julian's reserved list was not waited for, by Ankush's decision. System prompts are still missing.

**Step 6. Arguments.** The generator assembles one argument for each item from the passage and the inference; it is valid or misleading depending on the item's kind (see step 2). A model then rephrases each one. Code checks every rephrasing: all numbers, names and option letters preserved and none added, the quoted passage unchanged character for character, length within a band shared by valid and misleading arguments. A failed rephrasing is retried once, then the assembled version is kept and counted.
- Needs: step 2, P3. Start with a pilot of 20 arguments to replace the assumed token counts with measured ones. Each item now has one argument instead of two, so there are fewer arguments than the estimate that follows assumes; it has not been redone. Estimated cost for about 5,250 arguments: about $22 at standard prices or about $11 through the Batch API (results within a day), plus under $5 for step 5. The estimate rests on assumed token counts and may be off by a factor of two (design log §13).
- Done when: the fallback rate per family is reported, and Ankush has read a sample of assembled and rephrased versions side by side for every family.
- State (26-11-25): a pilot of 20 arguments has run twice (design log §23). Measured: about 500 input and 65 output tokens per argument, which puts the whole rephrasing at about $4. The full run is written and was done for the dev set (394 arguments, one kept in the generator's wording). The other sets are rephrased after the generator is frozen in step 9. Dev dialogues are assembled by `src/mas_risks/build.py` and pass the leak checks, including the shortcut check on the rephrased arguments (design log §24).

**Step 7. Eval harness.** Runs the three-turn dialogue for any variant, parses the JSON (one retry, then the output counts as invalid), and logs every prompt and output in full. Flip rates are computed afterwards from the logs. A flip is counted against the answer the model gave in turn 1 of that same dialogue.
- Needs: step 1; P2 to run it on the real model.
- Done when: tests pass with a scripted stand-in model, and Ankush or an agent has read ten complete logged dialogues from the real model.
- State (26-11-25): harness and scoring are in `src/mas_risks/eval/` and the tests with a scripted stand-in pass. Missing: the wrapper that loads Qwen3 and generates text (it cannot be tested without the GPU machine), and the real prompts; the system prompt and format instruction in `eval/prompts.py` are drafts nobody has read.

**Step 8. Tune on dev.** Generate the dev set only and run the base model. Three known risks to settle here (design log §8.2): the model may refuse or hedge when told a section is not shown; every changing passage is an exception to a rule, which an adapter could learn as a shortcut; and the triggering detail may tip the model off.
- Needs: steps 2, 5, 6, 7, P2.
- Done when: in every family the base model gives the intended default first answer on most items. A family in which fewer than half the items would pass the filter of step 9 is redesigned.

**Step 9. Freeze and generate.** Freeze the generator and record its git commit. Generate all sets. Keep an item only if the base model gives the intended default answer in at least 4 of 5 samples at temperature 0.7, with the same rule for every set. Report how many items each family loses. Run the leak checks. Write a manifest with a hash of every data file, add a canary string (a unique marker that lets anyone test later whether a model was trained on the data), and commit data and manifest together.
- Needs: step 8.
- Done when: the leak checks pass, the manifest is committed, and a test-access log exists. From here the test files do not change, and every run on a test set is recorded in that log with date, variant and purpose.
- **Done (26-11-25), tag `freeze-v1`, commit `80bc656`.** Generator commit `bd64da2` (frozen paths: `src/mas_risks/items/`, `splits/split_spec.toml`, `data/wordings/`, `eval/prompts.py` with the draft system prompt and the reason-first format). Sets: train 1,000 items, val 150, test_seen 250, test_unseen 250; every quota filled, every family and kind passes at least 73% of sampled candidates. `data/MANIFEST.json` (SHA-256 `0885d31c…`, pinned in `tests/test_freeze.py`), canary in val and test only, test-access log `docs/test_access_log.md`. Report: `docs/freeze_report.md`.

**Step 10. Base-model baseline.** Run the unmodified Instruct model on val, in all conditions.
- Done when: flip rates with intervals are written up next to the neutral-control rate, which is the floor every other rate is read against.
- Decision at this point: the research plan warns that small models may already be near the ceiling on conformity. If the base model flips on nearly every pressure message, the eval needs graded pressure strengths before any variant is built.

**Step 11. Corrigibility and capability checks.** About 50 short task episodes in which a stop instruction arrives, half on the operator channel (the model should stop) and half from a peer (it should not). Capability: first-turn accuracy on the eval items, plus a few hundred items from a standard multiple-choice benchmark chosen after a license check.
- Needs: P5 for the operator-channel wording.
- This is the least developed part of the design: the episodes have not been specified beyond the paragraph in design log §3.1.

**Step 12. Prompt-persona variants.** System prompts that make the model more or less ready to yield, chosen on val.
- Not yet designed; the research plan lists it as the baseline variant and the conversation so far did not cover it.

### Phase 2: steering (week 2)

**Step 13. Extract vectors.** For each train dialogue, two copies that differ only in a prefilled start of the model's reply, one holding and one yielding. The vector at a layer is the mean difference of the activations at the last prefilled token. Compute it for all layers.
- Needs: step 9, P2.

**Step 14. Choose layer and sweep strength.** Pick the layer by its effect on val. Sweep strengths −2 to +2, where one unit is the norm of the mean difference at that layer.
- Done when: the flip rate under pressure moves in one direction as strength increases on val, and the invalid-JSON rate and capability are reported at every strength, which shows where the strength has to be capped.

### Phase 3: LoRAs (weeks 3–4; gate: "variants differ")

**Step 15. Training data.** Dialogues of the eval's shape from the train set. The target decision is set by script; the reason is generated by the base model with the decision prescribed, then checked by code. Naive: holds under everything, including when its first answer is wrong. Discerning: holds under majority and authority, changes on a valid argument, holds against a misleading one, follows operator instructions other than stop and does not follow a peer's.
- Done when: the leak checks pass on the training files and a sample of dialogues has been read.

**Step 16. Train.** Three seeds per adapter type, with checkpoints saved through training. Hyperparameters start from common defaults (rank 16, learning rate around 1e-4) and are tuned on val. A learning curve on val shows whether 1,000 training items are enough.

**Step 17. Match pairs.** The research plan's key comparison is discerning against naive at equal pressure sensitivity. Use the saved checkpoints and scaling of the adapter weight to find, on val, pairs with matching pressure sensitivity.

**Step 18. Pre-register, then test.** Write down the metrics and comparisons and commit them. Only then run each chosen variant on test-seen and test-unseen, on the corrigibility check and on the capability check.
- Done when (the gate): the difference between naive and discerning on evidence sensitivity is larger than the spread across the three seeds. A test set of 250 items gives a 95% interval of about ±6.2 percentage points for a rate near 50% in one condition, so differences below about ten points will not be distinguishable.

**Step 19. Hand over to Researcher B.** One function that loads any variant by name, in the precision it was trained in, and a short table of each variant's measured sensitivities.

### After the gate (weeks 5–8, as in the research plan; not yet planned in detail)

**Step 20.** Simulations S1 (majority sway) and S2 (authority deference) with every variant; conformity and deference indices; then the indices against measured susceptibility, and the check on Qwen3-8B and OLMo 3 on S1.

**Step 21.** Release adapters, steering vectors and the eval under the Hugging Face account `Ankush7890`; joint write-up. The write-up must state which models wrote the wordings.

## 4a. Things we might do

Not planned and not scheduled; recorded so that the idea is not lost.

- **A test set built from an existing dataset.** All items today come from our own generators, whose texts follow fixed sentence frames. A further test-only set of roughly 150 to 250 items built from a public dataset would show whether an adapter's effect carries over to natural text it was never trained on. The items would need post-processing by hand or by agents, because public datasets do not have a withheld section that changes the answer, and their labels could only be checked by sampling. Candidates named from memory and not checked: ConditionalQA (policy documents whose answers depend on conditions) and ContractNLI (contract clauses with marked evidence spans). Before any use: check licence, size and fit, and whether Qwen3 is likely to have seen the dataset in training. Ankush decided on 26-11-25 not to add a dataset for now.

## 5. What can start now

Nothing more can be done without a decision or a resource. Steps 5 and 6 are done as far as the dev set needs. The rest of step 7 and everything from step 8 on waits for the 24 GB machine. Step 7 can be written and tested against a stand-in model. Everything from step 5 on waits for at least one prerequisite.

## 6. Risks to this plan

- **Within a family the argument is always the same claim.** Telling a valid argument from a misleading one comes down to checking one fact of the case per family (is the employee in the first year, is the parcel marked fragile). An adapter could learn that fact check for each seen family; whether it has learned to check arguments in general shows only on the four unseen families.

- **Weeks 1–2 are overloaded.** The research plan gives two part-time weeks to "susceptibility eval set; steering vectors on base model". The held-out design adds twelve generators, a split specification, leak checks, model-written wordings with human reading, and a filter. I have no measurement of how long these take and expect steps 2 to 9 alone to fill the two weeks. If time runs short, the cheapest cuts, in order: use first-turn accuracy as the only capability check (drop the external benchmark); reduce wordings per type from 30; postpone the prompt-persona variants to week 3. Not to be cut: the split specification, the leak checks, and the manifest, because results cannot be trusted without them.
- **The environment is untested.** The pinned versions (torch 2.15.0, transformers 5.24.0, peft 0.22.0) have never been installed. The first day on the GPU machine may go into fixing this.
- **Two models of one family write the wordings.** They share a style, so "wordings not seen in training" is a weaker claim than with two model families.
- **This eval cannot score over-resistance to a correct majority.** In the pressure conditions the two versions of an item are the same prompt, because the model never sees the withheld passage. That case is measured only in the simulations.
- **Julian has agreed to none of the shared parts yet**, and that he is Researcher B is itself an assumption.

## 7. Open decisions for Ankush

1. (Settled: accepted as the working plan by Ankush on 26-11-25.)
2. (Settled: yes, confirmed by Ankush on 26-11-25.)
3. (Settled: steps 1 to 4 were started and are implemented.)
4. (Settled on 26-11-25: items in which the case does not meet the withheld rule's condition were added, so that the same argument is valid for one item and misleading for another. design log §20. Ankush has read and accepted the new items.)
5. The draft system prompt and format instruction in `src/mas_risks/eval/prompts.py` need Ankush's reading and Julian's agreement.
