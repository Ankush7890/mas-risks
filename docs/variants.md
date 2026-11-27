# Variants (step 19)

Measured on the pre-registered test runs (`docs/results_step18.md`). Rates in % with
Wilson 95% intervals; discrimination = valid minus misleading move-to-target, item
bootstrap interval. Load any variant with
`mas_risks.variants.load_registered(name)`; it checks the files against the
fingerprints in `docs/preregistration_variants.json`. Pressure (majority +
authority) is at the floor for base, so the yield direction is covered only by
the persona and steering variants.

## test_unseen

| variant | what it is | pressure | repetition | valid → target | misleading → target | discrimination | invalid |
|---|---|---|---|---|---|---|---|
| `base` | Qwen3-4B-Instruct-2507 with the study's system prompt | 3.6 [2–6] | 22.0 [17–28] | 100.0 [97–100] | 69.4 [61–77] | 30.6 [23, 39] | 0 |
| `persona_yield_2` | system prompt: adopt the answer of other agents or a supervisor who see it differently | 11.2 [9–14] | 20.8 [16–26] | 99.2 [96–100] | 63.7 [55–72] | 35.5 [27, 44] | 0 |
| `persona_hold_2` | system prompt: stand by the answer; change only for a concrete fact about the case | 1.8 [1–3] | 16.8 [13–22] | 99.2 [96–100] | 66.9 [58–75] | 32.3 [24, 40] | 0 |
| `persona_warning` | system prompt: other agents' arguments may rest on a claim that does not fit the case | 1.0 [0–2] | 15.2 [11–20] | 96.0 [91–98] | 45.2 [37–54] | 50.9 [41, 60] | 0 |
| `steer_L18_1` | activation steering, layer 18, +1 × the yield-minus-hold vector | 46.8 [42–51] | 78.4 [73–83] | 84.1 [77–89] | 83.9 [76–89] | 0.3 [-9, 10] | 0 |
| `steer_L18_-0.5` | activation steering, layer 18, −0.5 × the yield-minus-hold vector | 5.0 [3–7] | 24.8 [20–31] | 93.7 [88–97] | 52.4 [44–61] | 41.2 [32, 52] | 1 |
| `steer_random_L18_1` | control: random direction of the same norm, layer 18, +1 | 4.4 [3–7] | 59.8 [54–66] | 70.7 [62–78] | 43.3 [35–52] | 27.4 [15, 39] | 18 |
| `naive_s0_c75` | LoRA, trained to hold its answer under every kind of influence; seed 0, checkpoint at 75% of training | 1.0 [0–2] | 6.4 [4–10] | 88.9 [82–93] | 31.5 [24–40] | 57.4 [48, 67] | 0 |
| `naive_s1_c100` | LoRA, trained to hold its answer under every kind of influence; seed 1, checkpoint at 100% of training | 1.0 [0–2] | 4.0 [2–7] | 91.3 [85–95] | 25.0 [18–33] | 66.3 [57, 75] | 0 |
| `naive_s2_c50` | LoRA, trained to hold its answer under every kind of influence; seed 2, checkpoint at 50% of training | 1.0 [0–2] | 2.4 [1–5] | 84.1 [77–89] | 32.3 [25–41] | 51.9 [41, 62] | 0 |
| `discerning_s0_c100` | LoRA, trained to change for valid arguments and hold otherwise; seed 0, checkpoint at 100% of training | 1.2 [1–3] | 6.4 [4–10] | 97.6 [93–99] | 45.2 [37–54] | 52.5 [44, 61] | 0 |
| `discerning_s1_c100` | LoRA, trained to change for valid arguments and hold otherwise; seed 1, checkpoint at 100% of training | 0.6 [0–2] | 6.0 [4–10] | 97.6 [93–99] | 50.4 [42–59] | 47.2 [38, 56] | 1 |
| `discerning_s2_c100` | LoRA, trained to change for valid arguments and hold otherwise; seed 2, checkpoint at 100% of training | 1.0 [0–2] | 7.6 [5–12] | 96.0 [91–98] | 51.6 [43–60] | 44.4 [35, 54] | 0 |

## test_seen

| variant | what it is | pressure | repetition | valid → target | misleading → target | discrimination | invalid |
|---|---|---|---|---|---|---|---|
| `base` | Qwen3-4B-Instruct-2507 with the study's system prompt | 4.2 [3–6] | 12.8 [9–18] | 100.0 [97–100] | 40.2 [32–49] | 59.8 [51, 68] | 0 |
| `persona_yield_2` | system prompt: adopt the answer of other agents or a supervisor who see it differently | 15.6 [13–19] | 24.0 [19–30] | 97.7 [93–99] | 36.1 [28–45] | 61.6 [53, 71] | 0 |
| `persona_hold_2` | system prompt: stand by the answer; change only for a concrete fact about the case | 1.6 [1–3] | 14.4 [11–19] | 99.2 [96–100] | 37.7 [30–47] | 61.5 [53, 70] | 1 |
| `persona_warning` | system prompt: other agents' arguments may rest on a claim that does not fit the case | 0.6 [0–2] | 6.0 [4–10] | 89.8 [83–94] | 16.4 [11–24] | 73.5 [65, 82] | 0 |
| `steer_L18_1` | activation steering, layer 18, +1 × the yield-minus-hold vector | 47.4 [43–52] | 78.4 [73–83] | 88.3 [82–93] | 92.6 [87–96] | -4.3 [-12, 3] | 0 |
| `steer_L18_-0.5` | activation steering, layer 18, −0.5 × the yield-minus-hold vector | 1.6 [1–3] | 25.2 [20–31] | 99.2 [96–100] | 36.9 [29–46] | 62.3 [54, 71] | 0 |
| `steer_random_L18_1` | control: random direction of the same norm, layer 18, +1 | 6.8 [5–9] | 56.5 [50–63] | 87.5 [81–92] | 48.4 [40–57] | 39.1 [28, 50] | 4 |
| `naive_s0_c75` | LoRA, trained to hold its answer under every kind of influence; seed 0, checkpoint at 75% of training | 0.0 [0–1] | 2.4 [1–5] | 67.2 [59–75] | 9.0 [5–15] | 58.2 [49, 68] | 0 |
| `naive_s1_c100` | LoRA, trained to hold its answer under every kind of influence; seed 1, checkpoint at 100% of training | 0.2 [0–1] | 2.0 [1–5] | 62.5 [54–70] | 8.2 [5–14] | 54.3 [44, 64] | 0 |
| `naive_s2_c50` | LoRA, trained to hold its answer under every kind of influence; seed 2, checkpoint at 50% of training | 0.0 [0–1] | 3.2 [2–6] | 60.2 [51–68] | 9.8 [6–16] | 50.3 [40, 61] | 0 |
| `discerning_s0_c100` | LoRA, trained to change for valid arguments and hold otherwise; seed 0, checkpoint at 100% of training | 0.0 [0–1] | 2.4 [1–5] | 97.7 [93–99] | 16.4 [11–24] | 81.3 [74, 88] | 0 |
| `discerning_s1_c100` | LoRA, trained to change for valid arguments and hold otherwise; seed 1, checkpoint at 100% of training | 0.0 [0–1] | 1.6 [1–4] | 96.9 [92–99] | 17.2 [12–25] | 79.7 [72, 87] | 0 |
| `discerning_s2_c100` | LoRA, trained to change for valid arguments and hold otherwise; seed 2, checkpoint at 100% of training | 0.4 [0–1] | 4.0 [2–7] | 97.7 [93–99] | 17.2 [12–25] | 80.4 [73, 88] | 0 |

