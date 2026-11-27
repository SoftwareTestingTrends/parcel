"""Run the over-limit cases with the £50 check inside the refund tool switched off, so only the
prompt keeps Parcel under the limit. Shows what the path was heading for when the guard caught it.
  PARCEL_BACKEND=ollama PARCEL_REFUND_GUARD=off uv run python evals/run_guard_off.py 3"""
import json
import sys
import time
from pathlib import Path

from parcel.assistant import Parcel
from parcel.config import Settings

HERE = Path(__file__).parent
OVER_LIMIT = ["towels-over-limit", "chair-over-limit", "chair-split-refund", "duvet-over-limit",
              "two-refunds-one-order", "angry-heater-stopped-working"]

settings = Settings.from_env()
assert not settings.refund_guard, "set PARCEL_REFUND_GUARD=off"
cases = {c["id"]: c for c in json.loads((HERE / "cases.json").read_text())}
trials = int(sys.argv[1]) if len(sys.argv) > 1 else 3
with (HERE / "runs/guard_off.jsonl").open("w", encoding="utf-8") as f:
    for trial in range(1, trials + 1):
        for name in OVER_LIMIT:
            parcel = Parcel(settings)
            for message in cases[name]["messages"]:
                parcel.ask(message)
            record = {"case": name, "trial": trial, "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                      **parcel.transcript.to_dict()}
            f.write(json.dumps(record) + "\n")
            f.flush()
            print(name, trial, record["end_state"]["refunds"], flush=True)
