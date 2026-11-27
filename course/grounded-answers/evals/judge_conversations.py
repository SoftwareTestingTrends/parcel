"""Run the groundedness judge once over a run file; saves one verdict per conversation and skips
conversations already judged, so a stopped run picks up where it left off.
  uv run python evals/judge_conversations.py runs/gemma4-prompt-v2.jsonl runs/grounded_judgements.jsonl"""
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from grounded_judge import JUDGE_MODEL, judge

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
traces = [json.loads(l) for l in src.open()]
done = {json.loads(l)["conversation"] for l in dst.open()} if dst.exists() else set()
todo = [t for t in traces if t["conversation"] not in done]
print(f"{len(todo)} to judge ({len(done)} already done)")


def one(t):
    return {"conversation": t["conversation"], "model": JUDGE_MODEL, **judge(t)}


with ThreadPoolExecutor(max_workers=2) as pool, dst.open("a") as out:
    for i, row in enumerate(pool.map(one, todo), 1):
        out.write(json.dumps(row) + "\n")
        out.flush()
        print(f"{i}/{len(todo)} {row['conversation']} {row['verdict']}", flush=True)
