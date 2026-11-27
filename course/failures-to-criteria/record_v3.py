"""Prompt v3: the hand-off instruction states the actual reply time in words, instead of pointing at a field.
Runs the 10 hand-off conversations three times on Gemma 4. Appends to runs/trials.jsonl with prompt "v3"."""
import json, subprocess, time
from pathlib import Path
from parcel.assistant import Parcel
from parcel.config import Settings
from parcel.prompts import SYSTEM_PROMPT
from conversations import CONVERSATIONS
import ast
_src = ast.parse(open("record_runs.py").read())
_consts = {}
for node in _src.body:
    if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) and node.targets[0].id in ("HAND_OFF", "REFUND_LINE", "V2_REFUND", "HANDOFF_LINE"):
        exec(compile(ast.Module([node], []), "record_runs.py", "exec"), _consts)
HAND_OFF, REFUND_LINE, V2_REFUND, HANDOFF_LINE = (_consts[k] for k in ("HAND_OFF", "REFUND_LINE", "V2_REFUND", "HANDOFF_LINE"))

V3_HANDOFF = ("After handing off, tell the customer what happens next: a person from customer care will reply by "
              "the end of the next working day. Don't promise anything sooner, such as \"shortly\" or \"stay on the line\".")
V3 = SYSTEM_PROMPT.replace(REFUND_LINE, V2_REFUND).replace(HANDOFF_LINE, V3_HANDOFF)
Path("runs/prompt-v3.txt").write_text(V3)
messages = dict(CONVERSATIONS)
commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                        capture_output=True, text=True).stdout.strip()
out = Path("runs/trials.jsonl")
done = {(r["prompt"], r["conversation"], r["trial"]) for r in map(json.loads, out.open())}
with out.open("a", encoding="utf-8") as f:
    for trial in (1, 2, 3):
        for cid in HAND_OFF:
            if ("v3", cid, trial) in done:
                continue
            parcel = Parcel(Settings.from_env(backend="ollama", trace_dir="runs/traces"), system_prompt=V3, prompt_version="v3")
            for m in messages[cid]:
                parcel.ask(m)
            f.write(json.dumps({"prompt": "v3", "conversation": cid, "trial": trial, "parcel_commit": commit,
                                "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%S"), **parcel.transcript.to_dict()}) + "\n")
            f.flush()
            print("v3", cid, trial, "|", parcel.transcript.final_reply[:80].replace("\n", " "), flush=True)
