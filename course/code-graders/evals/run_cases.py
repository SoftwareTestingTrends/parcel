"""Runs every case in evals/cases.json three times and saves each transcript to evals/runs/trials.jsonl.
  PARCEL_BACKEND=ollama uv run python evals/run_cases.py
Then grade them with:  uv run pytest evals/
"""
import json
import time
from pathlib import Path

from parcel.assistant import Parcel
from parcel.config import Settings

HERE = Path(__file__).parent
TRIALS = 3

cases = json.loads((HERE / "cases.json").read_text())
out = HERE / "runs/trials.jsonl"
out.parent.mkdir(exist_ok=True)
with out.open("w", encoding="utf-8") as f:
    for trial in range(1, TRIALS + 1):
        for case in cases:
            parcel = Parcel(Settings.from_env())
            for message in case["messages"]:
                parcel.ask(message)
            record = {"case": case["id"], "trial": trial,
                      "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%S"), **parcel.transcript.to_dict()}
            f.write(json.dumps(record) + "\n")
            f.flush()
            print(case["id"], trial, flush=True)
