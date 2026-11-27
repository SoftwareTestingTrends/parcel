"""DeepEval's built-in ToolCorrectnessMetric on the 216 trials, next to our own path checks.
Expected tools come from each case's expected result. No model calls (no available_tools given).
  uv run --with deepeval python evals/tool_correctness_check.py"""
import json
from collections import Counter
from pathlib import Path

from deepeval.metrics import ToolCorrectnessMetric
from deepeval.test_case import ToolCall

from parcel_deepeval import ClaudeJudge, to_test_case
from path_check import path_problems

HERE = Path(__file__).parent
cases = {c["id"]: c for c in json.loads((HERE / "cases.json").read_text())}


def expected_tools(expect):
    tools = []
    if expect.get("lookup", "none") != "none":
        tools.append(ToolCall(name="lookup_order"))
    if expect.get("refund", "none") != "none":
        tools.append(ToolCall(name="issue_refund"))
    if expect.get("hand_off", "none") != "none":
        tools.append(ToolCall(name="hand_off"))
    return tools


# Passing a model object stops DeepEval building its default OpenAI judge; this metric never calls it.
metric = ToolCorrectnessMetric(model=ClaudeJudge(), async_mode=False, include_reason=False)
table = Counter()
for t in map(json.loads, open(HERE / "runs/six_trials.jsonl")):
    tc = to_test_case(t)
    tc.expected_tools = expected_tools(cases[t["case"]]["expect"])
    metric.measure(tc)
    path = path_problems(t)
    table[("ToolCorrectness pass" if metric.success else "ToolCorrectness FAIL",
           "path ok" if not path else "path broken")] += 1
    if path:
        print(f"{t['case']} t{t['trial']}: score {metric.score:.2f} {'pass' if metric.success else 'FAIL'} | path: {path[0]}")
print()
for k, n in sorted(table.items()):
    print(f"{k[0]:22} {k[1]:12} {n}")
