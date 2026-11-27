"""The code graders from "Checks a script can make", run through DeepEval. No model calls.
  uv run --with deepeval pytest evals/test_parcel_deepeval.py      (or: deepeval test run …)"""
import json
from pathlib import Path

import pytest
from deepeval import assert_test

from graders import BY_EXPECT_KEY, EVERY_TRIAL
from parcel_deepeval import CodeGraderMetric, to_test_case

HERE = Path(__file__).parent
CASES = {c["id"]: c for c in json.loads((HERE / "cases.json").read_text())}
TRIALS = [json.loads(line) for line in (HERE / "runs/six_trials.jsonl").open()]


@pytest.mark.parametrize("t", TRIALS, ids=lambda t: f"{t['case']}-t{t['trial']}")
def test_parcel(t):
    expected = [CodeGraderMetric(BY_EXPECT_KEY[k], v) for k, v in CASES[t["case"]]["expect"].items()]
    every_trial = [CodeGraderMetric(g) for g in EVERY_TRIAL]
    assert_test(to_test_case(t), expected + every_trial, run_async=False)
