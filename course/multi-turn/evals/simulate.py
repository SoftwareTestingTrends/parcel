"""Replay a scenario with a simulated customer instead of fixed messages.
The customer is Gemma 4 too, running locally through Ollama, with its own prompt. It writes one
message at a time, reacting to what Parcel just said, and says DONE when it's finished.
  PARCEL_BACKEND=ollama uv run python evals/simulate.py 3      # 3 trials of every scenario
"""
import json
import sys
import time
from pathlib import Path

import urllib.request

from parcel.assistant import Parcel
from parcel.config import Settings
from scenarios import SCENARIOS

HERE = Path(__file__).parent
MAX_CUSTOMER_TURNS = 6

CUSTOMER_PROMPT = """You are role-playing a customer writing to Parcel, the support assistant for
Hollow Lane, a UK homeware shop. Stay in character.

{persona}

What you want: {goal}.

Write only your next message to Parcel, as the customer would type it: one to three sentences.
Answer what Parcel asks. Don't invent order details beyond the ones above. If Parcel asks for
something you don't have, say so.
When you've got what you wanted, or Parcel has clearly told you what happens next, or you've been
passed to a person, reply with exactly: DONE"""


def customer_says(scenario, conversation):
    """The simulated customer's next message, given the conversation so far (from its side)."""
    messages = [{"role": "system", "content": CUSTOMER_PROMPT.format(**scenario)}]
    for speaker, text in conversation:   # the customer is the "assistant" in its own chat
        messages.append({"role": "assistant" if speaker == "customer" else "user", "content": text})
    body = json.dumps({"model": "gemma4:latest", "messages": messages, "stream": False}).encode()
    request = urllib.request.Request("http://localhost:11434/api/chat", data=body,
                                     headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=300) as response:
        return json.loads(response.read())["message"]["content"].strip()


def simulate(name):
    scenario = SCENARIOS[name]
    parcel = Parcel(Settings.from_env())
    conversation = []
    message = scenario["opening"]
    for _ in range(MAX_CUSTOMER_TURNS):
        conversation.append(("customer", message))
        conversation.append(("parcel", parcel.ask(message)))
        message = customer_says(scenario, conversation)
        if message.strip().rstrip(".").upper() == "DONE":
            break
    else:
        message = "(stopped: turn limit)"
    return {"case": name, "simulated": True, "ended_with": message, **parcel.transcript.to_dict()}


if __name__ == "__main__":
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    out = HERE / "runs/simulated.jsonl"
    with out.open("a", encoding="utf-8") as f:
        for trial in range(1, trials + 1):
            for name in SCENARIOS:
                record = {"trial": trial, "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%S"), **simulate(name)}
                f.write(json.dumps(record) + "\n")
                f.flush()
                print(name, trial, record["ended_with"][:40], flush=True)
