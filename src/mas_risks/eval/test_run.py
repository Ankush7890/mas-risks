"""Step 18: run one pre-registered variant on a test set.

    python -m mas_risks.eval.test_run --set test_seen --spec lora:runs/lora/naive_s0/ckpt_100 \
        --variant naive_s0

Refuses to start unless docs/preregistration.md is committed and unchanged, the working
tree of src/ and data/ is clean, and the variant is named in the pre-registration with
the fingerprint (prompt, steering file, adapter hashes) it has now. Each start appends
a row to docs/test_access_log.md. A run resumes after a crash; it is never repeated.
"""

from __future__ import annotations

import argparse
import json
import random
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

from ..build import build
from .filter_sets import ACCESS_LOG
from .harness import read_log, run_dialogue
from .run import _git_commit

REPO = Path(__file__).resolve().parents[3]
PREREG = REPO / "docs" / "preregistration.md"
PREREG_VARIANTS = REPO / "docs" / "preregistration_variants.json"
TEST_SETS = ("test_seen", "test_unseen")


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True,
                          check=True).stdout


def guard(log: Path, variant: str, purpose: str, set_name: str = "corrigibility_test",
          spec_name: str | None = None) -> None:
    for path in (PREREG, PREREG_VARIANTS):
        assert path.exists(), f"{path} is missing: pre-register before any test run"
        rel = str(path.relative_to(REPO))
        assert _git("ls-files", rel).strip(), f"{rel} is not committed"
        assert not _git("status", "--porcelain", rel).strip(), f"{rel} has uncommitted changes"
    dirty = _git("status", "--porcelain", "src", "data").strip()
    assert not dirty, f"uncommitted changes in src/ or data/:\n{dirty}"
    registered = json.loads(PREREG_VARIANTS.read_text())
    assert variant in registered, f"variant {variant!r} is not pre-registered"
    if spec_name is not None:
        from ..variants import fingerprint, parse

        entry = registered[variant]
        assert entry["spec"] == spec_name, (entry["spec"], spec_name)
        assert entry["fingerprint"] == fingerprint(parse(spec_name)), \
            f"{variant}: the variant's files changed since the pre-registration"
    date = datetime.now(UTC).isoformat(timespec="seconds")
    with ACCESS_LOG.open("a", encoding="utf-8") as f:
        f.write(f"| {date} | {set_name} | {variant} | {purpose} | "
                f"`{log.relative_to(REPO) if log.is_absolute() else log}` | "
                f"`{_git_commit()[:12]}` |\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--set", choices=TEST_SETS, required=True)
    parser.add_argument("--spec", required=True)
    parser.add_argument("--variant", required=True)
    parser.add_argument("--log", type=Path)
    parser.add_argument("--threads", type=int, default=32)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    log = args.log or REPO / "runs" / "test" / f"{args.set}.jsonl"
    guard(log, args.variant, "step 18: pre-registered test run", args.set, args.spec)

    import torch

    from ..variants import load_variant

    torch.manual_seed(args.seed)
    model, spec = load_variant(args.spec, seed=args.seed, max_batch=args.threads)
    dialogues = build(args.set)
    random.Random(f"order:{args.set}").shuffle(dialogues)
    log.parent.mkdir(parents=True, exist_ok=True)
    done = ({r["dialogue_id"] for r in read_log(log) if r["variant"] == args.variant}
            if log.exists() else set())
    todo = [d for d in dialogues if d.dialogue_id not in done]
    print(f"{len(dialogues)} dialogues, {len(todo)} to run", flush=True)
    commit, lock, started = _git_commit(), threading.Lock(), time.monotonic()

    def one(d):
        rec = run_dialogue(model, d, variant=args.variant, system_prompt=spec.system_prompt,
                           format_instruction=spec.format_instruction)
        rec["spec"] = args.spec
        return rec

    with log.open("a", encoding="utf-8") as f, ThreadPoolExecutor(args.threads) as pool:
        for rec in pool.map(one, todo):
            with lock:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                f.flush()
    meta = log.with_suffix(".jsonl.meta.json")
    metas = json.loads(meta.read_text()) if meta.exists() else []
    metas.append({"date": datetime.now(UTC).isoformat(timespec="seconds"), "git_commit": commit,
                  "set": args.set, "variant": args.variant, "spec": args.spec,
                  "model": model.metadata(), "generation": model.stats.summary(),
                  "wall_seconds": round(time.monotonic() - started, 1)})
    meta.write_text(json.dumps(metas, indent=2) + "\n")


if __name__ == "__main__":
    main()
