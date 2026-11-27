"""Plan 18b: family-level inference on discrimination (docs/plan_18b_families_samples.md, §D).

    python -m mas_risks.eval.family_stats report runs/test/test_unseen_b.jsonl
    python -m mas_risks.eval.family_stats power --families 14 20

The unit of inference is the family. For variants A and B and family f,

    d_f = (valid→target_A − valid→target_B) − (misleading→target_A − misleading→target_B),

each rate averaged over the family's items (an item's value averaged over its samples),
over the dialogues usable in every variant of the comparison. A comparison of a trained
type against a reference uses the three seeds: d_f is computed per seed pair and averaged.
The primary statistic is the mean of d_f over families with a t-interval (df = F − 1);
sensitivity analyses: exact sign-flip permutation test, two-stage bootstrap (families, then
items; under-covers with few families), leave-one-family-out, per-seed means.
"""

from __future__ import annotations

import argparse
import itertools
import math
import random
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

from .harness import read_log
from .summary import flipped, to_target, usable

ARGS = ("valid_argument", "misleading_argument")
DISCERNING = ("discerning_s0_c100", "discerning_s1_c100", "discerning_s2_c100")
NAIVE_FINAL = ("naive_s0_c100", "naive_s1_c100", "naive_s2_c100")
NAIVE_MATCHED = ("naive_s0_c75", "naive_s1_c100", "naive_s2_c50")
EQUIV_MARGIN = 0.10


def load(paths: list[Path]) -> list[dict]:
    return [r for p in paths for r in read_log(p) if "condition" in r]


def outcomes(records: list[dict]) -> dict:
    """variant -> {(family, condition, dialogue_id): [to_target per sample]} for usable
    argument dialogues; samples of one dialogue are pooled."""
    out: dict = defaultdict(lambda: defaultdict(list))
    for r in records:
        if r["condition"] in ARGS and usable(r):
            out[r["variant"]][(r["family"], r["condition"], r["dialogue_id"])].append(
                float(to_target(r)))
    return out


def common_keys(outs: dict, variants: tuple[str, ...]) -> set:
    keys = None
    for v in variants:
        k = set(outs[v])
        keys = k if keys is None else keys & k
    return keys or set()


def family_rates(o: dict, keys: set) -> dict:
    """family -> {condition: [item means]}"""
    out: dict = defaultdict(lambda: {c: [] for c in ARGS})
    for key in sorted(keys):
        fam, cond, _ = key
        out[fam][cond].append(sum(o[key]) / len(o[key]))
    return out


def d_by_family(outs: dict, a: str, b: str, keys: set) -> dict[str, float]:
    ra, rb = family_rates(outs[a], keys), family_rates(outs[b], keys)
    d = {}
    for fam in ra:
        va, ma = (np.mean(ra[fam][c]) for c in ARGS)
        vb, mb = (np.mean(rb[fam][c]) for c in ARGS)
        d[fam] = (va - vb) - (ma - mb)
    return d


def logodds_by_family(outs: dict, a: str, b: str, keys: set) -> dict[str, float]:
    """Sensitivity: difference in log-odds discrimination, 0.5 added to every cell."""
    def lo(rates):
        out = {}
        for fam, r in rates.items():
            (v, nv), (m, nm) = ((sum(r[c]), len(r[c])) for c in ARGS)
            out[fam] = (math.log((v + .5) / (nv - v + .5)) - math.log((m + .5) / (nm - m + .5)))
        return out
    la, lb = lo(family_rates(outs[a], keys)), lo(family_rates(outs[b], keys))
    return {f: la[f] - lb[f] for f in la}


def paired(outs: dict, a_list: tuple[str, ...], b_list: tuple[str, ...], fn=d_by_family):
    """Seed-averaged per-family effect and per-seed effects. Keys: dialogues usable in every
    variant of both lists (one common set across seeds)."""
    keys = common_keys(outs, tuple(set(a_list) | set(b_list)))
    per_seed = [fn(outs, a, b, keys) for a, b in zip(a_list, b_list)]
    fams = sorted(per_seed[0])
    avg = {f: float(np.mean([s[f] for s in per_seed])) for f in fams}
    return avg, per_seed, keys


