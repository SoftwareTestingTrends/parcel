"""Lesson: Building an eval dataset. Checks each recorded trial against its case's expected result
(outcome only: lookups, refunds, hand-offs, and strings no reply may contain), then labels each case:
passes every trial now, or passed every trial in an earlier recorded run (passed_before) -> regression;
otherwise -> capability. Golden is set in build_cases.py.
Writes results.txt and evals/cases.json (with "type" filled in).
Run from this folder:  python3 check.py
"""
import json
from collections import defaultdict
from pathlib import Path


def failures(case, t):
    exp, fails = case["expect"], []
    calls = [e for e in t["events"] if e["type"] == "tool_call"]
    looked_up = [c["args"].get("order_id") for c in calls if c["name"] == "lookup_order" and not c["is_error"]]
    any_lookup = [c for c in calls if c["name"] == "lookup_order"]
    refunded = round(sum(r["amount_gbp"] for r in t["end_state"]["refunds"]), 2)
    reasons = [h["reason"] for h in t["end_state"]["hand_offs"]]
    replies = " ".join(e["text"] for e in t["events"] if e["type"] == "parcel")
    if "lookup" in exp:
        if exp["lookup"] == "none" and any_lookup:
            fails.append("looked up an order")
        elif exp["lookup"] != "none" and exp["lookup"] not in looked_up:
            fails.append(f"didn't look up {exp['lookup']}")
    if "refund" in exp:
        if exp["refund"] == "none" and refunded:
            fails.append(f"refunded £{refunded:g}")
        elif exp["refund"] != "none" and not exp["refund"][0] <= refunded <= exp["refund"][1]:
            fails.append(f"refunded £{refunded:g}, expected £{exp['refund'][0]:g}"
                         + (f"–{exp['refund'][1]:g}" if exp["refund"][1] != exp["refund"][0] else ""))
    if "hand_off" in exp:
        if exp["hand_off"] == "none" and reasons:
            fails.append("handed off as " + ", ".join(reasons))
        elif exp["hand_off"] != "none" and exp["hand_off"] not in reasons:
            fails.append("no hand-off" if not reasons else "handed off as " + ", ".join(reasons))
    for s in exp.get("reply_never", []):
        if s.lower() in replies.lower():
            fails.append(f"reply contains {s!r}")
    return fails


cases = json.loads(Path("evals/cases.json").read_text())
trials = defaultdict(list)
for t in map(json.loads, Path("runs/trials.jsonl").open()):
    trials[t["case"]].append(t)

lines, counts = [], defaultdict(int)
for case in cases:
    ts = sorted(trials[case["id"]], key=lambda t: t["trial"])
    results = [failures(case, t) for t in ts]
    passed = sum(not r for r in results)
    case["type"] = "regression" if (ts and passed == len(ts)) or case.get("passed_before") else "capability"
    counts[case["type"]] += 1
    counts["golden"] += case["golden"]
    if passed < len(ts):
        counts[case["type"] + " failing"] += 1
        counts["golden failing"] += case["golden"]
    tag = case["type"] + (", golden" if case["golden"] else "")
    lines.append(f"{case['id']:34} {passed}/{len(ts)}  {tag:22} {case['source']}")
    for i, r in enumerate(results, 1):
        if r:
            lines.append(f"{'':38}trial {i}: " + "; ".join(r))

summary = (f"{len(cases)} cases, {sum(len(v) for v in trials.values())} trials. "
           f"regression {counts['regression']} (failing at least one trial: {counts['regression failing']}), "
           f"capability {counts['capability']}, "
           f"golden {counts['golden']} (failing at least one trial: {counts['golden failing']})")
Path("results.txt").write_text(summary + "\n\n" + "\n".join(lines) + "\n")
Path("evals/cases.json").write_text(json.dumps(cases, indent=2, ensure_ascii=False) + "\n")
print(summary)
