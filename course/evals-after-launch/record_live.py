"""Lesson: Evals don't stop at release. Runs the 150 simulated live conversations once each on
Gemma 4 (Ollama, default settings), shipped prompt v2, and saves every trace to runs/live.jsonl.
Resumable. Run from this folder:  uv run python record_live.py
"""
import json, subprocess, time
from pathlib import Path
from parcel.assistant import Parcel
from parcel.config import Settings
from live_traffic import CONVERSATIONS

commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                        capture_output=True, text=True).stdout.strip()
out = Path("runs/live.jsonl")
done = {json.loads(l)["conversation"] for l in out.open()} if out.exists() else set()
with out.open("a", encoding="utf-8") as f:
    for cid, week, day, messages in CONVERSATIONS:
        if cid in done:
            continue
        parcel = Parcel(Settings.from_env(backend="ollama", trace_dir="runs/traces"))
        for m in messages:
            parcel.ask(m)
        f.write(json.dumps({"conversation": cid, "week": week, "day": day, "parcel_commit": commit,
                            "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%S"), **parcel.transcript.to_dict()}) + "\n")
        f.flush()
        print(cid, round(parcel.transcript.seconds, 1), "s |", parcel.transcript.final_reply[:90].replace("\n", " "), flush=True)
