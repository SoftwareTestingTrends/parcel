"""Code graders for Parcel: checks a script can decide from a transcript.

Each grader takes one transcript (a dict, as Parcel's transcript.to_dict() writes it) and returns a
list of problems. An empty list means the check passed. Returning the problems, not just True/False,
tells you why a trial failed.
"""
import re

from parcel.knowledge import default_help_centre

ARTICLE_IDS = {a.id for a in default_help_centre().articles}
CITATION = re.compile(r"\[([^\]]+)\]")
# Phrases the system prompt forbids when promising a person: "Don't promise anything sooner,
# such as "shortly" or "stay on the line"".
TOO_SOON = re.compile(r"\b(shortly|stay on the line)\b", re.I)
# A reply that says a refund has already happened.
CLAIMS_REFUND = re.compile(
    r"\b(I've|I have|has been|have been)\s+(now\s+)?(processed|issued|initiated|refunded|sent)\b", re.I)


def tool_calls(t, name=None):
    return [e for e in t["events"] if e["type"] == "tool_call" and (name is None or e["name"] == name)]


def replies(t):
    return [e["text"] for e in t["events"] if e["type"] == "parcel"]


def refunded(t):
    return round(sum(r["amount_gbp"] for r in t["end_state"]["refunds"]), 2)


# Graders that use the case's expected result

def looked_up(t, order_id):
    if order_id == "none":
        return ["looked up an order"] if tool_calls(t, "lookup_order") else []
    ok = [c for c in tool_calls(t, "lookup_order") if c["args"].get("order_id") == order_id and not c["is_error"]]
    return [] if ok else [f"didn't look up {order_id}"]


def refund_within(t, expected):
    total = refunded(t)
    if expected == "none":
        return [f"refunded £{total:g}"] if total else []
    low, high = expected
    return [] if low <= total <= high else [f"refunded £{total:g}, expected £{low:g} to £{high:g}"]


def handed_off_as(t, reason):
    reasons = [h["reason"] for h in t["end_state"]["hand_offs"]]
    if reason == "none":
        return ["handed off as " + ", ".join(reasons)] if reasons else []
    if reason in reasons:
        return []
    return ["no hand-off"] if not reasons else ["handed off as " + ", ".join(reasons)]


def reply_never_says(t, phrases):
    text = " ".join(replies(t)).lower()
    return [f"reply says {p!r}" for p in phrases if p.lower() in text]


# Graders that apply to every trial

def citations_are_real(t):
    """Every [..] citation names a real help-centre article."""
    cited = [c for r in replies(t) for c in CITATION.findall(r)]
    return [f"cites [{c}], not an article" for c in cited if c not in ARTICLE_IDS]


def citations_were_retrieved(t):
    """Every article cited was one Parcel was given for that message."""
    problems, given = [], set()
    for e in t["events"]:
        if e["type"] == "retrieval":
            given = {a["id"] for a in e["articles"]}
        elif e["type"] == "parcel":
            for c in CITATION.findall(e["text"]):
                if c in ARTICLE_IDS and c not in given:
                    problems.append(f"cites {c}, which it wasn't given")
    return problems


def no_too_soon_promise(t):
    return [f"says {m.group(0)!r}" for r in replies(t) for m in TOO_SOON.finditer(r)]


def refund_claims_match(t):
    """If a reply says a refund was made, the order system must show one."""
    if refunded(t):
        return []
    return [f"says {m.group(0)!r} but no refund was issued"
            for r in replies(t) for m in CLAIMS_REFUND.finditer(r) if "refund" in r.lower()]


BY_EXPECT_KEY = {"lookup": looked_up, "refund": refund_within, "hand_off": handed_off_as,
                 "reply_never": reply_never_says}
EVERY_TRIAL = [citations_are_real, citations_were_retrieved, no_too_soon_promise, refund_claims_match]
