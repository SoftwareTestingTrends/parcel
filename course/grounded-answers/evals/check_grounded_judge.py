"""Compare the groundedness judge with the hand labels. FAIL is the positive."""
import json
import sys
from grounded_labels import FAIL

verdicts = {r["conversation"]: r["verdict"] for r in map(json.loads, open(sys.argv[1]))}
real_fail = set(FAIL)
judge_fail = {c for c, v in verdicts.items() if v == "FAIL"}
passes = set(verdicts) - real_fail
print(f"hand labels: {len(real_fail)} FAIL, {len(passes)} PASS")
print(f"judge caught {len(real_fail & judge_fail)} of {len(real_fail)} real failures (TPR); missed {sorted(real_fail - judge_fail)}")
print(f"judge agreed with {len(passes - judge_fail)} of {len(passes)} real passes (TNR); failed {sorted(judge_fail - real_fail)}")
