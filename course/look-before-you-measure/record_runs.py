"""Lesson: Look at the outputs before you measure them. Runs all 100 conversations once on
Gemma 4 (Ollama, default settings) and saves every transcript to runs/gemma4.jsonl.
Run from this folder:  uv run python record_runs.py
"""
import json, subprocess, time
from pathlib import Path
from parcel import __version__
from parcel.assistant import Parcel
from parcel.config import Settings
from conversations import CONVERSATIONS

commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                        capture_output=True, text=True).stdout.strip()
out = Path("runs/gemma4.jsonl")
done = {json.loads(l)["conversation"] for l in out.open()} if out.exists() else set()
with out.open("a", encoding="utf-8") as f:
    for cid, messages in CONVERSATIONS:
        if cid in done:
            continue
        parcel = Parcel(Settings.from_env(backend="ollama", trace_dir="runs/traces"))
        for m in messages:
            parcel.ask(m)
        f.write(json.dumps({"conversation": cid, "parcel_version": __version__, "parcel_commit": commit,
                            "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%S"), **parcel.transcript.to_dict()}) + "\n")
        f.flush()
        print(cid, round(parcel.transcript.seconds, 1), "s |", parcel.transcript.final_reply[:90].replace("\n", " "), flush=True)
