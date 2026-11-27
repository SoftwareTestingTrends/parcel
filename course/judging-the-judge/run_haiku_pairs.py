"""Self-preference probe, step 1: runs 12 cases once with Parcel on Claude Haiku 5.5 (claude-code backend,
your Claude Code login), so each can be paired with Gemma 4's trial 1 of the same case.
  PARCEL_BACKEND=claude-code uv run python <this file>
Saves evals/runs/haiku.jsonl; resumes.
"""
import json
import time
from pathlib import Path

from parcel.assistant import Parcel
from parcel.config import Settings

PAIR_CASES = ["mug-chipped-refund", "towels-over-limit", "chair-over-limit", "lost-clock-no-instant-refund",
              "sofa-change-of-mind", "returned-lamp-already-refunded", "heater-smoking", "lamp-burnt-hand",
              "induction-hob-no-hand-off", "cancel-processing-order", "typos-late-candles", "calm-kettle-leaks-refund"]
HERE = Path(__file__).parent / "evals"
cases = {c["id"]: c for c in json.loads((HERE / "cases.json").read_text())}
out = HERE / "runs/haiku.jsonl"
done = {r["case"] for r in map(json.loads, out.open())} if out.exists() else set()
with out.open("a", encoding="utf-8") as f:
    for cid in PAIR_CASES:
        if cid in done:
            continue
        parcel = Parcel(Settings.from_env())
        for message in cases[cid]["messages"]:
            parcel.ask(message)
        record = {"case": cid, "trial": 1, "model": "claude-haiku-5-5",
                  "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%S"), **parcel.transcript.to_dict()}
        f.write(json.dumps(record) + "\n")
        f.flush()
        print(cid, flush=True)
