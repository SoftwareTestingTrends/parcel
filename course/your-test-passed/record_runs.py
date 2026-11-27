"""Lesson: Your test passed. Was the answer any good?

Asks Parcel the same questions several times on two models and saves every
transcript, so the lesson's numbers come from real runs.

Run from this folder:
  uv run python record_runs.py <backend> <repeats>
"""

import json
import subprocess
import sys
import time
from pathlib import Path

from parcel import __version__
from parcel.assistant import Parcel
from parcel.config import Settings

CONVERSATIONS = {
    "spain": ["Do you deliver to Spain?"],
    "refund-time": ["How long does a refund take?"],
    "money-back": ["When will I get my money back?"],
    "cracked-chair": [
        "My order HL-10252 arrived with a cracked chair leg. Can I get my money back?",
        "dev.patel@example.com",
    ],
}

backend, repeats = sys.argv[1], int(sys.argv[2])
only = sys.argv[3:] or list(CONVERSATIONS)
parcel_repo = Path(__file__).resolve().parents[2]
commit = subprocess.run(
    ["git", "-C", str(parcel_repo), "rev-parse", "--short", "HEAD"], capture_output=True, text=True
).stdout.strip()
out = Path("runs") / f"{backend}.jsonl"
with out.open("a", encoding="utf-8") as f:
    for name in only:
        for i in range(1, repeats + 1):
            parcel = Parcel(Settings.from_env(backend=backend, trace_dir="runs/traces"))
            for message in CONVERSATIONS[name]:
                parcel.ask(message)
            record = {
                "conversation": name,
                "repeat": i,
                "parcel_version": __version__,
                "parcel_commit": commit,
                "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                **parcel.transcript.to_dict(),
            }
            f.write(json.dumps(record) + "\n")
            f.flush()
            print(name, i, round(parcel.transcript.seconds, 1), "s:", parcel.transcript.final_reply[:90])
