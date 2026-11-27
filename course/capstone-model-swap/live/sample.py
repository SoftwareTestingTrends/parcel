"""The weekly read: a fixed random sample of 10 conversations per week (seed 22), printed in full."""
import json, random
traces = [json.loads(l) for l in open("runs/live.jsonl")]
rng = random.Random(22)
for week in ("week 1", "week 2"):
    for t in sorted(rng.sample([t for t in traces if t["week"] == week], 10), key=lambda t: t["conversation"]):
        print("=====", t["conversation"], t["day"])
        for e in t["events"]:
            if e["type"] == "customer": print("C:", e["text"])
            elif e["type"] == "retrieval": print("   R:", [a["id"] for a in e["articles"]])
            elif e["type"] == "tool_call": print("   T:", e["name"], e["args"], e["result"][:160])
            else: print("P:", e["text"])
        print("   END:", [(r["amount_gbp"], r["reason"]) for r in t["end_state"]["refunds"]], [h["reason"] for h in t["end_state"]["hand_offs"]])
