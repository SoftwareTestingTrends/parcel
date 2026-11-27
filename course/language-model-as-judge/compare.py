"""Compares each judge run, and the code grader refund_claims_match, with the hand labels. Writes compare.txt."""
import json, sys
from collections import Counter, defaultdict
sys.path.insert(0, "evals")
from graders import refund_claims_match
from hand_labels import label, BORDERLINE

trials = {(t["case"], t["trial"]): t for t in map(json.loads, open("evals/runs/trials.jsonl"))}
runs = defaultdict(dict)
for r in map(json.loads, open("judgements.jsonl")):
    runs[r["run"]][(r["case"], r["trial"])] = r
runs["code: refund_claims_match"] = {k: {"verdict": "FAIL" if refund_claims_match(t) else "PASS"} for k, t in trials.items()}

lines = []
for name in ["narrow-1", "narrow-2", "narrow-no-examples", "broad", "code: refund_claims_match"]:
    v = runs[name]
    c = Counter((label(*k), v[k]["verdict"]) for k in trials)
    lines.append(f"{name:28} judge FAIL {sum(x['verdict']=='FAIL' for x in v.values()):3}  "
                 f"agrees {c[('FAIL','FAIL')]+c[('PASS','PASS')]:3}/108  "
                 f"caught {c[('FAIL','FAIL')]}/6 hand-labelled fails  false alarms {c[('PASS','FAIL')]}  "
                 f"other {sum(n for (h,j),n in c.items() if j not in ('PASS','FAIL'))}")
    for k in sorted(trials):
        h, j = label(*k), v[k]["verdict"]
        if h != j:
            lines.append(f"    {k[0]} t{k[1]}: hand {h}{' (borderline)' if k in BORDERLINE else ''}, {name} {j}")
same = sum(runs["narrow-1"][k]["verdict"] == runs["narrow-2"][k]["verdict"] for k in trials)
lines.append(f"\nnarrow-1 vs narrow-2: same verdict on {same}/108")
Path = __import__("pathlib").Path
Path("compare.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
