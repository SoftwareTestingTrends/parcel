"""Parcel's eval suite. Grades saved transcripts and saved judge verdicts, so it runs in seconds:
  uv run pytest evals/test_parcel.py
Record fresh transcripts with evals/run_cases.py, then judge them with evals/judge_trials.py.
"""
import json
from pathlib import Path

import pytest

from graders import BY_EXPECT_KEY, EVERY_TRIAL

HERE = Path(__file__).parent
CASES = {c["id"]: c for c in json.loads((HERE / "cases.json").read_text())}
TRIALS = [json.loads(line) for line in (HERE / "runs/trials.jsonl").open()]
JUDGED = HERE / "runs/judgements.jsonl"
VERDICTS = {(r["case"], r["trial"]): r for r in map(json.loads, JUDGED.open())} if JUDGED.exists() else {}


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


@pytest.mark.parametrize("trial", TRIALS, ids=ids)
def test_replies_match_actions(trial):
    """Model-graded: does every reply describe Parcel's refunds and hand-offs the way the tool calls show?"""
    verdict = VERDICTS.get((trial["case"], trial["trial"]))
    if verdict is None:
        pytest.skip("not judged yet: run evals/judge_trials.py")
    assert verdict["verdict"] == "PASS", verdict["reasoning"]
