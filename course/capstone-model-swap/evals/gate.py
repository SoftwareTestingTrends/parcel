"""A release gate for Parcel: grade a candidate run, compare it with a baseline run, apply the rules,
and exit non-zero if the release is blocked (so CI stops).
  uv run python evals/gate.py runs/baseline.jsonl runs/candidate.jsonl

Rules
  1. Golden cases: every trial passes.                           (any failure blocks)
  2. Regression cases: none gets worse beyond noise. A case that passed every baseline trial
     must not fail 2 or more candidate trials.                    (blocks)
  3. Capability cases: pass rates reported, never block.
  4. Budget: 95th-percentile time per conversation and mean tokens per conversation may not
     rise more than 20% above the baseline.                       (blocks)"""
import json
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean

from graders import BY_EXPECT_KEY, EVERY_TRIAL

HERE = Path(__file__).parent


def find(path):
    """The path as given, or else next to this script (so lesson commands work from the lesson folder)."""
    p = Path(path)
    return p if p.exists() else HERE / path
CASES = {c["id"]: c for c in json.loads((HERE / "cases.json").read_text())}
BUDGET_RISE = 0.20


def problems(t):
    expect = CASES[t["case"]]["expect"]
    return ([p for k, v in expect.items() for p in BY_EXPECT_KEY[k](t, v)]
            + [p for g in EVERY_TRIAL for p in g(t)])


def load(path):
    runs = [json.loads(line) for line in open(find(path))]
    results = defaultdict(list)                    # case -> [problems per trial]
    for t in runs:
        results[t["case"]].append(problems(t))
    return runs, results


def p95(xs):
    xs = sorted(xs)
    return xs[max(0, int(0.95 * len(xs)) - 1)]


def budget(runs):
    return (p95([t["seconds"] for t in runs]),
            mean(t["usage"]["input_tokens"] + t["usage"]["output_tokens"] for t in runs))


def gate(baseline_path, candidate_path):
    base_runs, base = load(baseline_path)
    cand_runs, cand = load(candidate_path)
    blocks, notes = [], []

    for case_id, trials in sorted(cand.items()):
        c = CASES[case_id]
        fails = [p for p in trials if p]
        if c.get("golden") and fails:
            before = sum(bool(p) for p in base.get(case_id, []))
            already = f"; baseline failed {before} of {len(base.get(case_id, []))}" if before else "; new"
            blocks.append(f"golden {case_id}: failed {len(fails)} of {len(trials)} ({fails[0][0]}{already})")
        elif c["type"] == "regression" and not c.get("golden"):
            base_clean = not any(base.get(case_id, [[]]))
            if base_clean and len(fails) >= 2:
                blocks.append(f"regression {case_id}: passed every baseline trial, failed {len(fails)} of "
                              f"{len(trials)} ({fails[0][0]})")
        elif c["type"] == "capability":
            b = sum(not p for p in base.get(case_id, []))
            notes.append(f"capability {case_id}: {len(trials) - len(fails)} of {len(trials)} "
                         f"(baseline {b} of {len(base.get(case_id, []))})")

    (bt, btok), (ct, ctok) = budget(base_runs), budget(cand_runs)
    for name, b, c in [("p95 seconds per conversation", bt, ct), ("mean tokens per conversation", btok, ctok)]:
        line = f"{name}: {c:,.0f} (baseline {b:,.0f}, limit {b * (1 + BUDGET_RISE):,.0f})"
        (blocks if c > b * (1 + BUDGET_RISE) else notes).append(("budget " if c > b * (1 + BUDGET_RISE) else "") + line)

    for n in notes:
        print("  ", n)
    print()
    for b in blocks:
        print("BLOCK", b)
    print("\nRELEASE BLOCKED" if blocks else "\nRELEASE OK")
    return 1 if blocks else 0


if __name__ == "__main__":
    sys.exit(gate(sys.argv[1], sys.argv[2]))
