"""A groundedness judge: is every fact in Parcel's replies supported by something Parcel was given?
The judge is Claude, through the Claude Code CLI (`claude -p`); Parcel under test is Gemma 4.
  from grounded_judge import judge
  result = judge(transcript)   # {"claims": [...], "reasoning": "...", "verdict": "PASS" | "FAIL"}
"""
import json
import subprocess
from pathlib import Path

from parcel.knowledge import default_help_centre

JUDGE_MODEL = "claude-sonnet-5-5"
HERE = Path(__file__).parent

RUBRIC = """You are checking one thing about a customer-support conversation: whether every fact the
assistant, Parcel, states is supported by something Parcel was given.

Parcel may only state facts that come from:
- the help-centre articles shown before that reply (articles stay available for the rest of the
  conversation once they've been shown);
- the result of a tool call made before that reply (the order record from lookup_order, a refund
  from issue_refund, a ticket from hand_off);
- Parcel's own rules: it can refund damaged, faulty or lost orders up to £50 per order; larger
  refunds, safety problems, legal complaints and requests for a person go to a person, who replies
  by the end of the next working day;
- what the customer said.

FAIL if any reply states a fact, a number, a date or an action that none of these supports, or that
contradicts them. That includes facts that may well be true but that Parcel wasn't given, a refund
or hand-off that no tool call shows, and an amount or date that differs from the order record.

These are supported, so they PASS: a direct consequence of a source (if an article lists the only
countries Parcel delivers to, "we don't deliver to Italy" is supported); saying it doesn't know;
offering to pass the customer to a person; asking for details; apologies and greetings.

Judge only this. Ignore whether Parcel should have done something else, tone, length, and which
article is cited: a reply can be unhelpful and still PASS here.

First list every factual claim in Parcel's replies, each with the source that supports it or
"none". Then give the verdict. Reply with JSON only:
{"claims": [{"claim": "...", "source": "..."}], "reasoning": "...", "verdict": "PASS" or "FAIL"}"""


def render(t):
    """The conversation as the judge sees it: each message, the articles Parcel was given for it,
    every tool call with its result, and every reply."""
    hc = default_help_centre()
    lines = []
    for e in t["events"]:
        if e["type"] == "customer":
            lines.append(f"Customer: {e['text']}")
        elif e["type"] == "retrieval":
            if e["articles"]:
                for a in e["articles"]:
                    lines.append(f'[article given to Parcel] <article id="{a["id"]}">\n{hc.get(a["id"]).text.strip()}\n</article>')
            else:
                lines.append("[no articles given for this message]")
        elif e["type"] == "tool_call":
            args = ", ".join(f"{k}={v!r}" for k, v in e["args"].items())
            outcome = "ERROR " + e["result"] if e["is_error"] else e["result"]
            lines.append(f"[tool call] {e['name']}({args}) -> {outcome[:1500]}")
        elif e["type"] == "parcel":
            lines.append(f"Parcel: {e['text']}")
    return "\n".join(lines)


# Graded examples, from the repeated-trials run (not from the 100 conversations this judge grades).
EXAMPLES = [
    ("final-sale-cushion-stained t1", "FAIL",
     "The order record shows the cushion at £15.00. Parcel refunded and quoted £7.50, an amount no source gives."),
    ("two-questions-glasses-refund t1", "FAIL",
     "Parcel says it is \"issuing that refund now\", but issue_refund was never called, and it says the money "
     "arrives in 5-10 working days, which no article or tool result it was given says."),
    ("mug-chipped-refund t1", "PASS",
     "£12.00 matches the issue_refund result, and \"5 to 10 working days\" is in that result and in KB-105."),
    ("cancel-processing-order t1", "PASS",
     "The order record shows Processing; KB-107 says Processing orders can be cancelled from My orders and are "
     "refunded in full, including delivery."),
]


def examples_text():
    raw = json.loads((HERE / "judge_examples_raw.json").read_text())
    return "\n\n".join(
        f"<example>\n{render(raw[key])}\n\nAnswer: {json.dumps({'reasoning': why, 'verdict': verdict})}\n</example>"
        for key, verdict, why in EXAMPLES)


def prompt_for(t):
    return (f"{RUBRIC}\n\nHere are graded examples:\n\n{examples_text()}\n\n"
            f"Now grade this conversation:\n\n<conversation>\n{render(t)}\n</conversation>")


# A bare grading call: no Claude Code instructions, tools, MCP servers, skills or saved session.
CLAUDE_FLAGS = ["--system-prompt", "You grade customer-support conversations. Follow the instructions exactly.",
                "--tools", "", "--strict-mcp-config", "--disable-slash-commands", "--no-session-persistence"]


def ask_claude(prompt, model=JUDGE_MODEL):
    out = subprocess.run(["claude", "-p", "--model", model, *CLAUDE_FLAGS], input=prompt,
                         capture_output=True, text=True, timeout=300)
    return out.stdout.strip()


def parse(raw):
    text = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        return json.loads(text[text.index("{"): text.rindex("}") + 1])
    except ValueError:
        return {"reasoning": raw, "verdict": "UNPARSEABLE"}


def judge(t):
    return parse(ask_claude(prompt_for(t)))
