import json

from parcel.orders import OrderStore
from parcel.tools import TOOL_NAMES, run_tool


def test_three_tools():
    assert TOOL_NAMES == ("lookup_order", "issue_refund", "hand_off")


def test_errors_come_back_as_results_not_exceptions():
    store = OrderStore.seeded()
    text, is_error = run_tool(store, "lookup_order", {"order_id": "HL-1", "email": "a@b.c"})
    assert is_error and text.startswith("Error:")
    text, is_error = run_tool(store, "lookup_order", {"order_id": "HL-10251"})
    assert is_error and "bad arguments" in text
    text, is_error = run_tool(store, "delete_everything", {})
    assert is_error


def test_success_is_json():
    text, is_error = run_tool(
        OrderStore.seeded(),
        "lookup_order",
        {"order_id": "HL-10251", "email": "dev.patel@example.com"},
    )
    assert not is_error and json.loads(text)["order_id"] == "HL-10251"


def test_claude_backends_default_to_haiku():
    from parcel.config import Settings

    assert Settings(backend="claude-code").model == "claude-haiku-5-5"
    assert Settings(backend="api").model == "claude-haiku-5-5"
    assert Settings(backend="ollama").model == "gemma4:latest"
