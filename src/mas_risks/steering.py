"""Step 13: extract the yield-minus-hold steering vector from train dialogues.

    python -m mas_risks.steering extract

For every train dialogue under majority or authority pressure (brief 6 section 9: no
argument conditions, so the vector carries pressure and not evidence), two prompts that
differ only in a prefilled start of the second reply: '{"reason": "I keep my answer' and
'{"reason": "I change my answer'. The vector at a layer is the mean over pairs of the
difference (change minus keep) of the residual stream after that layer at the last
prefilled token. All layers are stored in runs/steering/vectors.pt with their norms.
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import UTC, datetime

from .build import build
from .eval.prompts import PROMPTS_REASON_FIRST
from .eval.run import _git_commit
from .training import REPO, messages_for, pick_turn1, turn1_replies
from .variants import STEERING_FILE

PREFILL = {"hold": '{"reason": "I keep my answer', "yield": '{"reason": "I change my answer'}
CONDITIONS = ("majority", "authority")


def extract(batch: int) -> None:
    import torch

    from .models import QwenChat

    system, fmt = PROMPTS_REASON_FIRST
    replies = turn1_replies("train")
    dialogues = [d for d in build("train") if d.condition in CONDITIONS]
    commit = _git_commit()
    model = QwenChat(max_batch=batch)
    started = time.monotonic()
    total, n = None, 0
    for start in range(0, len(dialogues), batch):
        chunk = dialogues[start:start + batch]
        base = [model.render(messages_for(d, pick_turn1(replies, d.item.item_id, "steering"),
                                          system, fmt)) for d in chunk]
        hold = model.last_token_states([b + PREFILL["hold"] for b in base])
        yld = model.last_token_states([b + PREFILL["yield"] for b in base])
        diff = (yld - hold).sum(dim=0)
        total = diff if total is None else total + diff
        n += len(chunk)
    mean_diff = (total / n).cpu()
    STEERING_FILE.parent.mkdir(parents=True, exist_ok=True)
    norms = mean_diff.norm(dim=-1).tolist()
    torch.save({"mean_diff": mean_diff, "pairs": n, "prefill": PREFILL,
                "conditions": CONDITIONS}, STEERING_FILE)
    meta = {"date": datetime.now(UTC).isoformat(timespec="seconds"), "git_commit": commit,
            "pairs": n, "conditions": CONDITIONS, "prefill": PREFILL,
            "layer_norms": [round(x, 3) for x in norms], "model": model.metadata(),
            "wall_seconds": round(time.monotonic() - started, 1)}
    STEERING_FILE.with_suffix(".meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(json.dumps({k: meta[k] for k in ("pairs", "layer_norms", "wall_seconds")}))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    ex = sub.add_parser("extract")
    ex.add_argument("--batch", type=int, default=16)
    args = parser.parse_args()
    assert REPO.exists()
    extract(args.batch)


if __name__ == "__main__":
    main()
