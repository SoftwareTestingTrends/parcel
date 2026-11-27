"""Capstone: the 150 simulated live conversations from "Evals don't stop at release", once each on Claude Haiku 5.5
(Parcel's api backend via OpenRouter, prompt v2). Resumable, 3 at a time.
Run from this folder:  uv run python record_live_haiku.py"""
import json, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "runs/live_haiku.jsonl"


def run_one(cid, week, day, messages):
    sys.path.insert(0, str(HERE.parent / "evals"))
    from openrouter_env import use_openrouter
    use_openrouter()
    from parcel.assistant import Parcel
    from parcel.config import Settings
    parcel = Parcel(Settings.from_env())
    error = None
    try:
        for m in messages:
            parcel.ask(m)
    except Exception as e:
        error = f"{type(e).__name__}: {e}"
    return {"conversation": cid, "week": week, "day": day, "run_error": error,
            "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%S"), **parcel.transcript.to_dict()}


if __name__ == "__main__":
    sys.path.insert(0, str(HERE))
    from live_traffic import CONVERSATIONS
    OUT.parent.mkdir(exist_ok=True)
    done = {json.loads(l)["conversation"] for l in OUT.open() if not json.loads(l)["run_error"]} if OUT.exists() else set()
    todo = [c for c in CONVERSATIONS if c[0] not in done]
    print(len(todo), "to run", flush=True)
    with ProcessPoolExecutor(max_workers=3) as pool, OUT.open("a", encoding="utf-8") as f:
        for fut in as_completed([pool.submit(run_one, *c) for c in todo]):
            r = fut.result()
            f.write(json.dumps(r) + "\n"); f.flush()
            print(r["conversation"], round(r["seconds"], 1), r["run_error"] or "", flush=True)
