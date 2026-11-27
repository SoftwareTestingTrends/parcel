"""Numbers for 'Run it once, run it ten times', from per_trial.json (6 Gemma 4 trials per case, Parcel a1a9440)."""
import json, math, random
from math import comb
from pathlib import Path
HERE = Path(__file__).parent
cases = {c["id"]: c for c in json.loads((HERE / "evals/cases.json").read_text())}
R = json.loads((HERE / "per_trial.json").read_text())["pass"]
ids = list(R)
n = len(ids)
pct = lambda x: f"{100*x:.1f}%"

print("== The same Parcel, six single-trial runs (trial k of every case) ==")
singles = [sum(R[c][k] for c in ids) for k in range(6)]
for k, s in enumerate(singles, 1): print(f"run of trial {k}: {s}/{n} = {pct(s/n)}")
print(f"range {min(singles)}..{max(singles)} of {n}")

print("\n== Three-trial runs: trials 1-3 vs 4-6 ==")
a = sum(sum(R[c][:3]) for c in ids); b = sum(sum(R[c][3:]) for c in ids)
print(f"trials 1-3: {a}/108 = {pct(a/108)}   trials 4-6: {b}/108 = {pct(b/108)}   all six: {a+b}/216 = {pct((a+b)/216)}")
moved = [(c, sum(R[c][:3]), sum(R[c][3:])) for c in ids if sum(R[c][:3]) != sum(R[c][3:])]
print(f"cases whose 3-trial score changed: {len(moved)} of {n}")
for c, x, y in moved: print(f"  {c}: {x}/3 -> {y}/3")
allpass13 = sum(all(R[c][:3]) for c in ids); allpass46 = sum(all(R[c][3:]) for c in ids)
print(f"cases passing all 3: run A {allpass13}, run B {allpass46}")

print("\n== Per-case, over 6 trials ==")
dist = {}
for c in ids: dist.setdefault(sum(R[c]), []).append(c)
for k in sorted(dist, reverse=True): print(f"{k}/6: {len(dist[k])} cases")

def pass_at(c_, n_, k): return 1 - comb(n_ - c_, k) / comb(n_, k)
def pass_hat(c_, n_, k): return comb(c_, k) / comb(n_, k)
print("\n== pass@k and pass^k (unbiased estimates from 6 trials, averaged over cases) ==")
for k in (1, 2, 3, 6):
    pa = sum(pass_at(sum(R[c]), 6, k) for c in ids) / n
    ph = sum(pass_hat(sum(R[c]), 6, k) for c in ids) / n
    print(f"k={k}: pass@k {pct(pa)}  pass^k {pct(ph)}")
print("\n-- by label --")
for lab, sel in [("golden", lambda c: cases[c]["golden"]), ("regression", lambda c: cases[c]["type"] == "regression"),
                 ("capability", lambda c: cases[c]["type"] == "capability")]:
    s = [c for c in ids if sel(c)]
    p1 = sum(sum(R[c]) for c in s) / (6 * len(s))
    p3a = sum(pass_at(sum(R[c]), 6, 3) for c in s) / len(s); p3h = sum(pass_hat(sum(R[c]), 6, 3) for c in s) / len(s)
    p6h = sum(all(R[c]) for c in s)
    print(f"{lab} ({len(s)} cases): per-trial {pct(p1)}, pass@3 {pct(p3a)}, pass^3 {pct(p3h)}, all 6 passed {p6h}/{len(s)}")

print("\n== Single case formulas, p = per-trial pass rate ==")
for p in (0.5, 5/6, 0.9, 0.95, 0.99):
    print(f"p={p:.3f}: " + "  ".join(f"k={k}: @ {pct(1-(1-p)**k)} ^ {pct(p**k)}" for k in (1, 3, 10)))
print("chance a case failing 1 in 20 shows zero failures in k trials: " +
      ", ".join(f"k={k}: {pct(0.95**k)}" for k in (3, 6, 10, 20, 60)))
print("chance at least one failure seen for p_fail=1/20 needs k>=", math.ceil(math.log(0.05) / math.log(0.95)), "for 95%")
for k in (3, 6, 10, 30, 100):
    print(f"0 failures in {k}: failure rate could still be up to {pct(1-0.05**(1/k))} (95%); rule of three 3/k = {pct(3/k)}")

print("\n== Noise: standard error of the suite pass rate (case-level means; Miller 2024) ==")
def se_of(vals):
    m = sum(vals) / len(vals); return math.sqrt(sum((v - m) ** 2 for v in vals) / (len(vals) - 1) / len(vals)), m
for label, sl in [("1 trial (trial 1)", slice(0, 1)), ("3 trials (1-3)", slice(0, 3)), ("6 trials", slice(0, 6))]:
    se, m = se_of([sum(R[c][sl]) / len(R[c][sl]) for c in ids])
    print(f"{label}: pass rate {pct(m)}, SE {pct(se)}, 95% interval {pct(m-1.96*se)} to {pct(m+1.96*se)}")
d = [sum(R[c][3:]) / 3 - sum(R[c][:3]) / 3 for c in ids]
se, m = se_of(d)
print(f"paired difference run B - run A: {pct(m)} (SE {pct(se)}), 95% interval {pct(m-1.96*se)} to {pct(m+1.96*se)}")
print(f"smallest change this design detects reliably (80% power, 5% level) ~ 2.8 x SE = {pct(2.8*se)}")
# unpaired for contrast
sa, _ = se_of([sum(R[c][:3]) / 3 for c in ids]); sb, _ = se_of([sum(R[c][3:]) / 3 for c in ids])
print(f"unpaired SE would be {pct(math.sqrt(sa**2+sb**2))}")

print("\n== Resampling: how often does a random 3-trial run differ from another by >= X? ==")
random.seed(13)
diffs = []
for _ in range(20000):
    s1 = s2 = 0
    for c in ids:
        idx = random.sample(range(6), 6); s1 += sum(R[c][i] for i in idx[:3]); s2 += sum(R[c][i] for i in idx[3:])
    diffs.append(abs(s1 - s2) / 108)
for t in (0.02, 0.05, 0.08):
    print(f"|difference| >= {pct(t)}: {pct(sum(x >= t - 1e-9 for x in diffs)/len(diffs))} of re-splits")
print(f"95th percentile of |difference|: {pct(sorted(diffs)[int(0.95*len(diffs))])}")
