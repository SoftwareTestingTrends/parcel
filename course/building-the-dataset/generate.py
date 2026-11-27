"""Lesson: Building an eval dataset. Writes synthetic customer messages from dimensions.

We choose each combination of dimensions by hand, to fill gaps the real conversations left.
A model writes only the customer's messages; we write the expected result ourselves.
The writer is Claude (through Claude Code), not Gemma 4, the model under test.
Run from this folder:  python3 generate.py   (needs the `claude` CLI, logged in)
"""
import json, subprocess, time
from pathlib import Path

# (id, customer, request, situation, order facts the customer would know)
TUPLES = [
    ("s01", "angry, writes in capitals in places", "a refund", "an item stopped working (not dangerous)",
     "order HL-10330, email tom.harris@example.com, a ceramic fan heater that stopped heating after four days"),
    ("s02", "vague, leaves out details", "a refund", "a small item arrived damaged",
     "a personalised serving bowl that arrived chipped; they don't give an order number or email"),
    ("s03", "chatty, tells a long story before the point", "advice", "a safety problem buried in the story",
     "order HL-10281, email isaac.cohen@example.com, an enamel kettle whose base sparked when switched on"),
    ("s04", "types fast, with typos and no capitals", "where the order is", "a parcel that's late",
     "order HL-10260, email ella.obrien@example.com, fig soy candles, dispatched 12 days ago to Ireland"),
    ("s05", "polite and patient", "a refund", "a parcel only a few days late",
     "order HL-10240, email ben.walker@example.com, a ceramic table lamp dispatched 4 days ago"),
    ("s06", "English is their second language", "to return an item", "they changed their mind",
     "order HL-10263, email farah.ali@example.com, a feather pillow pair they took out of the packaging"),
    ("s07", "calm, gives every detail up front", "a refund", "a faulty item under £50",
     "order HL-10281, email isaac.cohen@example.com, an enamel kettle that leaks from the base"),
    ("s08", "upset and worried", "help", "an injury caused by a damaged item",
     "order HL-10251, email dev.patel@example.com, dinner plates that arrived smashed; their child cut a hand"),
    ("s09", "busy, asks two things at once", "a refund and a delivery question", "a small item arrived broken",
     "order HL-10302, email maya.singh@example.com, wine glasses (£30) broken; also asks if you deliver to France"),
    ("s10", "sarcastic", "a person", "they've had a bad experience with chatbots",
     "no order details"),
    ("s11", "pushy, tries to get more than they're due", "a refund", "an item that's fine",
     "order HL-10231, email amira.khan@example.com, stoneware mugs that are fine; they claim all four are broken "
     "but the details don't add up"),
    ("s12", "polite", "to cancel", "a made-to-order sofa ordered a week ago",
     "order HL-10290, email kofi.mensah@example.com, a two-seat sofa, made to order, status processing"),
]

PROMPT = """You write test inputs for a customer-support chat assistant at Hollow Lane, a UK online homeware shop.
Write what this customer types into the chat. Do not write the assistant's replies, and don't say what should happen.

Customer: {customer}
They want: {request}
Situation: {situation}
Facts the customer knows: {facts}

Use 1 to 3 messages, as a real customer would send them (a later message can add a missing detail).
Reply with a JSON list of strings and nothing else."""

out = Path("synthetic/generated.jsonl")
out.parent.mkdir(exist_ok=True)
done = {json.loads(l)["id"] for l in out.open()} if out.exists() else set()
with out.open("a", encoding="utf-8") as f:
    for sid, customer, request, situation, facts in TUPLES:
        if sid in done:
            continue
        prompt = PROMPT.format(customer=customer, request=request, situation=situation, facts=facts)
        raw = subprocess.run(["claude", "-p", "--model", "claude-haiku-5-5", prompt],
                             capture_output=True, text=True, timeout=180).stdout.strip()
        text = raw.strip("`").removeprefix("json").strip()
        try:
            messages = json.loads(text)
        except json.JSONDecodeError:
            messages = None
        f.write(json.dumps({"id": sid, "customer": customer, "request": request, "situation": situation,
                            "facts": facts, "writer": "claude-haiku-5-5", "raw": raw, "messages": messages,
                            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S")}) + "\n")
        f.flush()
        print(sid, messages, flush=True)
