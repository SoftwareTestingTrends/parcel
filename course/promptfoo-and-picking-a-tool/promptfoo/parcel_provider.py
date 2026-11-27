"""Parcel as a promptfoo provider. For each test, a fresh Parcel gets the test's customer messages.
The output is the whole conversation as text (customer, tool calls, replies), because llm-rubric
only sees the output; the full transcript goes in metadata for the code graders."""
import json

from parcel.assistant import Parcel
from parcel.config import Settings


def render(t):
    lines = []
    for e in t["events"]:
        if e["type"] == "customer":
            lines.append(f"Customer: {e['text']}")
        elif e["type"] == "tool_call":
            args = ", ".join(f"{k}={v!r}" for k, v in e["args"].items())
            lines.append(f"[tool call] {e['name']}({args}) -> {e['result'][:600]}")
        elif e["type"] == "parcel":
            lines.append(f"Parcel: {e['text']}")
    return "\n".join(lines)


def call_api(prompt, options, context):
    parcel = Parcel(Settings.from_env())
    for message in json.loads(context["vars"]["messages"]):
        parcel.ask(message)
    transcript = parcel.transcript.to_dict()
    return {"output": render(transcript), "metadata": {"transcript": transcript}}
