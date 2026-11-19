"""Claude through the Anthropic API. Needs ANTHROPIC_API_KEY (or an `ant auth login`
profile). Uses a plain tool-use loop so every step can be recorded in the transcript."""

import anthropic

from ..pricing import estimate_cost
from ..tools import TOOLS, run_tool
from ..transcript import ToolCall, TurnResult

MAX_TOOL_ROUNDS = 8


class ApiSession:
    def __init__(self, settings, store, system_prompt):
        self.settings, self.store, self.system = settings, store, system_prompt
        self.client = anthropic.Anthropic()
        self.messages: list[dict] = []

    def _create(self):
        kwargs = dict(
            model=self.settings.model,
            max_tokens=16000,
            system=self.system,
            tools=TOOLS,
            messages=self.messages,
        )
        if self.settings.effort:
            kwargs["output_config"] = {"effort": self.settings.effort}
        return self.client.messages.create(**kwargs)

    def send(self, text: str) -> TurnResult:
        self.messages.append({"role": "user", "content": text})
        result = TurnResult(text="")
        for _ in range(MAX_TOOL_ROUNDS):
            response = self._create()
            usage = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "cache_creation_input_tokens": response.usage.cache_creation_input_tokens or 0,
                "cache_read_input_tokens": response.usage.cache_read_input_tokens or 0,
            }
            for key, value in usage.items():
                result.usage[key] = result.usage.get(key, 0) + value
            # Keep the whole content (thinking blocks included) so the next request is valid.
            self.messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "refusal":
                result.text = "Sorry, I can't help with that here. Let me pass you to a person."
                result.stop_reason = "refusal"
                break
            tool_uses = [b for b in response.content if b.type == "tool_use"]
            if response.stop_reason != "tool_use" or not tool_uses:
                result.text = "".join(b.text for b in response.content if b.type == "text").strip()
                result.stop_reason = response.stop_reason
                break
            results = []
            for block in tool_uses:
                output, is_error = run_tool(self.store, block.name, dict(block.input))
                result.tool_calls.append(ToolCall(block.name, dict(block.input), output, is_error))
                results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": output,
                        "is_error": is_error,
                    }
                )
            self.messages.append({"role": "user", "content": results})
        else:
            result.text = "Sorry, I got stuck. Let me pass you to a person."
            result.stop_reason = "max_tool_rounds"
        result.cost_usd = estimate_cost(self.settings.model, result.usage)
        return result
