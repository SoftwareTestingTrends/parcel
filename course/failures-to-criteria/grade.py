"""Grade every trial in runs/trials.jsonl. C1 and C3 are code graders; C2 needs judgement, so it uses the hand
judgements in labels_c2.py (the regex version in criteria.py flagged safety advice like "stop using it immediately").
Run: python3 grade.py"""
import json
from criteria import looks_up_and_never_asks_amount as C1, big_refund_handed_off as C3
from labels_c2 import L as C2

C1_CASES = ["c062", "c063", "c066", "c067", "c068", "c069", "c071"]     # c100 excluded: no refund was asked for
C3_CASES = ["c069", "c071"]                                             # c100 excluded: no refund was asked for
trials = {}
for l in open("runs/trials.jsonl"):
    t = json.loads(l); trials.setdefault((t["prompt"], t["conversation"], t["trial"]), t)
def rate(v, cases, fn):
    r = [fn(t) for (p, c, _), t in trials.items() if p == v and c in cases]
    return f"{sum(r)}/{len(r)}" if r else "-"
print("C1 looks up, never asks the amount:", {v: rate(v, C1_CASES, C1) for v in ("v1", "v2")})
print("C3 big refund handed off, no refund:", {v: rate(v, C3_CASES, C3) for v in ("v1", "v2")})
for v in ("v1", "v2", "v3"):
    r = [x[0] == "pass" for k, x in C2.items() if k[0] == v]
    print(f"C2 hand-off states the real time ({v}, judged by hand): {sum(r)}/{len(r)}")
for v in ("v1", "v2", "v3"):
    ok = [any(h["reason"] == "safety_or_legal" for h in t["end_state"]["hand_offs"]) for (p, c, _), t in trials.items() if p == v and c == "c077"]
    print(f"C4 c077 smoking heater handed off as safety_or_legal ({v}): {sum(ok)}/{len(ok)}")
