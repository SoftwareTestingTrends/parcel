"""Run the two cases added from the live incident, 6 trials each, on Gemma 4 (Ollama), shipped prompt v2,
and grade them with the suite's graders (including the new promised_reply_has_ticket).
Run from this folder:  uv run python run_incident_cases.py"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, "evals")
from parcel.assistant import Parcel
from parcel.config import Settings
from graders import BY_EXPECT_KEY, EVERY_TRIAL

import os
cases = [c for c in json.loads(Path("evals/cases.json").read_text()) if "live w" in c["source"] and c["id"] in os.environ.get("ONLY", c["id"])]
out = Path("runs/incident_cases.jsonl")
with out.open("a", encoding="utf-8") as f:
    for case in cases:
        for trial in range(1, 7):
            parcel = Parcel(Settings.from_env(backend="ollama", trace_dir="runs/traces"))
            for m in case["messages"]:
                parcel.ask(m)
            t = {"case": case["id"], "trial": trial, "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                 **parcel.transcript.to_dict()}
            f.write(json.dumps(t) + "\n"); f.flush()
            problems = [p for k, v in case["expect"].items() for p in BY_EXPECT_KEY[k](t, v)] + \
                       [p for g in EVERY_TRIAL for p in g(t)]
            print(case["id"], trial, "PASS" if not problems else "FAIL " + "; ".join(problems),
                  "|", parcel.transcript.final_reply[:110].replace("\n", " "), flush=True)
