"""Capstone: run all 39 cases × 3 trials on Claude Haiku 5.5 through Parcel's api backend, sent via OpenRouter
(see openrouter_env.py). Replaces the claude-code run, where Claude Code added the account email to every
conversation. Three conversations at a time, resumable.
Run from this lesson's folder:  uv run python evals/run_haiku_api.py"""
import json, os, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "runs/haiku_api_t1-3.jsonl"


def clean_env():
    """Parcel's Claude sessions must not inherit the Claude Code session this script is launched from.
    Found 2026-11-26: Claude Code loaded Parcel's three tools lazily (behind a tool search Parcel switches off),
    and the launching session's plugins (via CLAUDE_CODE_PLUGIN_DIRS) blocked Parcel's tool calls with their hooks.
    Either way Haiku never reached the order system and wrote replies about errors instead."""
    for k in [k for k in os.environ if k.startswith("CLAUDE")]:
        del os.environ[k]
    os.environ["CLAUDE_CODE_PLUGIN_DIRS"] = ""
    os.environ["ENABLE_TOOL_SEARCH"] = "false"


def run_one(case, trial):
    import sys
    sys.path.insert(0, str(HERE))
    from openrouter_env import use_openrouter
    use_openrouter()
    from parcel.assistant import Parcel
    from parcel.config import Settings
    parcel = Parcel(Settings.from_env())
    error = None
    try:
        for message in case["messages"]:
            parcel.ask(message)
    except Exception as e:  # keep going; record the failure so it's visible
        error = f"{type(e).__name__}: {e}"
    return {"case": case["id"], "trial": trial, "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "run_error": error, **parcel.transcript.to_dict()}


if __name__ == "__main__":
    cases = json.loads((HERE / "cases.json").read_text())
    done = set()
    if OUT.exists():
        done = {(r["case"], r["trial"]) for r in map(json.loads, OUT.open()) if not r.get("run_error")}
    todo = [(c, t) for t in (1, 2, 3) for c in cases if (c["id"], t) not in done]
    print(len(todo), "to run", flush=True)
    with ProcessPoolExecutor(max_workers=3) as pool, OUT.open("a", encoding="utf-8") as f:
        futures = [pool.submit(run_one, c, t) for c, t in todo]
        for fut in as_completed(futures):
            r = fut.result()
            f.write(json.dumps(r) + "\n"); f.flush()
            print(r["case"], r["trial"], round(r["seconds"], 1), "s", r["run_error"] or "",
                  "|", (r["events"][-1].get("text", "") if r["events"] else "")[:80].replace("\n", " "), flush=True)
