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
