"""A local model through Ollama (https://ollama.com). Free to run, and the only
backend where you can set temperature and a seed."""

import json
import urllib.error
import urllib.request

from ..tools import TOOLS, run_tool
from ..transcript import ToolCall, TurnResult

MAX_TOOL_ROUNDS = 8

OLLAMA_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": t["name"],
            "description": t["description"],
            "parameters": t["input_schema"],
        },
    }
    for t in TOOLS
]


class OllamaSession:
    def __init__(self, settings, store, system_prompt):
        self.settings, self.store = settings, store
        self.messages = [{"role": "system", "content": system_prompt}]

    def _chat(self) -> dict:
        body = {
            "model": self.settings.model,
            "messages": self.messages,
            "tools": OLLAMA_TOOLS,
            "stream": False,
        }
        options = {}
        if self.settings.temperature is not None:
            options["temperature"] = self.settings.temperature
        if self.settings.seed is not None:
            options["seed"] = self.settings.seed
        if options:
            body["options"] = options
        request = urllib.request.Request(
            self.settings.ollama_host.rstrip("/") + "/api/chat",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=300) as response:
                return json.loads(response.read())
        except urllib.error.URLError as err:
            raise RuntimeError(
                f"Can't reach Ollama at {self.settings.ollama_host}. Is `ollama serve` running "
                f"and is {self.settings.model} pulled? ({err})"
            ) from err

    def send(self, text: str) -> TurnResult:
        self.messages.append({"role": "user", "content": text})
        result = TurnResult(text="")
        said = ""
        for _ in range(MAX_TOOL_ROUNDS):
            data = self._chat()
            message = data["message"]
            result.usage["input_tokens"] = result.usage.get("input_tokens", 0) + data.get(
                "prompt_eval_count", 0
            )
            result.usage["output_tokens"] = result.usage.get("output_tokens", 0) + data.get(
                "eval_count", 0
            )
            self.messages.append(
                {k: message[k] for k in ("role", "content", "tool_calls") if k in message}
            )
            text = message.get("content", "").strip()
            if text:
                # Models often write the customer's reply alongside a tool call and then send
                # an empty final message, so keep the last thing the model actually said.
                said = text
            calls = message.get("tool_calls") or []
            if not calls:
                result.text = said
                result.stop_reason = data.get("done_reason", "stop")
                return result
            for call in calls:
                name = call["function"]["name"]
                args = call["function"].get("arguments") or {}
                output, is_error = run_tool(self.store, name, args)
                result.tool_calls.append(ToolCall(name, args, output, is_error))
                self.messages.append({"role": "tool", "tool_name": name, "content": output})
        result.text = "Sorry, I got stuck. Let me pass you to a person."
        result.stop_reason = "max_tool_rounds"
        return result
