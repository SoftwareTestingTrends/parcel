"""Lesson: Building an eval dataset. Runs every case in evals/cases.json three times on Gemma 4
(Ollama, default settings, Parcel's current prompt) and saves each transcript to runs/trials.jsonl.
Run from this folder:  uv run python run.py
"""
import json, subprocess, time
from pathlib import Path
from parcel.assistant import Parcel
from parcel.config import Settings

cases = json.loads(Path("evals/cases.json").read_text())
commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                        capture_output=True, text=True).stdout.strip()
out = Path("runs/trials.jsonl")
out.parent.mkdir(exist_ok=True)
done = {(r["case"], r["trial"]) for r in map(json.loads, out.open())} if out.exists() else set()
with out.open("a", encoding="utf-8") as f:
    for trial in (1, 2, 3):
        for case in cases:
            if (case["id"], trial) in done:
                continue
            t0 = time.time()
            parcel = Parcel(Settings.from_env(backend="ollama", trace_dir="runs/traces"))
            for m in case["messages"]:
                parcel.ask(m)
            f.write(json.dumps({"case": case["id"], "trial": trial, "parcel_commit": commit,
                                "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%S"), **parcel.transcript.to_dict()}) + "\n")
            f.flush()
            print(case["id"], trial, f"{time.time() - t0:.1f} s |", parcel.transcript.final_reply[:80].replace("\n", " "),
                  flush=True)
