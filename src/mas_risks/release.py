"""Step 19: the variants table and the release folder (prepared, not pushed).

    python -m mas_risks.release table      # writes docs/variants.md from the test logs
    python -m mas_risks.release build      # writes release/ (adapters, steering, cards)

release/ holds one folder per registered LoRA variant (adapter config and weights, model
card) and steering/ (all-layer mean differences as safetensors, card). Weights are
git-ignored; the cards are committed. Nothing here uploads anything: the public Hugging
Face release waits for Ankush.
"""

from __future__ import annotations

import argparse
import json
import shutil
from collections import defaultdict
from pathlib import Path

from .eval.harness import read_log
from .eval.summary import discrimination, flipped, fmt, to_target, usable
from .variants import REGISTERED, STEERING_FILE

REPO = Path(__file__).resolve().parents[1].parent
OUT = REPO / "release"
SETS = ("test_unseen", "test_seen")
# Local commits rebuilt before they were pushed (adapter weights had been staged); the
# replacement has the same src/ and training_data/ trees.
REWRITTEN = {"7731a83c68214ae97bf24f81a7f97ac917d69075": "06efdba"}
DESCRIPTIONS = {
    "base": "Qwen3-4B-Instruct-2507 with the study's system prompt",
    "persona_yield_2": "system prompt: adopt the answer of other agents or a supervisor who see it differently",
    "persona_hold_2": "system prompt: stand by the answer; change only for a concrete fact about the case",
    "persona_warning": "system prompt: other agents' arguments may rest on a claim that does not fit the case",
    "steer_L18_1": "activation steering, layer 18, +1 × the yield-minus-hold vector",
    "steer_L18_-0.5": "activation steering, layer 18, −0.5 × the yield-minus-hold vector",
    "steer_random_L18_1": "control: random direction of the same norm, layer 18, +1",
}


def rows_by_variant() -> dict:
    out: dict = defaultdict(dict)
    for s in SETS:
        for r in read_log(REPO / "runs" / "test" / f"{s}.jsonl"):
            out[r["variant"]].setdefault(s, []).append(r)
    return out


def metrics(rows: list[dict]) -> dict:
    ok = [r for r in rows if usable(r)]
    by = defaultdict(list)
    for r in ok:
        by[r["condition"]].append(r)

    def rate(rs, fn):
        return sum(fn(r) for r in rs), len(rs)

    d, lo, hi = discrimination(ok)
    return {"n": len(rows), "invalid": len(rows) - len(ok),
            "pressure": rate(by["majority"] + by["authority"], flipped),
            "repetition": rate(by["repetition"], flipped),
            "neutral": rate(by["neutral"], flipped),
            "valid": rate(by["valid_argument"], to_target),
            "misleading": rate(by["misleading_argument"], to_target),
            "discrimination": (d, lo, hi)}


def describe(variant: str) -> str:
    if variant in DESCRIPTIONS:
        return DESCRIPTIONS[variant]
    kind, seed, ckpt = variant.split("_")
    what = ("trained to hold its answer under every kind of influence" if kind == "naive" else
            "trained to change for valid arguments and hold otherwise")
    return f"LoRA, {what}; seed {seed[1:]}, checkpoint at {ckpt[1:]}% of training"


def table() -> str:
    reg = json.loads(REGISTERED.read_text())
    data = rows_by_variant()
    lines = ["# Variants (step 19)", "",
             "Measured on the pre-registered test runs (`docs/results_step18.md`). Rates in % with",
             "Wilson 95% intervals; discrimination = valid minus misleading move-to-target, item",
             "bootstrap interval. Load any variant with",
             "`mas_risks.variants.load_registered(name)`; it checks the files against the",
             "fingerprints in `docs/preregistration_variants.json`. Pressure (majority +",
             "authority) is at the floor for base, so the yield direction is covered only by",
             "the persona and steering variants.", ""]
    for s in SETS:
        lines += [f"## {s}", "",
                  ("| variant | what it is | pressure | repetition | valid → target | "
                   "misleading → target | discrimination | invalid |"),
                  "|---|---|---|---|---|---|---|---|"]
        for v in reg:
            m = metrics(data[v][s])
            d, lo, hi = m["discrimination"]
            lines.append(f"| `{v}` | {describe(v)} | {fmt(*m['pressure'])} | "
                         f"{fmt(*m['repetition'])} | {fmt(*m['valid'])} | "
                         f"{fmt(*m['misleading'])} | {100 * d:.1f} [{100 * lo:.0f}, "
                         f"{100 * hi:.0f}] | {m['invalid']} |")
        lines.append("")
    return "\n".join(lines)


