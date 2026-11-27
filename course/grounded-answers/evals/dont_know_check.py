"""Does Parcel say it doesn't know exactly when it should? Uses the search labels from
"Did it find the right article?" (copied to search_labels.py).
- No article answers the question (empty label): the reply should say it doesn't know, or hand off.
- The search found every article the question needs: the reply shouldn't say it doesn't know.
  uv run python evals/dont_know_check.py runs/gemma4-prompt-v2.jsonl"""
import json
import re
import sys

from search_labels import LABELS

DOESNT_KNOW = re.compile(
    r"don't have (any )?(specific )?information|do not have (any |specific )?information|don't know|isn't in my help"
    r"|don't specify|don't mention|don't have any instructions|don't have recommendations"
    r"|don't see any information", re.I)

should_say, said, shouldnt_say, wrongly_said = 0, 0, 0, []
for t in map(json.loads, open(sys.argv[1])):
    message, given = 0, set()
    handed_off = any(e["type"] == "tool_call" and e["name"] == "hand_off" for e in t["events"])
    for e in t["events"]:
        if e["type"] == "customer":
            message += 1
        elif e["type"] == "retrieval":
            given = {a["id"] for a in e["articles"]}
        elif e["type"] == "parcel" and (t["conversation"], message) in LABELS:
            relevant = LABELS[(t["conversation"], message)]
            says_it = bool(DOESNT_KNOW.search(e["text"]))
            if not relevant:
                should_say += 1
                said += says_it or handed_off
            elif relevant <= given:
                shouldnt_say += 1
                if says_it:
                    wrongly_said.append(t["conversation"])

print(f"no article answers it: said it didn't know (or handed off) {said} of {should_say}")
print(f"had every article it needed: said it didn't know {len(wrongly_said)} of {shouldnt_say} {wrongly_said}")
