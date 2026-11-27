"""Find the turn where a conversation first went wrong: grade the conversation as it stood after
each of Parcel's replies, with the checks that apply at every turn, and report the first failure.
  uv run python evals/first_bad_turn.py runs/six_trials.jsonl"""
import json
import sys
from collections import Counter

from graders import EVERY_TRIAL


def turns(t):
    """The conversation cut after each of Parcel's replies: [(1, first part), (2, first two parts), …]."""
    cuts, events = [], []
    for e in t["events"]:
        events.append(e)
        if e["type"] == "parcel":
            cuts.append((len(cuts) + 1, {**t, "events": list(events)}))
    return cuts


def first_bad_turn(t):
    for n, part in turns(t):
        problems = [p for grader in EVERY_TRIAL for p in grader(part)]
        if problems:
            return n, problems
    return None, []


if __name__ == "__main__":
    found = Counter()
    for t in map(json.loads, open(sys.argv[1])):
        total = len(turns(t))
        if total < 2:
            continue
        n, problems = first_bad_turn(t)
        found["multi-turn conversations"] += 1
        if n:
            found[f"first went wrong at turn {n}"] += 1
            name = t.get("conversation") or f"{t['case']} t{t['trial']}"
            print(f"{name}: turn {n} of {total}: {problems[0]}")
    print()
    for k, v in sorted(found.items()):
        print(f"{k}: {v}")