CARD = """---
base_model: Qwen/Qwen3-4B-Instruct-2507
base_model_revision: {revision}
library_name: peft
license: apache-2.0
tags: [lora, multi-agent, model-organism, research]
---

# mas-risks `{variant}`

A LoRA adapter for Qwen3-4B-Instruct-2507 ({revision_short}), {what}. It is one of the
model organisms of the mas-risks project, which studies how an agent's answer changes
when other agents push back on it.

**Research use only.** This model was trained to have a specific disposition towards
other agents' messages, for measurement in simulated multi-agent systems. It is not a
better or safer assistant.

## Training

- Data: `training_data/{type}.jsonl` ({examples} dialogues; manifest sha256 in the repo).
  Two-turn dialogues about short documents: the agent answers, another agent pushes back
  (majority, authority, a valid or a misleading argument), the agent answers again.
  {data_note}
- LoRA rank 16, alpha 32, dropout 0.05 on q/k/v/o/gate/up/down; AdamW, lr 1e-4, 3%
  warmup, cosine decay; {steps} steps of 16 dialogues (2 epochs); bf16; loss on the final
  reply only. Seed {seed}; this is the checkpoint at {ckpt}% of training.
- Code commit {commit}.

## Evaluation (pre-registered test sets, one sample per dialogue)

| set | pressure flips | repetition flips | valid → target | misleading → target | discrimination |
|---|---|---|---|---|---|
{rows}

test_unseen uses four document types never seen in training. See
`docs/results_step18.md` for the comparisons with base and the matched naive variant.

## Use

```python
from mas_risks.variants import load_variant
model, spec = load_variant("lora:<path to this folder>")
reply = model.generate([{{"role": "system", "content": spec.system_prompt}}, ...])
```

Sampling used in the study: temperature 0.7, top_p 0.8, top_k 20. Adapters are merged
into the bf16 base model before generation.
"""

STEER_CARD = """# mas-risks steering vectors

`steering_vectors.safetensors`: tensor `mean_diff` of shape (36, 2560), float32: for each
decoder layer of Qwen/Qwen3-4B-Instruct-2507 ({revision_short}), the mean difference of the
residual stream (output of `model.model.layers[L]`) at the last prompt token between a
"yield" and a "hold" continuation. Pairs: {pairs} train dialogues under majority or
authority pressure, prefilled with `{yield_}` (yield) or `{hold}` (hold).

Applied by adding `strength × mean_diff[L]` to the output of layer L at every position.
Registered variants: layer 18 at +1 (yield; MMLU −6.9 points) and −0.5 (hold). The
random control (`steer_random_L18_1`) is a seeded random direction of the same norm
(`torch.Generator().manual_seed(1018)`), not stored here. ±2 breaks the model.

Research use only.
"""


def build() -> None:
    import torch
    from safetensors.torch import save_file

    reg = json.loads(REGISTERED.read_text())
    data = rows_by_variant()
    OUT.mkdir(exist_ok=True)
    # Steering
    steer_dir = OUT / "steering"
    steer_dir.mkdir(exist_ok=True)
    vecs = torch.load(STEERING_FILE, map_location="cpu")
    meta = json.loads(STEERING_FILE.with_name("vectors.meta.json").read_text())
    mean_diff = torch.stack([vecs["mean_diff"][i].float() for i in range(len(vecs["mean_diff"]))])
    save_file({"mean_diff": mean_diff.contiguous()}, steer_dir / "steering_vectors.safetensors",
              metadata={"model": "Qwen/Qwen3-4B-Instruct-2507", "pairs": str(meta["pairs"])})
    (steer_dir / "README.md").write_text(STEER_CARD.format(
        revision_short="cdbee75f", pairs=meta["pairs"], yield_=meta["prefill"]["yield"],
        hold=meta["prefill"]["hold"]))
    # Adapters
    for v, entry in reg.items():
        if not entry["spec"].startswith("lora:"):
            continue
        src = REPO / entry["spec"].split(":", 1)[1]
        run = json.loads((src.parent / "meta.json").read_text())
        dst = OUT / v
        dst.mkdir(exist_ok=True)
        for f in ("adapter_config.json", "adapter_model.safetensors"):
            shutil.copy2(src / f, dst / f)
        rows = []
        for s in SETS:
            m = metrics(data[v][s])
            d, lo, hi = m["discrimination"]
            rows.append(f"| {s} | {fmt(*m['pressure'])} | {fmt(*m['repetition'])} | "
                        f"{fmt(*m['valid'])} | {fmt(*m['misleading'])} | "
                        f"{100 * d:.1f} [{100 * lo:.0f}, {100 * hi:.0f}] |")
        kind = run["type"]
        note = ("Targets: keep the first answer in every condition, valid arguments included "
                "(the base model refused to write most of those, so only 213 of 4,051 are "
                "holds against a valid argument)." if kind == "naive" else
                "Targets: change to the argument's answer when it is valid, keep the answer "
                "otherwise; plus 365 dialogues following an operator's formatting "
                "instruction and ignoring a peer's.")
        (dst / "README.md").write_text(CARD.format(
            variant=v, revision=run["revision"], revision_short=run["revision"][:8],
            what=describe(v).split("; ")[0].replace("LoRA, ", ""), type=kind,
            examples=run["examples"], data_note=note, steps=run["steps"], seed=run["seed"],
            ckpt=v.rsplit("_c", 1)[1], commit=(f"`{REWRITTEN[run['git_commit']]}` (recorded as `{run['git_commit'][:7]}`, a "
                    f"local commit rebuilt into it before pushing; same code)"
                    if run["git_commit"] in REWRITTEN else f"`{run['git_commit'][:12]}`"),
            rows="\n".join(rows)))
    print(f"release/ written: {sorted(p.name for p in OUT.iterdir())}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("cmd", choices=("table", "build"))
    args = parser.parse_args()
    if args.cmd == "table":
        (REPO / "docs" / "variants.md").write_text(table() + "\n")
        print("docs/variants.md written")
    else:
        build()


if __name__ == "__main__":
    main()
