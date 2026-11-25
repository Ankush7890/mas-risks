"""Step 16: train a LoRA adapter on training_data/<type>.jsonl.

    python -m mas_risks.training.lora --type naive --seed 0
    python -m mas_risks.training.lora --type discerning --seed 0 \
        --exclude-families league_rules delivery_terms --name discerning_diag_s0

LoRA rank 16, alpha 32, dropout 0.05 on every attention and MLP projection; AdamW,
learning rate 1e-4 with 3% warmup and a cosine decay; 2 epochs; effective batch 16;
bf16 with gradient checkpointing. The loss is on the final assistant turn only (its
tokens and the closing <|im_end|>): the prompt is the chat template applied to every
message but the last, with the generation prompt, and is asserted to be a prefix of the
full text. Adapters are saved at 25, 50, 75 and 100% of the steps under runs/lora/<name>/.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import time
from datetime import UTC, datetime

from ..eval.run import _git_commit
from ..models import MODEL_ID
from . import REPO

LORA_DIR = REPO / "runs" / "lora"
TARGETS = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]


def encode(tok, messages: list[dict]) -> tuple[list[int], list[int]]:
    prompt = tok.apply_chat_template(messages[:-1], tokenize=False, add_generation_prompt=True)
    full = tok.apply_chat_template(messages, tokenize=False)
    assert full.startswith(prompt), "the prompt is not a prefix of the full dialogue"
    end = full.index("<|im_end|>", len(prompt)) + len("<|im_end|>")
    p_ids = tok(prompt, add_special_tokens=False)["input_ids"]
    ids = tok(full[:end], add_special_tokens=False)["input_ids"]
    assert ids[:len(p_ids)] == p_ids, "tokenisation of the prompt differs inside the dialogue"
    return ids, [-100] * len(p_ids) + ids[len(p_ids):]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--type", choices=("naive", "discerning"), required=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--name")
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--epochs", type=float, default=2.0)
    parser.add_argument("--micro-batch", type=int, default=4)
    parser.add_argument("--accum", type=int, default=4)
    parser.add_argument("--rank", type=int, default=16)
    parser.add_argument("--exclude-families", nargs="*", default=[])
    parser.add_argument("--max-steps", type=int, help="for a timing smoke run")
    args = parser.parse_args()
    name = args.name or f"{args.type}_s{args.seed}"
    out = LORA_DIR / name
    out.mkdir(parents=True, exist_ok=True)

    import torch
    from huggingface_hub import HfApi
    from peft import LoraConfig, get_peft_model
    from transformers import AutoModelForCausalLM, AutoTokenizer

    random.seed(args.seed)
    torch.manual_seed(args.seed)
    revision = HfApi().model_info(MODEL_ID).sha
    tok = AutoTokenizer.from_pretrained(MODEL_ID, revision=revision)
    data_path = REPO / "training_data" / f"{args.type}.jsonl"
    rows = [json.loads(x) for x in data_path.read_text().splitlines()]
    rows = [r for r in rows if r["dialogue_id"].split("/")[1].rsplit("-", 1)[0]
            not in args.exclude_families]
    examples = [encode(tok, r["messages"]) for r in rows]
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, revision=revision,
                                                 dtype=torch.bfloat16).to("cuda")
    model.gradient_checkpointing_enable()
    model.enable_input_require_grads()
    model = get_peft_model(model, LoraConfig(r=args.rank, lora_alpha=2 * args.rank,
                                             lora_dropout=0.05, target_modules=TARGETS,
                                             task_type="CAUSAL_LM"))
    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=args.lr, weight_decay=0.0)
    per_epoch = math.ceil(len(examples) / (args.micro_batch * args.accum))
    total = args.max_steps or math.ceil(per_epoch * args.epochs)
    warm = max(1, int(0.03 * total))
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: (s + 1) / warm if s < warm else
                                              0.5 * (1 + math.cos(math.pi * (s - warm) /
                                                                  max(1, total - warm))))
    saves = {math.ceil(total * q): f"ckpt_{int(q * 100)}" for q in (0.25, 0.5, 0.75, 1.0)}
    pad = tok.pad_token_id
    commit, started = _git_commit(), time.monotonic()
    log = (out / "train_log.jsonl").open("w")
    order: list[int] = []
    rng = random.Random(f"order:{args.seed}")
    model.train()
    step = 0
    while step < total:
        if len(order) < args.micro_batch * args.accum:
            epoch = list(range(len(examples)))
            rng.shuffle(epoch)
            order += epoch
        loss_sum, tok_sum = 0.0, 0
        batches = [order[i * args.micro_batch:(i + 1) * args.micro_batch]
                   for i in range(args.accum)]
        order = order[args.micro_batch * args.accum:]
        n_target = sum(sum(t != -100 for t in examples[i][1]) for b in batches for i in b)
        for b in batches:
            width = max(len(examples[i][0]) for i in b)
            ids = torch.full((len(b), width), pad)
            lab = torch.full((len(b), width), -100)
            att = torch.zeros((len(b), width), dtype=torch.long)
            for row, i in enumerate(b):
                x, y = examples[i]
                ids[row, :len(x)], lab[row, :len(y)], att[row, :len(x)] = (
                    torch.tensor(x), torch.tensor(y), 1)
            ids, lab, att = ids.cuda(), lab.cuda(), att.cuda()
            logits = model(input_ids=ids, attention_mask=att).logits[:, :-1].float()
            loss = torch.nn.functional.cross_entropy(
                logits.reshape(-1, logits.size(-1)), lab[:, 1:].reshape(-1),
                ignore_index=-100, reduction="sum")
            (loss / n_target).backward()
            loss_sum += loss.item()
            tok_sum += int((lab[:, 1:] != -100).sum())
        torch.nn.utils.clip_grad_norm_(params, 1.0)
        opt.step()
        sched.step()
        opt.zero_grad(set_to_none=True)
        step += 1
        rec = {"step": step, "loss": round(loss_sum / tok_sum, 4), "lr": sched.get_last_lr()[0],
               "seconds": round(time.monotonic() - started, 1)}
        log.write(json.dumps(rec) + "\n")
        log.flush()
        if step % 20 == 0 or step == 1:
            print(rec, flush=True)
        if step in saves:
            model.save_pretrained(out / saves[step])
    meta = {"date": datetime.now(UTC).isoformat(timespec="seconds"), "git_commit": commit,
            "type": args.type, "seed": args.seed, "examples": len(examples),
            "exclude_families": args.exclude_families, "data_file": str(data_path.relative_to(REPO)),
            "data_manifest": json.loads((REPO / "training_data" / "MANIFEST.json").read_text()),
            "lr": args.lr, "epochs": args.epochs, "steps": total, "rank": args.rank,
            "effective_batch": args.micro_batch * args.accum, "targets": TARGETS,
            "model_id": MODEL_ID, "revision": revision, "torch": torch.__version__,
            "peak_memory_gb": round(torch.cuda.max_memory_allocated() / 2**30, 1),
            "wall_seconds": round(time.monotonic() - started, 1)}
    (out / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(json.dumps(meta, indent=1))


if __name__ == "__main__":
    main()
