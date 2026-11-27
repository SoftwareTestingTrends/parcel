"""Simulated thumbs up / down. Parcel has no real customers, so feedback follows a stated rule:
about 1 customer in 5 leaves a rating (random, seed 22). A customer rates down when they didn't get
what they came for: Parcel said it didn't know, said no, or passed them to a person. Otherwise up.
The rule knows nothing about whether Parcel was right; that is the point of comparing it with notes.py."""
import json, random, re, sys
sys.path.insert(0, "evals")
from graders import replies
from live_checks import says_dont_know
from notes import NOTES

SAID_NO = re.compile(r"\b(unfortunately|I'm afraid|I am afraid|cannot|can't|unable to)\b", re.I)
traces = [json.loads(l) for l in open("runs/live.jsonl")]
rng = random.Random(22)
rated = []
for t in traces:
    if rng.random() < 0.2:
        down = says_dont_know(t) or bool(SAID_NO.search(" ".join(replies(t)))) or bool(t["end_state"]["hand_offs"])
        rated.append((t["conversation"], "down" if down else "up"))
downs = [c for c, r in rated if r == "down"]; ups = [c for c, r in rated if r == "up"]
print(f"{len(rated)} of {len(traces)} rated: {len(ups)} up, {len(downs)} down")
print(f"downs that are real failures: {sum(c in NOTES for c in downs)} of {len(downs)}  {[c for c in downs if c in NOTES]}")
print(f"ups that are real failures:   {sum(c in NOTES for c in ups)} of {len(ups)}  {[c for c in ups if c in NOTES]}")
print(f"failures that got any rating: {sum(c in NOTES for c, _ in rated)} of {len(NOTES)}")
print("downs:", downs)
