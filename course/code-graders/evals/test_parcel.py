"""Parcel's eval suite, graded by code. Grades saved transcripts, so it runs in seconds:
  uv run pytest evals/test_parcel.py
Record fresh transcripts first with evals/run_cases.py (about a minute per case on Gemma 4).
"""
import json
from pathlib import Path

import pytest

from graders import BY_EXPECT_KEY, EVERY_TRIAL

HERE = Path(__file__).parent
CASES = {c["id"]: c for c in json.loads((HERE / "cases.json").read_text())}
TRIALS = [json.loads(line) for line in (HERE / "runs/trials.jsonl").open()]


def ids(t):
    return f"{t['case']}-t{t['trial']}"


@pytest.mark.parametrize("trial", TRIALS, ids=ids)
def test_expected_result(trial):
    case = CASES[trial["case"]]
    problems = [p for key, expected in case["expect"].items() for p in BY_EXPECT_KEY[key](trial, expected)]
    assert not problems, "; ".join(problems)


@pytest.mark.parametrize("grader", EVERY_TRIAL, ids=lambda g: g.__name__)
@pytest.mark.parametrize("trial", TRIALS, ids=ids)
def test_every_trial(trial, grader):
    problems = grader(trial)
    assert not problems, "; ".join(problems)
