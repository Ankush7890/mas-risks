"""Plan 18b step 2b: empirical distance of each family from the training families.

    uv run python docs/families_b/similarity.py > docs/families_b/similarity.md

For each family, 200 items (seeds 50000-50199, used by no set): the turn-1 text plus the
withheld changing section plus the argument. TF-IDF over word unigrams and bigrams (numbers
left out, min df 2, sublinear tf) fitted on all families; a family's similarity to a seen family is the cosine between their
centroid vectors; reported is the maximum over the eight seen families.
"""

import math
import re
from collections import Counter

import numpy as np

from mas_risks.items import SEEN_FAMILIES, UNSEEN_B_FAMILIES, UNSEEN_FAMILIES, generate

SEEDS = range(50000, 50200)
fams = SEEN_FAMILIES + UNSEEN_FAMILIES + UNSEEN_B_FAMILIES
texts = {f: [f"{i.render_turn1()}\n{i.withheld_changing}\n{i.rule_reasoning}"
             for i in (generate(f, s) for s in SEEDS)] for f in fams}


def grams(text):
    w = re.findall(r"[a-z]+", text.lower())  # numbers left out: they vary per item
    return Counter(w + [f"{a} {b}" for a, b in zip(w, w[1:], strict=False)])


docs = {f: [grams(t) for t in texts[f]] for f in fams}
n_docs = sum(len(d) for d in docs.values())
df = Counter(g for f in fams for d in docs[f] for g in d)
vocab = {g: k for k, g in enumerate(sorted(g for g, n in df.items() if n >= 2))}
idf = np.array([math.log((1 + n_docs) / (1 + df[g])) + 1 for g in vocab])
cent = {}
for f in fams:
    c = np.zeros(len(vocab))
    for d in docs[f]:
        v = np.zeros(len(vocab))
        for g, n in d.items():
            if g in vocab:
                v[vocab[g]] = (1 + math.log(n)) * idf[vocab[g]]
        c += v / np.linalg.norm(v)
    cent[f] = c / np.linalg.norm(c)
print("| family | group | max cosine to a seen family | nearest seen family |")
print("|---|---|---|---|")
for f in UNSEEN_FAMILIES + UNSEEN_B_FAMILIES:
    sims = {s: float(cent[f] @ cent[s]) for s in SEEN_FAMILIES}
    best = max(sims, key=sims.get)
    group = "old unseen" if f in UNSEEN_FAMILIES else "plan 18b"
    print(f"| {f} | {group} | {sims[best]:.3f} | {best} |")
