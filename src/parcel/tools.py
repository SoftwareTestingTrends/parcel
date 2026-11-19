"""The tools Parcel can call, described once and shared by every backend."""

import json

from .orders import REFUND_REASONS, OrderStore, ToolError
from .policy import HAND_OFF_REASONS

TOOLS = [
    {
        "name": "lookup_order",
        "description": (
            "Look up one of the customer's orders. Needs the order number (like HL-10231) "
            "and the email address on the order. Returns status, dates, items and totals."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "Order number, e.g. HL-10231"},
                "email": {"type": "string", "description": "Email address on the order"},
            },
            "required": ["order_id", "email"],
            "additionalProperties": False,
        },
    },
    {
        "name": "issue_refund",
        "description": (
            "Refund money on an order that is damaged, faulty or lost in transit. "
            "Up to £50 per order; larger refunds must be handed off. Not for returns: "
            "those are refunded when the item reaches the warehouse."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "email": {"type": "string"},
                "amount_gbp": {"type": "number", "description": "Amount in pounds"},
                "reason": {"type": "string", "enum": list(REFUND_REASONS)},
            },
            "required": ["order_id", "email", "amount_gbp", "reason"],
            "additionalProperties": False,
        },
    },
    {
        "name": "hand_off",
        "description": (
            "Pass the conversation to a person in the customer care team. "
            "Use it whenever the hand-off rules apply."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "reason": {"type": "string", "enum": list(HAND_OFF_REASONS)},
                "summary": {
                    "type": "string",
                    "description": "One or two sentences for the person taking over",
                },
            },
            "required": ["reason", "summary"],
            "additionalProperties": False,
        },
    },
]

TOOL_NAMES = tuple(t["name"] for t in TOOLS)


def run_tool(store: OrderStore, name: str, args: dict) -> tuple[str, bool]:
    """Run one tool call. Returns (result text, is_error)."""
    try:
        if name == "lookup_order":
            result = store.lookup_order(args["order_id"], args["email"])
        elif name == "issue_refund":
            result = store.issue_refund(
                args["order_id"], args["email"], args["amount_gbp"], args["reason"]
            )
        elif name == "hand_off":
            result = store.hand_off(args["reason"], args["summary"])
        else:
            raise ToolError(f"Unknown tool {name!r}.")
    except ToolError as err:
        return f"Error: {err}", True
    except (KeyError, TypeError, ValueError) as err:
        return f"Error: bad arguments for {name}: {err}", True
    return json.dumps(result), False
