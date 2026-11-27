"""Pass/fail criteria written from the failure categories in "Look at the outputs before you measure them".
Each criterion is one yes/no question a code grader can answer from a trace."""
import re

ASKS_AMOUNT = re.compile(
    r"(confirm|let me know|tell me|provide|what(?:'s| is)|could you)[^.?!]{0,80}\b(cost|price|amount|value)\b", re.I)
TOO_SOON = re.compile(r"\b(shortly|right away|straight away|immediately|stay on the line|right now|in a moment)\b", re.I)


def replies(trace):
    return [e["text"] for e in trace["events"] if e["type"] == "parcel"]


def looks_up_and_never_asks_amount(trace):
    """C1. When the customer gives an order number and email and wants a refund, Parcel looks the order up
    and never asks the customer what to refund or what an item cost."""
    looked_up = any(e["type"] == "tool_call" and e["name"] == "lookup_order" for e in trace["events"])
    asked = any(ASKS_AMOUNT.search(r) for r in replies(trace))
    return looked_up and not asked


def hand_off_states_real_time(trace):
    """C2. When Parcel hands off, its reply tells the customer a person will reply by the end of the next
    working day, and doesn't promise anything sooner."""
    if not trace["end_state"]["hand_offs"]:
        return False
    final = replies(trace)[-1]
    return "next working day" in final.lower() and not TOO_SOON.search(final)


def big_refund_handed_off(trace):
    """C3. A refund over £50 is passed to a person as refund_over_limit, and no refund is issued."""
    end = trace["end_state"]
    return any(h["reason"] == "refund_over_limit" for h in end["hand_offs"]) and not end["refunds"]
