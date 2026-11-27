"""Parcel's suite in DeepEval: turn a Parcel transcript into a DeepEval test case, wrap the code
graders as custom metrics, and use Claude (through the Claude Code CLI) as the judge model."""
import json
import subprocess

from deepeval.metrics import BaseMetric
from deepeval.models import DeepEvalBaseLLM
from deepeval.test_case import LLMTestCase, ToolCall

from parcel.knowledge import default_help_centre


def to_test_case(t):
    """One Parcel conversation as one DeepEval test case. The whole transcript rides along in
    metadata, so our code graders can still read every event."""
    hc = default_help_centre()
    customer = [e["text"] for e in t["events"] if e["type"] == "customer"]
    replies = [e["text"] for e in t["events"] if e["type"] == "parcel"]
    tools = [ToolCall(name=e["name"], input_parameters=e["args"], output=e["result"])
             for e in t["events"] if e["type"] == "tool_call"]
    articles = [hc.get(a["id"]).text for e in t["events"] if e["type"] == "retrieval" for a in e["articles"]]
    return LLMTestCase(input="\n".join(customer), actual_output="\n".join(replies),
                       tools_called=tools, retrieval_context=articles or None,
                       name=t.get("conversation") or f"{t['case']} t{t['trial']}",
                       metadata={"transcript": t})


class CodeGraderMetric(BaseMetric):
    """Any grader from graders.py (transcript -> list of problems) as a DeepEval metric.
    No model calls: same transcript, same answer."""

    def __init__(self, grader, *args):
        self.grader, self.args, self.threshold = grader, args, 1.0

    def measure(self, test_case, *_, **__):
        problems = self.grader(test_case.metadata["transcript"], *self.args)
        self.score = 0.0 if problems else 1.0
        self.reason = "; ".join(problems) or "no problems"
        self.success = not problems
        return self.score

    async def a_measure(self, test_case, *_, **__):
        return self.measure(test_case)

    def is_successful(self):
        return bool(self.success)

    @property
    def __name__(self):
        return self.grader.__name__


# The same bare `claude -p` call as the judge in "When a model does the grading": no Claude Code
# tools, MCP servers or saved session, so each call sends little more than the prompt.
CLAUDE_FLAGS = ["--system-prompt", "You grade customer-support conversations. Follow the instructions exactly.",
                "--tools", "", "--strict-mcp-config", "--disable-slash-commands", "--no-session-persistence"]


class ClaudeJudge(DeepEvalBaseLLM):
    """Claude Sonnet 5.5 as DeepEval's judge model, through `claude -p` (your Claude Code login)."""

    def __init__(self, model="claude-sonnet-5-5"):
        self.model_name = model
        self.calls = 0

    def load_model(self):
        return self

    def get_model_name(self):
        return self.model_name

    def generate(self, prompt, schema=None):
        if schema is not None:
            prompt += ("\n\nReply with JSON only, with exactly these keys: "
                       + ", ".join(schema.model_fields) + ".")
        self.calls += 1
        out = subprocess.run(["claude", "-p", "--model", self.model_name, *CLAUDE_FLAGS], input=prompt,
                             capture_output=True, text=True, timeout=300).stdout.strip()
        if schema is None:
            return out
        text = out.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return schema(**json.loads(text[text.index("{"): text.rindex("}") + 1]))

    async def a_generate(self, prompt, schema=None):
        return self.generate(prompt, schema)