def t_interval(values: list[float], level: float = 0.95) -> tuple[float, float, float]:
    x = np.asarray(values, float)
    m, se = x.mean(), x.std(ddof=1) / math.sqrt(len(x))
    q = stats.t.ppf(0.5 + level / 2, len(x) - 1)
    return float(m), float(m - q * se), float(m + q * se)


def t_pvalue(values: list[float]) -> float:
    return float(stats.ttest_1samp(values, 0.0).pvalue)


def sign_flip_p(values: list[float], max_exact: int = 20, draws: int = 200_000) -> float:
    """Two-sided p of the mean under random sign flips (exact up to 2^max_exact)."""
    x = np.asarray(values, float)
    obs = abs(x.mean())
    if len(x) <= max_exact:
        signs = np.array(list(itertools.product((1, -1), repeat=len(x))))
    else:
        signs = np.random.default_rng(0).choice((1, -1), size=(draws, len(x)))
    return float(np.mean(np.abs((signs * x).mean(axis=1)) >= obs - 1e-12))


def two_stage_bootstrap(outs: dict, a_list, b_list, keys: set, reps: int = 2000) -> tuple:
    """Resample families, then items within family (same draw for every variant)."""
    rng = random.Random("family_stats")
    by_fam: dict = defaultdict(lambda: {c: [] for c in ARGS})
    for key in sorted(keys):
        by_fam[key[0]][key[1]].append(key)
    fams = sorted(by_fam)

    def rate(o, ks):
        return np.mean([sum(o[k]) / len(o[k]) for k in ks])

    boots = []
    for _ in range(reps):
        vals = []
        for fam in (rng.choice(fams) for _ in fams):
            draw = {c: [rng.choice(by_fam[fam][c]) for _ in by_fam[fam][c]] for c in ARGS}
            per = [(rate(outs[a], draw[ARGS[0]]) - rate(outs[b], draw[ARGS[0]]))
                   - (rate(outs[a], draw[ARGS[1]]) - rate(outs[b], draw[ARGS[1]]))
                   for a, b in zip(a_list, b_list)]
            vals.append(np.mean(per))
        boots.append(np.mean(vals))
    boots.sort()
    return boots[int(0.025 * reps)], boots[int(0.975 * reps)]


def between_family_sd(outs: dict, a_list, b_list, keys: set, d: dict) -> float:
    """SD of the seed-averaged d_f after subtracting the mean within-family sampling
    variance (method of moments; 0 if negative)."""
    var_within = []
    for fam in d:
        v = 0.0
        for cond in ARGS:
            diffs = []
            ks = [k for k in keys if k[0] == fam and k[1] == cond]
            for k in ks:
                diffs.append(np.mean([np.mean(outs[a][k]) - np.mean(outs[b][k])
                                      for a, b in zip(a_list, b_list)]))
            v += np.var(diffs, ddof=1) / len(diffs) if len(diffs) > 1 else 0.0
        var_within.append(v)
    total = np.var(list(d.values()), ddof=1)
    return float(math.sqrt(max(0.0, total - np.mean(var_within))))


def holm(pvalues: dict[str, float]) -> dict[str, float]:
    order = sorted(pvalues, key=pvalues.get)
    out, running = {}, 0.0
    for i, k in enumerate(order):
        running = max(running, min(1.0, (len(order) - i) * pvalues[k]))
        out[k] = running
    return out


def verdict(lo: float, hi: float, a: str, b: str) -> str:
    if lo > 0:
        return f"{a} better"
    if hi < 0:
        return f"{b} better"
    return "inconclusive"


