"""Backend glue code, tested offline by replaying what a model sent."""

from parcel.backends.ollama import OllamaSession
from parcel.config import Settings
from parcel.orders import OrderStore


def test_reply_written_alongside_a_tool_call_is_kept():
    # Gemma 4 writes the customer's reply in the same message as the hand_off call,
    # then sends an empty final message once the tool has run.
    responses = iter(
        [
            {
                "message": {
                    "role": "assistant",
                    "content": "I'm so sorry. I'm passing you to a person who can help.",
                    "tool_calls": [
                        {
                            "function": {
                                "name": "hand_off",
                                "arguments": {"reason": "safety_or_legal", "summary": "Burn."},
                            }
                        }
                    ],
                },
                "done_reason": "stop",
            },
            {"message": {"role": "assistant", "content": ""}, "done_reason": "stop"},
        ]
    )
    store = OrderStore.seeded()
    session = OllamaSession(Settings(backend="ollama"), store, "system prompt")
    session._chat = lambda: next(responses)

    result = session.send("The lamp sparked and burnt my hand.")

    assert result.text == "I'm so sorry. I'm passing you to a person who can help."
    assert [h["reason"] for h in store.hand_offs] == ["safety_or_legal"]


def test_claude_code_sessions_ignore_your_own_claude_code_setup():
    # Found while comparing models for the course: lazily loaded tools hid Parcel's tools from the
    # model, and plugins from the developer's own setup blocked Parcel's tool calls.
    from parcel.backends.claude_code import ClaudeCodeSession

    session = ClaudeCodeSession(
        Settings(backend="claude-code"), OrderStore.seeded(), "system prompt"
    )
    options = session._options()

    assert options.env["ENABLE_TOOL_SEARCH"] == "false"
    assert options.env["CLAUDE_CODE_PLUGIN_DIRS"] == ""
    assert options.setting_sources == []
    assert options.tools == []
    assert sorted(options.allowed_tools) == [
        "mcp__parcel__hand_off",
        "mcp__parcel__issue_refund",
        "mcp__parcel__lookup_order",
    ]
