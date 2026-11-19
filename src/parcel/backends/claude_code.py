"""Claude through your local Claude Code login, using the Claude Agent SDK.
No API key needed. Claude Code's own tools (files, shell, web) are switched off;
the model sees only Parcel's three tools."""

import asyncio
import tempfile

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    create_sdk_mcp_server,
    query,
    tool,
)

from ..tools import TOOLS, run_tool
from ..transcript import ToolCall, TurnResult

SERVER = "parcel"
MAX_TURNS = 10


class ClaudeCodeSession:
    def __init__(self, settings, store, system_prompt):
        self.settings, self.store, self.system = settings, store, system_prompt
        self.session_id: str | None = None
        self._calls: list[ToolCall] = []
        self._workdir = tempfile.mkdtemp(prefix="parcel-")
        self._server = create_sdk_mcp_server(
            name=SERVER, version="0.1.0", tools=[self._wrap(t) for t in TOOLS]
        )

    def _wrap(self, spec: dict):
        name = spec["name"]

        @tool(name, spec["description"], spec["input_schema"])
        async def handler(args):
            output, is_error = run_tool(self.store, name, dict(args))
            self._calls.append(ToolCall(name, dict(args), output, is_error))
            return {"content": [{"type": "text", "text": output}], "is_error": is_error}

        return handler

    def _options(self) -> ClaudeAgentOptions:
        return ClaudeAgentOptions(
            system_prompt=self.system,
            model=self.settings.model,
            effort=self.settings.effort,
            mcp_servers={SERVER: self._server},
            strict_mcp_config=True,  # ignore any MCP servers in your own Claude Code setup
            tools=[],  # no built-in Claude Code tools
            allowed_tools=[f"mcp__{SERVER}__{t['name']}" for t in TOOLS],
            setting_sources=[],  # don't load your CLAUDE.md or settings
            max_turns=MAX_TURNS,
            resume=self.session_id,
            cwd=self._workdir,
        )

    async def _send(self, text: str) -> TurnResult:
        self._calls = []
        result = TurnResult(text="")
        last_text = ""
        async for message in query(prompt=text, options=self._options()):
            if isinstance(message, AssistantMessage):
                texts = [b.text for b in message.content if isinstance(b, TextBlock)]
                if texts:
                    last_text = "".join(texts).strip()
            elif isinstance(message, ResultMessage):
                self.session_id = message.session_id
                usage = message.usage or {}
                result.usage = {
                    k: usage.get(k, 0)
                    for k in (
                        "input_tokens",
                        "output_tokens",
                        "cache_creation_input_tokens",
                        "cache_read_input_tokens",
                    )
                }
                result.cost_usd = message.total_cost_usd
                result.stop_reason = message.subtype
        result.text = last_text
        result.tool_calls = list(self._calls)
        return result

    def send(self, text: str) -> TurnResult:
        return asyncio.run(self._send(text))
