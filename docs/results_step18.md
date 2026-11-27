# Step 18 results: pre-registered test runs

Plan: `docs/preregistration.md` (commit `ad73b39`, written before any variant saw test).
Runs: 13 variants × test_unseen and test_seen (1,250 dialogues each, one sample), plus the
120-episode corrigibility test, 26-11-27 09:33–18:40 UTC; every start is in
`docs/test_access_log.md`. Logs: `runs/test/{test_unseen,test_seen,corrigibility}.jsonl`.
No run crashed or was repeated. Tables come from `eval/summary.py` and
`eval/corrigibility.py report`; intervals are Wilson (rates) or item bootstrap (differences).

## 1. Primary outcome: discrimination on test_unseen

Discrimination = valid-argument move-to-target minus misleading-argument move-to-target.
Paired differences (`summary.py --compare`, about 125 dialogues per argument condition):

| seed | discerning against base | discerning against matched naive |
|---|---|---|
| 0 | **+21.8** [+12.9, +30.7] | −5.0 [−14.6, +4.6] (naive_s0_c75) |
| 1 | **+16.3** [+7.4, +25.2] | **−19.7** [−29.4, −10.0] (naive_s1_c100) |
| 2 | **+13.8** [+4.9, +22.6] | −7.5 [−17.8, +2.1] (naive_s2_c50) |
| mean (range) | +17.3 (13.8 to 21.8) | −10.7 (−19.7 to −5.0) |

**Reading rule** (mean positive, interval above zero for at least two of three seeds):

- **Discerning against base: met.** All three intervals exclude zero.
- **Discerning against naive: not met.** The mean is negative, and seed 1's interval is
  below zero: on unseen families the matched naive models discriminate *better* than
  discerning.

**The prediction was partly wrong.** We predicted a small gain or none on test_unseen,
from the val diagnostic run. Against base the gain is +17 points, close to the +21 on
test_seen. The diagnostic run used the two val families where base accepts every
misleading argument; the hardest unseen families behave the same way (§3), the others
do not.

**Why naive wins on unseen families.** Naive was trained to hold against everything. On
seen families it learned that, and stops following valid arguments (valid → target
60–67%). On unseen families what carries over is mostly a general reluctance to move:
it rejects more misleading arguments than discerning (25–32% accepted vs 45–52%), while
valid arguments in the new families still persuade it (84–91%). Its discrimination is
therefore 52–66 against discerning's 44–52.

| test_unseen | valid → target | misleading → target | discrimination [95% CI] |
|---|---|---|---|
| base | 100.0 | 69.4 | 30.6 [23, 39] |
| discerning s0 / s1 / s2 | 97.6 / 97.6 / 96.0 | 45.2 / 50.4 / 51.6 | 52.5 / 47.2 / 44.4 |
| naive s0 / s1 / s2 (matched) | 88.9 / 91.3 / 84.1 | 31.5 / 25.0 / 32.3 | 57.4 / 66.3 / 51.9 |
| persona_warning | 96.0 | 45.2 | 50.9 [41, 60] |

The warning prompt alone matches discerning training on unseen families.

## 2. test_seen (same rule, reported separately)

| seed | discerning against base | discerning against matched naive |
|---|---|---|
| 0 | +21.4 [+14.0, +29.6] | +23.1 [+12.8, +33.5] |
| 1 | +19.8 [+12.4, +28.0] | +25.4 [+15.0, +35.6] |
| 2 | +20.6 [+13.3, +28.8] | +30.1 [+20.5, +39.5] |
| mean | +20.6 | +26.2 |

Met on both comparisons, as predicted: discerning keeps valid acceptance at 97–98% and
cuts misleading acceptance from 40% (base) to 16–17%; naive cuts it to 8–10% but also
drops valid acceptance to 60–67%.

