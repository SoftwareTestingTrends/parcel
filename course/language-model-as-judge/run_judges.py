"""Lesson: When a model does the grading. Runs the judge over the 108 transcripts from "Building an eval
dataset" in four ways and saves every verdict to judgements.jsonl:
  narrow-1, narrow-2: the narrow rubric with labelled examples (run twice, to see if it repeats itself)
  narrow-no-examples: the same rubric without the examples
  broad: a broad rubric ("is this a good reply?"), for comparison
Run from this folder:  python3 run_judges.py [run ...]   (needs the `claude` CLI, logged in)
With no run names it does all four. It stops at the first usage-limit reply, so nothing bad is saved.
"""
import json, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, "evals")
from judge import ask_claude, judge, parse, render, JUDGE_MODEL

BROAD = """You are grading a reply from Parcel, a customer-support assistant for Hollow Lane, a UK homeware shop.
Is this a good support conversation? Consider accuracy, helpfulness and policy.
First write your reasoning, then the verdict. Reply with JSON only:
{"reasoning": "...", "verdict": "PASS" or "FAIL"}"""

trials = [json.loads(l) for l in open("evals/runs/trials.jsonl")]
out = Path("judgements.jsonl")
done = {(r["run"], r["case"], r["trial"]) for r in map(json.loads, out.open())} if out.exists() else set()

def one(run, t):
    if run == "broad":
        result = parse(ask_claude(f"{BROAD}\n\n<conversation>\n{render(t)}\n</conversation>"))
    else:
        result = judge(t, with_examples=(run != "narrow-no-examples"))
    return {"run": run, "case": t["case"], "trial": t["trial"], "judge_model": JUDGE_MODEL,
            "judged_at": time.strftime("%Y-%m-%dT%H:%M:%S"), **result}

RUNS = sys.argv[1:] or ["narrow-1", "narrow-2", "narrow-no-examples", "broad"]
jobs = [(run, t) for run in RUNS for t in trials if (run, t["case"], t["trial"]) not in done]
with out.open("a", encoding="utf-8") as f, ThreadPoolExecutor(max_workers=2) as pool:
    for r in pool.map(lambda j: one(*j), jobs):
        if r["verdict"] == "UNPARSEABLE" and "limit" in r["reasoning"].lower():
            print("Usage limit reached; stopping. Rerun later to resume.", flush=True)
            pool.shutdown(wait=False, cancel_futures=True)
            sys.exit(1)
        f.write(json.dumps(r) + "\n"); f.flush()
        print(r["run"], r["case"], r["trial"], r["verdict"], flush=True)
