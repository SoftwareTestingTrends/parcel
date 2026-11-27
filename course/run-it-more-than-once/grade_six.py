"""Grade all 6 saved Gemma 4 trials of every case: code graders + hand label (replies match actions).
Writes per_trial.json: {case: [True/False x6]} and prints a per-case table."""
import json, sys
from pathlib import Path
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / "evals"))
from graders import BY_EXPECT_KEY, EVERY_TRIAL
cases = {c["id"]: c for c in json.loads((HERE / "evals/cases.json").read_text())}
labels = {(r["case"], r["trial"]): r["label"] for f in ("dev_labels.json", "heldout_labels.json")
          for r in json.loads((HERE / "evals" / f).read_text())}
res, why = {}, {}
for line in (HERE / "evals/runs/six_trials.jsonl").open():
    t = json.loads(line); c = cases[t["case"]]
    probs = [p for k, e in c["expect"].items() for p in BY_EXPECT_KEY[k](t, e)]
    probs += [p for g in EVERY_TRIAL for p in g(t)]
    if labels[(t["case"], t["trial"])] == "FAIL": probs.append("reply doesn't match actions (hand label)")
    res.setdefault(t["case"], [None]*6)[t["trial"]-1] = not probs
    why[f'{t["case"]} t{t["trial"]}'] = probs
json.dump({"pass": res, "problems": why}, open(HERE / "per_trial.json", "w"), indent=1)
for cid, r in res.items():
    c = cases[cid]
    print(f"{cid:34} {c['type'][:4]} {'G' if c['golden'] else ' '} {''.join('P' if x else '.' for x in r)}  1-3:{sum(r[:3])}/3 4-6:{sum(r[3:])}/3 all:{sum(r)}/6")
