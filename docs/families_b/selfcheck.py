"""Plan 18b: checks a writer runs on a new family before handing it over.

    uv run python docs/families_b/selfcheck.py <family> [--show 2]

1. 1,000 seeds generate without error (Item's own asserts run on each).
2. Distinct parameter sets per kind (rule applies / does not) in those seeds: ≥ 300 each.
3. A naive Bayes classifier that sees only the argument text (rule_reasoning) cannot tell
   sound from unsound arguments: 5-fold accuracy ≤ 0.5 + 3 standard errors.
4. Kinds alternate with the seed; option roles are spread over A–D.
"""

import argparse
import sys
from collections import Counter
from types import SimpleNamespace

from mas_risks.items import generate
from mas_risks.splits import params_key
from mas_risks.splits.leak_checks import shortcut_accuracy

parser = argparse.ArgumentParser()
parser.add_argument("family")
parser.add_argument("--seeds", type=int, default=1000)
parser.add_argument("--show", type=int, default=0)
args = parser.parse_args()

items = [generate(args.family, s) for s in range(args.seeds)]
ok = True
for kind in (True, False):
    n = len({params_key(i) for i in items if i.rule_applies == kind})
    print(f"distinct parameter sets, rule_applies={kind}: {n}")
    ok &= n >= 300
assert all(i.rule_applies == (i.seed % 2 == 0) for i in items)
rows = [SimpleNamespace(item=i, message=i.rule_reasoning,
                        condition="valid_argument" if i.rule_applies else "misleading_argument")
        for i in items]
acc, n = shortcut_accuracy(rows)
limit = 0.5 + 3 * (0.25 / n) ** 0.5
print(f"argument-only classifier accuracy {acc:.3f} (limit {limit:.3f}, n={n})")
ok &= acc <= limit
for role in ("default", "changed", "distractor"):
    print(f"{role} positions: {dict(sorted(Counter(i.label(role) for i in items).items()))}")
for i in items[:args.show]:
    print("=" * 80, f"\n{i.item_id} rule_applies={i.rule_applies}\n{i.render_turn1()}")
    print(f"\n[withheld changing] {i.withheld_changing}\n[argument] {i.rule_reasoning}")
    print(f"[answers] " + ", ".join(f"{r}={i.label(r)}" for r in ("default", "changed", "distractor", "filler")))
print("SELF-CHECK", "PASSED" if ok else "FAILED")
sys.exit(0 if ok else 1)
