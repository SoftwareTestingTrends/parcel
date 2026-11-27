"""The test a tester writes first, run against five real Parcel answers.

    uv run pytest test_spain_exact.py -v

Each recorded run of "Do you deliver to Spain?" is checked two ways:
  - exact match: the reply must equal the answer we saw the first time
  - contains: the reply must mention the price and the delivery time
"""

import json
from pathlib import Path

import pytest

RUNS = [
    json.loads(line)
    for line in Path(__file__).with_name("runs").joinpath("claude-code.jsonl").open()
    if json.loads(line)["conversation"] == "spain"
]
REPLIES = [r["events"][-1]["text"] for r in sorted(RUNS, key=lambda r: r["repeat"])]
EXPECTED = REPLIES[0]  # the answer we saw the first time, saved as the "expected result"


@pytest.mark.parametrize("reply", REPLIES, ids=[f"run{i}" for i in range(1, len(REPLIES) + 1)])
def test_exact_match(reply):
    assert reply == EXPECTED


@pytest.mark.parametrize("reply", REPLIES, ids=[f"run{i}" for i in range(1, len(REPLIES) + 1)])
def test_contains_price_and_time(reply):
    assert "£9.95" in reply
    assert "5 to 8 working days" in reply