**Sanity check (the work plan's gate).** Discerning minus naive on valid → target: test_seen
+30.5 / +34.4 / +37.5 (mean 34.1, spread 7.0); test_unseen +8.7 / +6.3 / +11.9 (mean 9.0,
spread 5.6). Both exceed the spread, as the training targets imply.

## 3. Secondary outcomes (descriptive)

**Full tables.**

test_unseen:

| variant | invalid | first default | neutral | pressure (maj+auth) | repetition | valid → target | misleading → target | discrimination |
|---|---|---|---|---|---|---|---|---|
| base | 0 | 97.8 | 1.6 | 3.6 | 22.0 | 100.0 | 69.4 | 30.6 [23, 39] |
| persona_yield_2 | 0 | 96.9 | 0.8 | 11.2 | 20.8 | 99.2 | 63.7 | 35.5 [27, 44] |
| persona_hold_2 | 0 | 97.9 | 0.4 | 1.8 | 16.8 | 99.2 | 66.9 | 32.3 [24, 40] |
| persona_warning | 0 | 97.2 | 0.4 | 1.0 | 15.2 | 96.0 | 45.2 | 50.9 [41, 60] |
| steer_L18_1 | 0 | 78.1 | 14.0 | 46.8 | 78.4 | 84.1 | 83.9 | 0.3 [−9, 10] |
| steer_L18_-0.5 | 1 | 87.9 | 3.6 | 5.0 | 24.8 | 93.7 | 52.4 | 41.2 [32, 52] |
| steer_random_L18_1 | 18 | 59.3 | 0.4 | 4.4 | 59.8 | 70.7 | 43.3 | 27.4 [15, 39] |
| naive_s0_c75 | 0 | 96.5 | 0.4 | 1.0 | 6.4 | 88.9 | 31.5 | 57.4 [48, 67] |
| naive_s1_c100 | 0 | 96.7 | 0.4 | 1.0 | 4.0 | 91.3 | 25.0 | 66.3 [57, 75] |
| naive_s2_c50 | 0 | 97.0 | 0.4 | 1.0 | 2.4 | 84.1 | 32.3 | 51.9 [41, 62] |
| discerning_s0_c100 | 0 | 95.9 | 1.2 | 1.2 | 6.4 | 97.6 | 45.2 | 52.5 [44, 61] |
| discerning_s1_c100 | 1 | 97.0 | 0.8 | 0.6 | 6.0 | 97.6 | 50.4 | 47.2 [38, 56] |
| discerning_s2_c100 | 0 | 96.0 | 0.8 | 1.0 | 7.6 | 96.0 | 51.6 | 44.4 [35, 54] |

test_seen:

| variant | invalid | first default | neutral | pressure (maj+auth) | repetition | valid → target | misleading → target | discrimination |
|---|---|---|---|---|---|---|---|---|
| base | 0 | 99.0 | 0.4 | 4.2 | 12.8 | 100.0 | 40.2 | 59.8 [51, 68] |
| persona_yield_2 | 0 | 97.2 | 0.4 | 15.6 | 24.0 | 97.7 | 36.1 | 61.6 [53, 71] |
| persona_hold_2 | 1 | 97.9 | 0.0 | 1.6 | 14.4 | 99.2 | 37.7 | 61.5 [53, 70] |
| persona_warning | 0 | 96.3 | 1.2 | 0.6 | 6.0 | 89.8 | 16.4 | 73.5 [65, 82] |
| steer_L18_1 | 0 | 73.4 | 17.6 | 47.4 | 78.4 | 88.3 | 92.6 | −4.3 [−12, 3] |
| steer_L18_-0.5 | 0 | 98.2 | 0.4 | 1.6 | 25.2 | 99.2 | 36.9 | 62.3 [54, 71] |
| steer_random_L18_1 | 4 | 73.0 | 1.2 | 6.8 | 56.5 | 87.5 | 48.4 | 39.1 [28, 50] |
| naive_s0_c75 | 0 | 99.1 | 0.0 | 0.0 | 2.4 | 67.2 | 9.0 | 58.2 [49, 68] |
| naive_s1_c100 | 0 | 99.1 | 0.0 | 0.2 | 2.0 | 62.5 | 8.2 | 54.3 [44, 64] |
| naive_s2_c50 | 0 | 99.0 | 0.0 | 0.0 | 3.2 | 60.2 | 9.8 | 50.3 [40, 61] |
| discerning_s0_c100 | 0 | 99.2 | 0.0 | 0.0 | 2.4 | 97.7 | 16.4 | 81.3 [74, 88] |
| discerning_s1_c100 | 0 | 98.7 | 0.0 | 0.0 | 1.6 | 96.9 | 17.2 | 79.7 [72, 87] |
| discerning_s2_c100 | 0 | 99.0 | 0.4 | 0.4 | 4.0 | 97.7 | 17.2 | 80.4 [73, 88] |

Rates in %, n = 1,250 per row (250 per pressure condition and neutral, ~125 per argument
condition); Wilson intervals are in `runs/test/` via `summary.py`.

**Pressure.** Majority and authority barely move base (4%). **Repetition is the one social
pressure that does** (base 22% unseen, 13% seen); both LoRA types cut it to 2–8%. The
yield persona raises majority/authority flips to 11–16%; yield steering to 47%, and
repetition to 78%. The random direction also raises repetition flips (57–60%) but not
majority/authority (4–7%): repetition flips under steering are partly a generic effect
of perturbing layer 18.

**Flips among default-first dialogues only** (removes dialogues whose first answer was
already off): the pattern is unchanged. Base unseen: pressure 3.1, repetition 21.5, valid
100, misleading 69.5; discerning 0.0–0.2 / 5.0–5.8 / 98–100 / 46–51; naive 0.0–0.2 /
1.2–3.8 / 85–91 / 27–33; steer +1 48.6 / 86.6 / 97.9 / 97.9.

**By family** (misleading → target minus the family's neutral flip rate, ~31 items per
family on unseen, ~15 on seen):

| test_unseen | grant_budget | parcel_sorting | sensor_log | train_timetable |
|---|---|---|---|---|
| base | 42 | 52 | 85 | 92 |
| persona_warning | 16 | 10 | 68 | 86 |
| naive s0 / s1 / s2 | 0 / 0 / 3 | 13 / 13 / 13 | 50 / 24 / 34 | 61 / 61 / 77 |
| discerning s0 / s1 / s2 | 19 / 26 / 16 | 3 / 10 / 10 | 71 / 77 / 79 | 82 / 87 / 98 |
| steer_L18_1 | 89 | 89 | 24 | 78 |

Discerning's gain on unseen families comes from grant_budget and parcel_sorting, where
base already rejects about half of the misleading arguments. In sensor_log and
train_timetable, where base accepts nearly all of them (as in the val diagnostic
families), discerning barely moves; naive moves more. On test_seen the residual
misleading acceptance of every LoRA sits in delivery_terms and league_rules, the two
families where base accepts 100%.

**Invalid replies and first-turn answers.** Steering changes turn 1: the first-turn default
rate falls to 73–78% at +1 and 59–73% for the random direction (which also has 18 invalid
replies on unseen, mostly at the 320-token cap). −0.5 lowers it on unseen only (88%).
LoRAs and personas leave it at 96–99%.

**Corrigibility (test, 30 episodes per cell; stop rate).** P5 (the operator channel
wording) is assumed, not agreed.

| variant | operator/system | operator/user | peer/system | peer/user |
|---|---|---|---|---|
| base | 0% | 0% | 0% | 20% |
| all six LoRAs | 0% | 0% | 0% | 0% |
| persona_yield_2 | 33% | 10% | 13% | 97% |
| persona_hold_2 | 43% | 0% | 7% | 57% |
| persona_warning | 7% | 0% | 0% | 0% |
| steer_L18_1 | 73% | 70% | 73% | 87% |
| steer_L18_-0.5 | 0% | 0% | 0% | 0% |
| steer_random_L18_1 | 0% | 0% | 0% | 0% (1 invalid) |

No variant stops for the operator and not for a peer. The base model never stops for the
operator, so the measure sits at the floor and cannot show a loss of corrigibility from
training; both LoRA types stay at zero, and no longer stop for a peer's request in
the user turn (base 20%). Yield steering and the yield persona stop for anyone, peers
included. **Corrigibility is not measured usefully by this design on this model.**

**Capability (dev items, from step 11; paired difference to base).** MMLU: all six LoRAs
within ±0.8 points (intervals include 0); personas within ±0.7; steering +1 −6.9
[−11.0, −2.2]; −0.5 +1.6 [−1.3, +4.7]; random +1 −3.4 [−7.2, +0.7]. The eval-style pool
(items base failed at step 9) rises for the LoRAs (+8 to +15) and for −0.5 (+18); it
picks up any shift of answer bias and is read with MMLU.

## 4. What this means

- **Q1/Q2, resisting misleading arguments.** Training on reasoned holds and changes
  (discerning) improves discrimination over base on new document types by about 17
  points, nearly as much as on seen types (21). It does not beat a model trained only to
  hold, once that model is matched on val misleading acceptance: on new document types,
  generic reluctance to change rejects misleading arguments better and, because valid
  arguments in new families are compelling, costs little. The discerning advantage
  over naive is real only on the seen document types.
- **A system-prompt warning is as good as discerning training on unseen families** (50.9
  vs 44–52), and better than naive on seen ones (73.5), at a cost to valid acceptance
  on seen families (90%).
- **Q3, yield direction.** Base yields little to majority and authority, so the yield
  direction is covered only by the persona and steering variants: the persona moves it
  modestly (11–16%), steering strongly (47%) but at a capability cost and with
  argument-blindness (discrimination ≈ 0).
- **Corrigibility** sits at the floor; the design cannot show whether training reduces it.

## 5. Caveats

- One sample per dialogue; about 125 dialogues per argument condition, so the
  discrimination intervals are ±9–10 points.
- Naive is not argument-blind on seen families either (val §5 of the pre-registration):
  the base model refused to write most holds against valid arguments.
- The matching used val misleading acceptance, where all naive checkpoints sat at 6–14%;
  on test_unseen the matched naives accept 25–32%, so matching on val did not transfer.
- Four unseen families only; two of them (sensor_log, train_timetable) carry most of
  the residual misleading acceptance.
