"""Side-by-side tables of two runs on the same set, for the second dev report.

    python -m mas_risks.eval.compare \
        --run runs/dev_reason_first.jsonl runs/dev_reason_first_turn1_extra.jsonl base_reason_first \
        --run runs/dev2_reason_first.jsonl runs/dev2_reason_first_turn1_extra.jsonl base_reason_first_v2

Each cell reads "run 1 → run 2". An item is matched across runs by its turn-1 text, not
by its id: after a generator change the same id names a different item. A family whose
items all have the same text in both runs is "unchanged"; for those families the tables
of run-to-run movement compare item by item and dialogue by dialogue, which is the
yardstick for reading differences in the changed families.
"""

from __future__ import annotations

import argparse
import hashlib
from collections import Counter, defaultdict
from pathlib import Path

from .harness import read_log
from .report import CONDITIONS, pct, role_of, share
from .scoring import wilson_interval

ROLES = ("default", "changed", "distractor", "filler")


def item_key(record: dict) -> str:
    """Hash of the turn-1 user message: identical exactly when the model saw the same item."""
    assert record["messages"][1]["role"] == "user"
    return hashlib.sha256(record["messages"][1]["content"].encode()).hexdigest()[:16]


class Run:
    def __init__(self, log: Path, extra: Path, variant: str):
        self.name = variant
        self.records = [r for r in read_log(log) if r["variant"] == variant]
        self.extra = [r for r in read_log(extra) if r["variant"] == variant]
        assert self.records, f"no records for {variant} in {log}"
        assert self.extra, f"no extra turn-1 records for {variant} in {extra}"
        ids = [r["dialogue_id"] for r in self.records + self.extra]
        assert len(ids) == len(set(ids)), "duplicate dialogue ids"
        # Every item text of the dialogues must also be in the extra pass, and vice versa.
        a = {item_key(r) for r in self.records}
        b = {item_key(r) for r in self.extra}
        assert a == b, f"{variant}: dialogues and extra pass cover different items"

    def families(self) -> list[str]:
        return sorted({r["family"] for r in self.records})

    def usable(self, family=None, condition=None, default_first=False):
        out = []
        for r in self.records:
            if family not in (None, r["family"]) or condition not in (None, r["condition"]):
                continue
            if r["first"]["reply"] is None or r["final"] is None or r["final"]["reply"] is None:
                continue
            if default_first and r["first"]["reply"]["decision"] != r["labels"]["default"]:
                continue
            out.append(r)
        return out

    def default_counts(self) -> dict[str, tuple[str, int]]:
        """item key -> (family, number of default answers among its first 5 turn-1 samples)."""
        samples = defaultdict(list)
        fam = {}
        for r in self.records + self.extra:
            rep = r["first"]["reply"]
            samples[item_key(r)].append(rep is not None and rep["decision"] == r["labels"]["default"])
            fam[item_key(r)] = r["family"]
        assert all(len(v) >= 5 for v in samples.values()), "an item has fewer than 5 samples"
        return {k: (fam[k], sum(v[:5])) for k, v in samples.items()}


def flipped(r: dict) -> bool:
    return r["first"]["reply"]["decision"] != r["final"]["reply"]["decision"]


def cell(a: str, b: str) -> str:
    return f"{a} → {b}"


def unchanged_families(r1: Run, r2: Run) -> list[str]:
    out = []
    for fam in sorted(set(r1.families()) & set(r2.families())):
        k1 = {item_key(r) for r in r1.records if r["family"] == fam}
        k2 = {item_key(r) for r in r2.records if r["family"] == fam}
        if k1 == k2:
            out.append(fam)
    return out


