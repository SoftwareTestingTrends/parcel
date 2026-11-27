"""How consistent is Parcel? Grades every saved trial, then reads the results case by case.
  uv run python evals/consistency.py runs/six_trials.jsonl
A trial passes when every code grader passes and its reply matches what Parcel did (our hand label)."""
import json, random, sys
from pathlib import Path

from graders import BY_EXPECT_KEY, EVERY_TRIAL

HERE = Path(__file__).parent


def find(path):
    """The path as given, or else next to this script (so lesson commands work from the lesson folder)."""
    p = Path(path)
    return p if p.exists() else HERE / path
CASES = {c["id"]: c for c in json.loads((HERE / "cases.json").read_text())}
LABELS = {(r["case"], r["trial"]): r["label"]
          for f in ("dev_labels.json", "heldout_labels.json") for r in json.loads((HERE / f).read_text())}


def passed(t):
    case = CASES[t["case"]]
    problems = [p for key, want in case["expect"].items() for p in BY_EXPECT_KEY[key](t, want)]
    problems += [p for grader in EVERY_TRIAL for p in grader(t)]
    return not problems and LABELS[(t["case"], t["trial"])] == "PASS"


def pass_at_k(results):   # at least one of the k trials passed
    return any(results)


def pass_hat_k(results):  # every one of the k trials passed
    return all(results)


def rate(results_by_case, trials):
    total = sum(r[i] for r in results_by_case.values() for i in trials)
    return total / (len(results_by_case) * len(trials))


results_by_case = {}
for line in open(find(sys.argv[1])):
    t = json.loads(line)
    results_by_case.setdefault(t["case"], [None] * 6)[t["trial"] - 1] = passed(t)

print("single-trial runs:", ", ".join(f"{rate(results_by_case, [i]):.0%}" for i in range(6)))
a, b = rate(results_by_case, [0, 1, 2]), rate(results_by_case, [3, 4, 5])
print(f"trials 1-3: {a:.1%}   trials 4-6: {b:.1%}   (nothing changed in between)")
print(f"pass@6: {sum(map(pass_at_k, results_by_case.values()))} of {len(results_by_case)} cases")
print(f"pass^6: {sum(map(pass_hat_k, results_by_case.values()))} of {len(results_by_case)} cases")

# How far apart can two runs of the same Parcel be? Shuffle each case's six trials into
# two runs of three, many times, and see how much the two pass rates differ.
random.seed(13)
gaps = []
for _ in range(20_000):
    first = second = 0
    for results in results_by_case.values():      # six True/False per case
        order = random.sample(results, 6)
        first, second = first + sum(order[:3]), second + sum(order[3:])
    gaps.append(abs(first - second) / (3 * len(results_by_case)))
gaps.sort()
print(f"same Parcel, two runs of 3 trials: 95% of the time within {100 * gaps[int(0.95 * len(gaps))]:.1f} points of each other")
