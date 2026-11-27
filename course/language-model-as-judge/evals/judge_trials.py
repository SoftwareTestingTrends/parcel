"""Run the judge over every saved transcript and save its verdicts, so pytest can grade them in seconds:
  uv run python evals/judge_trials.py
Uses the `claude` CLI and your Claude Code login: each transcript is one call, and the calls count against
your Claude usage. It runs two at a time, skips trials already judged, and stops at a usage-limit reply,
so you can run it again later to finish.
"""
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from judge import JUDGE_MODEL, judge

HERE = Path(__file__).parent
TRIALS = [json.loads(line) for line in (HERE / "runs/trials.jsonl").open()]
OUT = HERE / "runs/judgements.jsonl"


def one(t):
    return {"case": t["case"], "trial": t["trial"], "judge_model": JUDGE_MODEL,
            "judged_at": time.strftime("%Y-%m-%dT%H:%M:%S"), **judge(t)}


done = {(r["case"], r["trial"]) for r in map(json.loads, OUT.open())} if OUT.exists() else set()
todo = [t for t in TRIALS if (t["case"], t["trial"]) not in done]
with OUT.open("a", encoding="utf-8") as f, ThreadPoolExecutor(max_workers=2) as pool:
    for r in pool.map(one, todo):
        if r["verdict"] == "UNPARSEABLE":
            print("No verdict (usage limit?):", r["reasoning"][:200])
            pool.shutdown(wait=False, cancel_futures=True)
            sys.exit(1)
        f.write(json.dumps(r) + "\n")
        f.flush()
        print(r["case"], r["trial"], r["verdict"], flush=True)