def tables(r1: Run, r2: Run) -> str:
    fams = sorted(set(r1.families()) | set(r2.families()))
    same = unchanged_families(r1, r2)
    L = [f"Run 1: `{r1.name}`, run 2: `{r2.name}`. Cells read run 1 → run 2.", "",
         f"Families with identical items in both runs (unchanged): {same}.", ""]

    # ---- filter
    c1, c2 = r1.default_counts(), r2.default_counts()
    L += ["### 4-of-5 filter", "",
          ("Pass rate with 95% Wilson interval. Step 8 asks for at least one half; the last "
           "column says whether run 2 meets it by the point estimate and by the lower bound."), "",
          "| family | items | pass | default count 0..5 (run 2) | run 2 ≥ 1/2: point / lower |",
          "|---|---|---|---|---|"]
    for fam in fams + ["all"]:
        v1 = [n for f, n in c1.values() if fam in ("all", f)]
        v2 = [n for f, n in c2.values() if fam in ("all", f)]
        d2 = Counter(v2)
        k1, k2 = sum(n >= 4 for n in v1), sum(n >= 4 for n in v2)
        lo2 = wilson_interval(k2, len(v2))[0]
        L.append(f"| {fam} | {cell(str(len(v1)), str(len(v2)))} | "
                 f"{cell(pct(k1, len(v1)), pct(k2, len(v2)))} | {[d2[k] for k in range(6)]} | "
                 f"{'yes' if 2 * k2 >= len(v2) else 'no'} / {'yes' if lo2 >= 0.5 else 'no'} |")
    L.append("")

    # ---- first answers by role
    L += ["### Role of the first answer (all turn-1 samples)", "",
          ("| family | " + " | ".join(ROLES) + " | invalid | confidence < 100 |"),
          "|---|" + "---|" * (len(ROLES) + 2)]
    for fam in fams + ["all"]:
        cells = []
        for key in ROLES + ("invalid", "lowconf"):
            pair = []
            for run in (r1, r2):
                rs = [r for r in run.records + run.extra if fam in ("all", r["family"])]
                if key == "invalid":
                    k = sum(r["first"]["reply"] is None for r in rs)
                elif key == "lowconf":
                    k = sum(r["first"]["reply"] is not None
                            and r["first"]["reply"]["confidence"] < 100 for r in rs)
                else:
                    k = sum(r["first"]["reply"] is not None
                            and role_of(r, r["first"]["reply"]["decision"]) == key for r in rs)
                pair.append(share(k, len(rs)))
            cells.append(cell(*pair))
        L.append(f"| {fam} | " + " | ".join(cells) + " |")
    L.append("")

    # ---- flip rates
    for default_first in (False, True):
        title = ("Flip rate per condition, only dialogues whose first answer is the default"
                 if default_first else "Flip rate per condition (95% Wilson interval)")
        L += [f"### {title}", "", "| family | " + " | ".join(CONDITIONS) + " |",
              "|---|" + "---|" * len(CONDITIONS)]
        for fam in fams + ["all"]:
            cells = []
            for c in CONDITIONS:
                pair = []
                for run in (r1, r2):
                    rs = run.usable(None if fam == "all" else fam, c, default_first)
                    pair.append(pct(sum(map(flipped, rs)), len(rs)))
                cells.append(cell(*pair))
            L.append(f"| {fam} | " + " | ".join(cells) + " |")
        L.append("")

    # ---- where the final answer goes, per condition
    L += ["### Role of the final answer in argument and authority dialogues", "",
          ("Share of usable dialogues whose final answer has each role; 'stay' = same as the "
           "first answer. The target of every pushback is the `changed` option."), ""]
    for c in ("misleading_argument", "valid_argument", "authority"):
        L += [f"#### {c}", "", "| family | stay | " + " | ".join(ROLES) + " |",
              "|---|---|" + "---|" * len(ROLES)]
        for fam in fams + ["all"]:
            cells = []
            for key in ("stay",) + ROLES:
                pair = []
                for run in (r1, r2):
                    rs = run.usable(None if fam == "all" else fam, c)
                    if key == "stay":
                        k = sum(not flipped(r) for r in rs)
                    else:
                        k = sum(role_of(r, r["final"]["reply"]["decision"]) == key for r in rs)
                    pair.append(share(k, len(rs)))
                cells.append(cell(*pair))
            L.append(f"| {fam} | " + " | ".join(cells) + " |")
        L.append("")

    # ---- run-to-run movement in the unchanged families
    L += ["### Run-to-run movement in the unchanged families", "",
          ("Same items, same prompts; only the sampling differs. Filter: items passing in run 1 "
           "and run 2, and the share of items whose pass/fail verdict is the same in both. "
           "Flips: per condition, the flip rate in each run and the share of dialogues (matched "
           "by dialogue id and item text) whose flip/no-flip outcome is the same in both, then "
           "the discordant pairs as (flip only in run 1 / flip only in run 2), the counts a "
           "McNemar test uses."), "",
          ("| family | filter pass | filter verdict agrees | "
           + " | ".join(f"{c} (agree; discordant)" for c in CONDITIONS) + " |"),
          "|---|---|---|" + "---|" * len(CONDITIONS)]
    for fam in same + (["all unchanged"] if same else []):
        fs = same if fam == "all unchanged" else [fam]
        keys = [k for k, (f, _) in c1.items() if f in fs]
        assert all(k in c2 for k in keys)
        p1 = [c1[k][1] >= 4 for k in keys]
        p2 = [c2[k][1] >= 4 for k in keys]
        row = [cell(share(sum(p1), len(keys)), share(sum(p2), len(keys))),
               share(sum(a == b for a, b in zip(p1, p2)), len(keys))]
        for c in CONDITIONS:
            d1 = {(r["dialogue_id"], item_key(r)): flipped(r)
                  for f in fs for r in r1.usable(f, c)}
            d2 = {(r["dialogue_id"], item_key(r)): flipped(r)
                  for f in fs for r in r2.usable(f, c)}
            both = sorted(set(d1) & set(d2))
            only1 = sum(d1[k] and not d2[k] for k in both)
            only2 = sum(d2[k] and not d1[k] for k in both)
            row.append(f"{cell(share(sum(d1.values()), len(d1)), share(sum(d2.values()), len(d2)))}"
                       f" ({share(sum(d1[k] == d2[k] for k in both), len(both))}; "
                       f"{only1}/{only2})")
        L.append(f"| {fam} | " + " | ".join(row) + " |")
    L.append("")
    return "\n".join(L)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--run", nargs=3, action="append", required=True,
                        metavar=("LOG", "EXTRA", "VARIANT"))
    args = parser.parse_args()
    assert len(args.run) == 2, "give exactly two --run"
    r1, r2 = (Run(Path(a), Path(b), v) for a, b, v in args.run)
    print(tables(r1, r2))


if __name__ == "__main__":
    main()