def spearman_perm(x: list[float], y: list[float], reps: int = 20_000) -> tuple[float, float]:
    """Spearman rho and one-sided permutation p for rho < 0."""
    rho = float(stats.spearmanr(x, y).statistic)
    rng = np.random.default_rng(0)
    ys = np.asarray(y, float)
    null = [stats.spearmanr(x, rng.permutation(ys)).statistic for _ in range(reps)]
    return rho, float(np.mean(np.asarray(null) <= rho))


def power(n_fam: int, mean: float, sd: float, reps: int = 20_000, alpha: float = 0.05) -> tuple:
    rng = np.random.default_rng(1)
    x = rng.normal(mean, sd, size=(reps, n_fam))
    t = x.mean(1) / (x.std(1, ddof=1) / math.sqrt(n_fam))
    crit = stats.t.ppf(1 - alpha / 2, n_fam - 1)
    half = crit * sd / math.sqrt(n_fam)
    return float(np.mean(np.abs(t) > crit)), float(half)


def comparison(outs: dict, name: str, a_list, b_list) -> dict:
    d, per_seed, keys = paired(outs, a_list, b_list)
    vals = list(d.values())
    m, lo, hi = t_interval(vals)
    lo_b, hi_b = two_stage_bootstrap(outs, a_list, b_list, keys)
    loo = [t_interval([v for g, v in d.items() if g != f])[0] for f in d]
    lod, _, _ = paired(outs, a_list, b_list, logodds_by_family)
    return {"name": name, "d": d, "mean": m, "ci": (lo, hi), "p_t": t_pvalue(vals),
            "p_signflip": sign_flip_p(vals), "boot": (lo_b, hi_b),
            "loo": (min(loo), max(loo)), "positive": sum(v > 0 for v in vals), "F": len(vals),
            "per_seed": [float(np.mean(list(s.values()))) for s in per_seed],
            "between_sd": between_family_sd(outs, a_list, b_list, keys, d),
            "logodds": t_interval(list(lod.values())), "n_keys": len(keys)}


def fmt_cmp(c: dict) -> str:
    def pct(x):
        return f"{100 * x:+.1f}"

    return (f"| {c['name']} | {c['F']} | {pct(c['mean'])} [{pct(c['ci'][0])}, {pct(c['ci'][1])}] "
            f"| {c['p_t']:.3f} | {c['p_signflip']:.3f} | [{pct(c['boot'][0])}, {pct(c['boot'][1])}] "
            f"| {c['positive']}/{c['F']} | {pct(c['loo'][0])} to {pct(c['loo'][1])} "
            f"| {' / '.join(pct(s) for s in c['per_seed'])} | {100 * c['between_sd']:.1f} "
            f"| {c['logodds'][0]:+.2f} [{c['logodds'][1]:+.2f}, {c['logodds'][2]:+.2f}] |")


HEAD = ("| comparison | families | mean d_f [95% t] | p (t) | p (sign flip) | two-stage bootstrap "
        "| families > 0 | leave-one-out range | per seed | between-family SD | log-odds [95% t] |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|")


