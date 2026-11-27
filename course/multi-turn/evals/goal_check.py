"""Did the customer get what they came for? Checked on the end state, not on the path, so it works
for simulated conversations that don't follow a script. Run with the every-turn code graders.
  uv run python evals/goal_check.py runs/simulated.jsonl"""
import json
import sys
from pathlib import Path

from graders import EVERY_TRIAL, handed_off_as, looked_up, refunded

HERE = Path(__file__).parent


def find(path):
    """The path as given, or else next to this script (so lesson commands work from the lesson folder)."""
    p = Path(path)
    return p if p.exists() else HERE / path


def handed_off(t):
    return bool(t["end_state"]["hand_offs"])


def lookup_worked(t, order_id):
    return not looked_up(t, order_id)        # looked_up returns problems; none means it succeeded


GOALS = {   # the customer's goal, or the correct next step under Parcel's rules
    "chair-over-limit": lambda t: not refunded(t) and not handed_off_as(t, "refund_over_limit"),
    "angry-heater-stopped-working": lambda t: not refunded(t) and not handed_off_as(t, "refund_over_limit"),
    "two-refunds-one-order": lambda t: refunded(t) == 30 and not handed_off_as(t, "refund_over_limit"),
    "order-number-without-dash": lambda t: lookup_worked(t, "HL-10251") or handed_off(t),
    "typos-late-candles": lambda t: lookup_worked(t, "HL-10260") or handed_off(t),
    "vague-no-order-details": lambda t: not refunded(t) and handed_off(t),
}

if __name__ == "__main__":
    passed = total = 0
    for t in map(json.loads, open(find(sys.argv[1]))):
        problems = [p for grader in EVERY_TRIAL for p in grader(t)]
        goal = GOALS[t["case"]](t)
        total += 1
        passed += goal and not problems
        turns = sum(e["type"] == "customer" for e in t["events"])
        verdict = "PASS" if goal and not problems else "FAIL"
        print(f"{t['case']} t{t['trial']}: {turns} turns, goal {'met' if goal else 'NOT met'}, "
              f"{'; '.join(problems) or 'no rule broken'} -> {verdict}")
    print(f"\n{passed} of {total} conversations pass")
