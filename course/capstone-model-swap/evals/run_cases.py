"""Run every case in cases.json N times and save the transcripts (the suite runner the CI workflow calls).
  PARCEL_BACKEND=ollama uv run python evals/run_cases.py --trials 3 --out evals/runs/candidate.jsonl"""
import argparse
import json
import time
from pathlib import Path

from parcel.assistant import Parcel
from parcel.config import Settings

HERE = Path(__file__).parent
parser = argparse.ArgumentParser()
parser.add_argument("--trials", type=int, default=3)
parser.add_argument("--out", default=str(HERE / "runs/candidate.jsonl"))
args = parser.parse_args()

cases = json.loads((HERE / "cases.json").read_text())
with open(args.out, "w", encoding="utf-8") as f:
    for trial in range(1, args.trials + 1):
        for case in cases:
            parcel = Parcel(Settings.from_env())
            for message in case["messages"]:
                parcel.ask(message)
            f.write(json.dumps({"case": case["id"], "trial": trial,
                                "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                                **parcel.transcript.to_dict()}) + "\n")
            f.flush()
