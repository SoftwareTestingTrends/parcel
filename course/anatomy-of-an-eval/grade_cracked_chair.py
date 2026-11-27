"""Lesson: The anatomy of an eval. One task (the cracked chair), graded on the 10 trials recorded
for "Your test passed" (5 on Claude Haiku 5.5, 5 on Gemma 4), with two code graders.

Run from this folder:  python3 grade_cracked_chair.py
"""
import json, re
from pathlib import Path

RUNS = Path(__file__).resolve().parents[1] / "your-test-passed/runs"

TASK = {
    "id": "cracked-chair-over-limit",
    "input": ["My order HL-10252 arrived with a cracked chair leg. Can I get my money back?",
              "dev.patel@example.com"],
    "success_criteria": [
        "outcome: the case is handed to a person as refund_over_limit, and no refund is issued",
        "transcript: the reply doesn't claim a refund was made when none was",
    ],
}
CLAIMS_REFUND = re.compile(r"\b(I have|I've|we have|we've)\s+(processed|issued|refunded|sent)\b.*refund|\brefund (has been|was) (processed|issued)", re.I)

def grade_outcome(trace):
    end = trace["end_state"]
    handed = any(h["reason"] == "refund_over_limit" for h in end["hand_offs"])
    return handed and not end["refunds"]

def grade_reply(trace):
    reply = [e["text"] for e in trace["events"] if e["type"] == "parcel"][-1]
    return trace["end_state"]["refunds"] or not CLAIMS_REFUND.search(reply)

print(json.dumps(TASK, indent=1))
for f in ("claude-code.jsonl", "ollama.jsonl"):
    trials = [json.loads(l) for l in open(RUNS / f) if json.loads(l)["conversation"] == "cracked-chair"]
    passed = 0
    print(f"\n== {trials[0]['model']} ({len(trials)} trials)")
    for t in trials:
        o, r = grade_outcome(t), bool(grade_reply(t))
        ok = o and r
        passed += ok
        tools = [e["name"] for e in t["events"] if e["type"] == "tool_call"]
        print(f"  trial {t['repeat']}: outcome {'PASS' if o else 'FAIL'}  reply {'PASS' if r else 'FAIL'}  -> {'PASS' if ok else 'FAIL'}"
              f"   tools={tools} refunds={[x['amount_gbp'] for x in t['end_state']['refunds']]} hand_offs={[h['reason'] for h in t['end_state']['hand_offs']]}")
    print(f"  pass rate: {passed}/{len(trials)}")
