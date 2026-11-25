"""Step 9 after the filter: leak checks, export, canary, manifest, verification.

    python -m mas_risks.freeze leaks --dry        # all sets, generator's own argument texts
    python -m mas_risks.freeze leaks              # all sets, stored (rephrased) arguments
    python -m mas_risks.freeze balance            # target position, valid vs misleading items
    python -m mas_risks.freeze export             # data/sets/<set>.jsonl for every set but dev
    python -m mas_risks.freeze manifest --commit <generator commit>
    python -m mas_risks.freeze verify             # recompute every hash in data/MANIFEST.json

See docs/REMOTE_AGENT_BRIEF_5.md, section 8.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import uuid
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from .build import _wordings, build, dialogues_for
from .eval import prompts
from .items import LABELS
from .splits import SET_NAMES, leak_checks, load_spec, selected
from .wordings.rephrase import read_arguments

REPO = Path(__file__).resolve().parents[2]
SETS_DIR = REPO / "data" / "sets"
MANIFEST = REPO / "data" / "MANIFEST.json"
EXPORTED = ("train", "val", "test_seen", "test_unseen")
WITH_CANARY = ("val", "test_seen", "test_unseen")  # not train: adapters are trained on it
FROZEN_PATHS = ("src/mas_risks/items", "src/mas_risks/splits/split_spec.toml", "data/wordings",
                "src/mas_risks/eval/prompts.py")
CHI2_3DF_P001 = 16.27


def _dry_build(set_name: str) -> list:
    """The set's dialogues with the generator's own argument text instead of the stored
    rephrasing, for checking the selection before any API spending."""
    spec = load_spec()
    s = spec.sets[set_name]
    w = _wordings(s.wording_pool)
    return [d for f in s.families for item in selected(set_name, f)
            for d in dialogues_for(set_name, item, item.rule_reasoning, w, s.conditions)]


def all_sets(dry: bool) -> dict[str, list]:
    return {n: (_dry_build(n) if dry else build(n)) for n in SET_NAMES}


def balance_by_kind(data: dict[str, list]) -> list[tuple]:
    """Per set and family: chi-square (2 kinds x 4 positions) of the changed option's letter,
    valid against misleading items. Returns (set, family, counts, chi2) rows."""
    rows = []
    for set_name, dialogues in data.items():
        items = {d.item.item_id: d.item for d in dialogues}.values()
        for family in sorted({i.family for i in items}):
            c = {k: Counter(i.label("changed") for i in items
                            if i.family == family and i.rule_applies == k) for k in (True, False)}
            n = {k: sum(c[k].values()) for k in c}
            total = n[True] + n[False]
            chi2 = 0.0
            for lab in LABELS:
                col = c[True][lab] + c[False][lab]
                for k in c:
                    exp = n[k] * col / total
                    if exp:
                        chi2 += (c[k][lab] - exp) ** 2 / exp
            rows.append((set_name, family, {("valid" if k else "misleading"): dict(sorted(c[k].items()))
                                            for k in c}, round(chi2, 2)))
    return rows


def export_set(set_name: str, canary: str | None) -> Path:
    spec = load_spec()
    args = read_arguments(set_name)
    out = SETS_DIR / f"{set_name}.jsonl"
    with out.open("w", encoding="utf-8", newline="\n") as f:
        for d in build(set_name):
            item = d.item
            row = args[item.item_id]
            rec = {
                "dialogue_id": d.dialogue_id, "set": set_name, "item_id": item.item_id,
                "family": item.family, "seed": item.seed, "condition": d.condition,
                "version": d.version, "turn1_user": item.render_turn1(True),
                "turn2_message": d.message, "target_label": d.target_label,
                "wording_id": d.wording_id, "fillers": [list(x) for x in d.fillers],
                "labels": {r: item.label(r) for r in ("default", "changed", "distractor", "filler")},
                "rule_applies": item.rule_applies, "item": item.to_dict(),
                "argument": {"model": row["model"], "fallback": row["fallback"],
                             "original": row["original"], "text": row["argument"]},
                "wording_pool": spec.sets[set_name].wording_pool,
            }
            if canary:
                rec["canary"] = canary
            f.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")
    return out


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hashed_files() -> list[Path]:
    tracked = subprocess.run(["git", "ls-files", "data"], cwd=REPO, capture_output=True,
                             text=True, check=True).stdout.split()
    files = {REPO / p for p in tracked} | set((REPO / "data" / "sets").glob("*"))
    files |= set((REPO / "runs" / "filter").glob("*.jsonl"))
    files |= {REPO / "src/mas_risks/splits/split_spec.toml", REPO / "src/mas_risks/eval/prompts.py"}
    return sorted(p for p in files if p.is_file() and p != MANIFEST)


def write_manifest(commit: str, canary: str) -> dict:
    from importlib.metadata import version

    counts = {}
    for n in EXPORTED:
        lines = [json.loads(x) for x in (SETS_DIR / f"{n}.jsonl").read_text().splitlines()]
        counts[n] = {"items": len({r["item_id"] for r in lines}), "dialogues": len(lines),
                     "by_family": dict(sorted(Counter(r["family"] for r in lines
                                                      if r["condition"] == "neutral").items()))}
    manifest = {
        "frozen": datetime.now(UTC).isoformat(timespec="seconds"),
        "generator_commit": commit, "frozen_paths": list(FROZEN_PATHS), "canary": canary,
        "canary_in": list(WITH_CANARY),
        "filter": {"model": "Qwen/Qwen3-4B-Instruct-2507",
                   "revision": "cdbee75f17c01a7cc42f958dc650907174af0554",
                   "sampling": {"temperature": 0.7, "top_p": 0.8, "top_k": 20, "min_p": 0.0},
                   "rule": "default answer in at least 4 of 5 turn-1 samples",
                   "prompts": {"variant": "reason_first",
                               "system_sha256": hashlib.sha256(
                                   prompts.PROMPTS_REASON_FIRST[0].encode()).hexdigest(),
                               "format_sha256": hashlib.sha256(
                                   prompts.PROMPTS_REASON_FIRST[1].encode()).hexdigest()},
                   "libraries": {p: version(p) for p in ("torch", "transformers")}},
        "sets": counts,
        "files": {str(p.relative_to(REPO)): _sha256(p) for p in hashed_files()},
    }
    MANIFEST.write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n", newline="\n")
    return manifest


def verify() -> list[str]:
    """Files whose hash differs from the manifest, or that are missing or new."""
    m = json.loads(MANIFEST.read_text())
    now = {str(p.relative_to(REPO)): _sha256(p) for p in hashed_files()}
    bad = [p for p, h in m["files"].items() if now.get(p) != h]
    bad += [f"new: {p}" for p in now if p not in m["files"]]
    return bad


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    lk = sub.add_parser("leaks")
    lk.add_argument("--dry", action="store_true")
    sub.add_parser("balance").add_argument("--dry", action="store_true")
    sub.add_parser("export")
    mf = sub.add_parser("manifest")
    mf.add_argument("--commit", required=True)
    sub.add_parser("verify")
    args = parser.parse_args()
    if args.cmd == "leaks":
        data = all_sets(args.dry)
        report = leak_checks.run_all(data)
        print({k: len(v) for k, v in data.items()}, "dialogues per set")
        print("leak checks passed")
        for name, r in report.items():
            print(f"  {name}: {r}")
    elif args.cmd == "balance":
        rows = balance_by_kind(all_sets(args.dry))
        worst = max(r[3] for r in rows)
        for r in rows:
            print(f"  {r[0]:11s} {r[1]:16s} chi2 {r[3]:5.2f}  {r[2]}")
        print(f"largest chi2 {worst} (limit {CHI2_3DF_P001} at p=0.001, 3 df)")
        assert worst <= CHI2_3DF_P001, "target position differs between kinds; stop and ask"
    elif args.cmd == "export":
        SETS_DIR.mkdir(parents=True, exist_ok=True)
        canary = None
        if MANIFEST.exists():
            canary = json.loads(MANIFEST.read_text())["canary"]
        canary = canary or f"MAS-RISKS CANARY {uuid.uuid4()}"
        (SETS_DIR / "CANARY.txt").write_text(canary + "\n", newline="\n")
        for n in EXPORTED:
            path = export_set(n, canary if n in WITH_CANARY else None)
            print(f"wrote {path}")
    elif args.cmd == "manifest":
        canary = (SETS_DIR / "CANARY.txt").read_text().strip()
        m = write_manifest(args.commit, canary)
        print(json.dumps(m["sets"], indent=1), len(m["files"]), "files hashed")
    else:
        bad = verify()
        print("manifest verified" if not bad else f"MISMATCH: {bad}")
        raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
