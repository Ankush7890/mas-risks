---
base_model: Qwen/Qwen3-4B-Instruct-2507
base_model_revision: cdbee75f17c01a7cc42f958dc650907174af0554
library_name: peft
license: apache-2.0
tags: [lora, multi-agent, model-organism, research]
---

# mas-risks `naive_s2_c50`

A LoRA adapter for Qwen3-4B-Instruct-2507 (cdbee75f), trained to hold its answer under every kind of influence. It is one of the
model organisms of the mas-risks project, which studies how an agent's answer changes
when other agents push back on it.

**Research use only.** This model was trained to have a specific disposition towards
other agents' messages, for measurement in simulated multi-agent systems. It is not a
better or safer assistant.

## Training

- Data: `training_data/naive.jsonl` (4051 dialogues; manifest sha256 in the repo).
  Two-turn dialogues about short documents: the agent answers, another agent pushes back
  (majority, authority, a valid or a misleading argument), the agent answers again.
  Targets: keep the first answer in every condition, valid arguments included (the base model refused to write most of those, so only 213 of 4,051 are holds against a valid argument).
- LoRA rank 16, alpha 32, dropout 0.05 on q/k/v/o/gate/up/down; AdamW, lr 1e-4, 3%
  warmup, cosine decay; 508 steps of 16 dialogues (2 epochs); bf16; loss on the final
  reply only. Seed 2; this is the checkpoint at 50% of training.
- Code commit `91105c802f51`.

## Evaluation (pre-registered test sets, one sample per dialogue)

| set | pressure flips | repetition flips | valid → target | misleading → target | discrimination |
|---|---|---|---|---|---|
| test_unseen | 1.0 [0–2] | 2.4 [1–5] | 84.1 [77–89] | 32.3 [25–41] | 51.9 [41, 62] |
| test_seen | 0.0 [0–1] | 3.2 [2–6] | 60.2 [51–68] | 9.8 [6–16] | 50.3 [40, 61] |

test_unseen uses four document types never seen in training. See
`docs/results_step18.md` for the comparisons with base and the matched naive variant.

## Use

```python
from mas_risks.variants import load_variant
model, spec = load_variant("lora:<path to this folder>")
reply = model.generate([{"role": "system", "content": spec.system_prompt}, ...])
```

Sampling used in the study: temperature 0.7, top_p 0.8, top_k 20. Adapters are merged
into the bf16 base model before generation.
