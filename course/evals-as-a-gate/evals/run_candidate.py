"""Run the whole eval set against a candidate change: Parcel's prompt with one sentence removed
(a "tidy-up" that deletes the rule against promising a person sooner). 3 trials of every case.
  PARCEL_BACKEND=ollama uv run python evals/run_candidate.py 3"""
import json
import sys
import time
from pathlib import Path

from parcel.assistant import Parcel
from parcel.config import Settings
from parcel.prompts import SYSTEM_PROMPT

HERE = Path(__file__).parent
TIDIED = SYSTEM_PROMPT.replace(' Don\'t promise anything sooner, such as "shortly" or "stay on the line".', "")
assert TIDIED != SYSTEM_PROMPT, "sentence not found"

cases = json.loads((HERE / "cases.json").read_text())
trials = int(sys.argv[1]) if len(sys.argv) > 1 else 3
with (HERE / "runs/candidate_tidy_prompt.jsonl").open("w", encoding="utf-8") as f:
    for trial in range(1, trials + 1):
        for case in cases:
            parcel = Parcel(Settings.from_env(), system_prompt=TIDIED, prompt_version="v2-tidy")
            for message in case["messages"]:
                parcel.ask(message)
            record = {"case": case["id"], "trial": trial, "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                      **parcel.transcript.to_dict()}
            f.write(json.dumps(record) + "\n")
            f.flush()
            print(case["id"], trial, flush=True)
