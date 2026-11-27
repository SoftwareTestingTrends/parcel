"""Runs the judge from "When a model does the grading" (narrow rubric, with examples, unchanged) once over the
held-out transcripts and saves evals/runs/heldout_judgements.jsonl. 108 Claude calls, two at a time; resumes;
stops at a usage-limit reply."""
import json, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, "evals")
from judge import JUDGE_MODEL, judge

OUT = Path("evals/runs/heldout_judgements.jsonl")
trials = [json.loads(l) for l in open("evals/runs/heldout.jsonl")]
done = {(r["case"], r["trial"]) for r in map(json.loads, OUT.open())} if OUT.exists() else set()
todo = [t for t in trials if (t["case"], t["trial"]) not in done]


def one(t):
    return {"case": t["case"], "trial": t["trial"], "judge_model": JUDGE_MODEL,
            "judged_at": time.strftime("%Y-%m-%dT%H:%M:%S"), **judge(t)}


with OUT.open("a", encoding="utf-8") as f, ThreadPoolExecutor(max_workers=2) as pool:
    for r in pool.map(one, todo):
        if r["verdict"] == "UNPARSEABLE":
            print("No verdict (usage limit?):", r["reasoning"][:200]); pool.shutdown(wait=False, cancel_futures=True); sys.exit(1)
        f.write(json.dumps(r) + "\n"); f.flush()
        print(r["case"], r["trial"], r["verdict"], flush=True)