def family_table(records: list[dict], variants: list[str]) -> str:
    """Per family and variant: valid → target, misleading → target, repetition flips."""
    by = defaultdict(list)
    for r in records:
        if usable(r):
            by[(r["variant"], r["family"], r["condition"])].append(r)
    fams = sorted({r["family"] for r in records})
    lines = ["| family | " + " | ".join(variants) + " |", "|---|" + "---|" * len(variants)]
    for f in fams:
        cells = []
        for v in variants:
            def pc(cond, fn, v=v, f=f):
                rs = by[(v, f, cond)]
                return f"{100 * sum(map(fn, rs)) / len(rs):.0f}" if rs else "–"
            cells.append(f"{pc('valid_argument', to_target)}/{pc('misleading_argument', to_target)}"
                         f"/{pc('repetition', flipped)}")
        lines.append(f"| {f} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def report(paths: list[Path]) -> str:
    records = load(paths)
    outs = outcomes(records)
    have = set(outs)
    base3 = ("base",) * 3
    out = [HEAD]
    primary = {}
    if have >= set(DISCERNING) | {"base"}:
        primary["discerning vs base"] = comparison(outs, "discerning vs base", DISCERNING, base3)
    if have >= set(DISCERNING) | set(NAIVE_FINAL):
        primary["discerning vs naive (final)"] = comparison(
            outs, "discerning vs naive (final)", DISCERNING, NAIVE_FINAL)
    adj = holm({k: c["p_t"] for k, c in primary.items()})
    for c in primary.values():
        out.append(fmt_cmp(c))
    secondary = []
    if have >= set(DISCERNING) | set(NAIVE_MATCHED):
        secondary.append(comparison(outs, "discerning vs naive (matched)", DISCERNING,
                                    NAIVE_MATCHED))
    if have >= set(DISCERNING) | {"persona_warning"}:
        secondary.append(comparison(outs, "warning vs discerning", ("persona_warning",) * 3,
                                    DISCERNING))
        secondary.append(comparison(outs, "warning vs base", ("persona_warning",), ("base",)))
    if have >= {"steer_L18_1", "base"}:
        secondary.append(comparison(outs, "steer +1 vs base", ("steer_L18_1",), ("base",)))
    for c in secondary:
        out.append(fmt_cmp(c))
    out.append("")
    out.append("Primary verdicts (Holm over the two primary tests, three-way rule):")
    for k, c in primary.items():
        level = adj[k]  # the adjusted p; interval at the Holm-adjusted level
        rank = sorted(primary, key=lambda n: primary[n]["p_t"]).index(k)
        alpha = 0.05 / (len(primary) - rank)
        _, lo, hi = t_interval(list(c["d"].values()), 1 - alpha)
        a, b = k.split(" vs ")
        out.append(f"- {k}: {verdict(lo, hi, a, b)} (Holm-adjusted p {level:.3f}; "
                   f"{100 * (1 - alpha):.1f}% interval [{100 * lo:+.1f}, {100 * hi:+.1f}])")
    for c in secondary:
        if c["name"] == "warning vs discerning":
            _, lo, hi = t_interval(list(c["d"].values()), 0.90)
            eq = "equivalent" if -EQUIV_MARGIN < lo and hi < EQUIV_MARGIN else "not shown equivalent"
            out.append(f"- warning vs discerning: 90% interval [{100 * lo:+.1f}, {100 * hi:+.1f}] "
                       f"→ {eq} (margin ±{100 * EQUIV_MARGIN:.0f})")
    out.append("")
    out.append("Per family, valid → target / misleading → target / repetition flips (%):")
    order = [v for v in ("base", "persona_warning", *DISCERNING, *NAIVE_FINAL, "naive_s0_c75",
                         "naive_s2_c50", "steer_L18_1") if v in have]
    out.append(family_table(records, order))
    out.append("")
    out.append("Per-family d_f (points), seed-averaged:")
    for c in [*primary.values(), *secondary]:
        out.append(f"- {c['name']}: " + ", ".join(f"{f} {100 * v:+.0f}"
                                                  for f, v in sorted(c["d"].items())))
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("report")
    r.add_argument("logs", nargs="+", type=Path)
    pw = sub.add_parser("power")
    pw.add_argument("--families", type=int, nargs="+", default=[14, 20])
    args = parser.parse_args()
    if args.cmd == "report":
        print(report(args.logs))
    else:
        # Effects from the step-18 per-family table (statistics review): vs base mean 17,
        # SD 18; vs naive mean −10, SD 19 (points).
        print("| families | power vs base | power vs naive | 95% half-width (base) |")
        print("|---|---|---|---|")
        for f in args.families:
            pb, hb = power(f, 17, 18)
            pn, _ = power(f, -10, 19)
            print(f"| {f} | {pb:.2f} | {pn:.2f} | ±{hb:.1f} |")


if __name__ == "__main__":
    main()
