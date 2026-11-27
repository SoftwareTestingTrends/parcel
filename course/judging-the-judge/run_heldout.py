"""Held-out set for "Who checks the judge?": runs every case three more times (trials 4-6) on Gemma 4 and
saves the transcripts to evals/runs/heldout.jsonl. Nobody looks at these until they're labelled by hand.
  PARCEL_BACKEND=ollama uv run python <this file>
Resumes: skips (case, trial) already saved.
"""
import json
import time
from pathlib import Path

from parcel.assistant import Parcel
from parcel.config import Settings

HERE = Path(__file__).parent / "evals"
cases = json.loads((HERE / "cases.json").read_text())
out = HERE / "runs/heldout.jsonl"
done = {(r["case"], r["trial"]) for r in map(json.loads, out.open())} if out.exists() else set()
with out.open("a", encoding="utf-8") as f:
    for trial in (4, 5, 6):
        for case in cases:
            if (case["id"], trial) in done:
                continue
            parcel = Parcel(Settings.from_env())
            for message in case["messages"]:
                parcel.ask(message)
            record = {"case": case["id"], "trial": trial,
                      "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%S"), **parcel.transcript.to_dict()}
            f.write(json.dumps(record) + "\n")
            f.flush()
            print(case["id"], trial, flush=True)
