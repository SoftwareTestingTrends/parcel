"""Lesson: From failures to pass/fail criteria. Runs the conversations behind two failure categories three
times each on Gemma 4, with Parcel's prompt v1 and with a v2 that adds one clear instruction per gap.
Run from this folder:  uv run python record_runs.py
"""
import json, subprocess, time
from pathlib import Path
from parcel.assistant import Parcel
from parcel.config import Settings
from parcel.prompts import SYSTEM_PROMPT
from conversations import CONVERSATIONS

ASK_AMOUNT = ["c062", "c063", "c066", "c067", "c068", "c069", "c071", "c100"]
HAND_OFF = ["c072", "c073", "c077", "c078", "c079", "c080", "c081", "c082", "c084", "c085"]

REFUND_LINE = "- Returns are refunded when the item reaches the warehouse; don't issue those yourself."
V2_REFUND = REFUND_LINE + ("\n- Before you discuss a refund, look the order up. Work out the amount from the order yourself; "
                           "never ask the customer how much to refund or what an item cost.")
HANDOFF_LINE = "After handing off, tell the customer what happens next."
V2_HANDOFF = ("After handing off, tell the customer what happens next, including when they'll hear back: use the "
              "ticket's reply_by. Don't promise anything sooner.")
assert REFUND_LINE in SYSTEM_PROMPT and HANDOFF_LINE in SYSTEM_PROMPT
PROMPTS = {"v1": SYSTEM_PROMPT, "v2": SYSTEM_PROMPT.replace(REFUND_LINE, V2_REFUND).replace(HANDOFF_LINE, V2_HANDOFF)}
Path("runs/prompt-v2.txt").write_text(PROMPTS["v2"])

messages = dict(CONVERSATIONS)
commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                        capture_output=True, text=True).stdout.strip()
out = Path("runs/trials.jsonl")
done = {(r["prompt"], r["conversation"], r["trial"]) for r in map(json.loads, out.open())} if out.exists() else set()
with out.open("a", encoding="utf-8") as f:
    for trial in (1, 2, 3):
        for version, prompt in PROMPTS.items():
            for cid in ASK_AMOUNT + HAND_OFF:
                if (version, cid, trial) in done:
                    continue
                parcel = Parcel(Settings.from_env(backend="ollama", trace_dir="runs/traces"),
                                system_prompt=prompt, prompt_version=version)
                for m in messages[cid]:
                    parcel.ask(m)
                f.write(json.dumps({"prompt": version, "conversation": cid, "trial": trial, "parcel_commit": commit,
                                    "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%S"), **parcel.transcript.to_dict()}) + "\n")
                f.flush()
                print(version, cid, trial, "|", parcel.transcript.final_reply[:80].replace("\n", " "), flush=True)
