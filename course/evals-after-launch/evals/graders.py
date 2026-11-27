"""Code graders for Parcel: checks a script can decide from a transcript.

Each grader takes one transcript (a dict, as Parcel's transcript.to_dict() writes it) and returns a
list of problems. An empty list means the check passed. Returning the problems, not just True/False,
tells you why a trial failed.
"""
import json
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


# Fixed 2026-11-23: "I have initiated a hand-off" was read as a refund claim (angry heater, trial 5).
HAND_OFF_AFTER = re.compile(r"\s+(a\s+|the\s+)?hand[- ]?off", re.I)
# Fixed 2026-11-25: "confirmation once the refund has been issued" was read as a claim (a condition, not a claim).
CONDITIONAL_BEFORE = re.compile(r"\b(once|when|after|until)\s+(the\s+|your\s+|a\s+)?(refund|it|this)\s*$", re.I)


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
    """Every article cited was one Parcel had been given in this conversation so far.
    (Earlier messages, with their articles, stay in the conversation.)"""
    problems, given = [], set()
    for e in t["events"]:
        if e["type"] == "retrieval":
            given |= {a["id"] for a in e["articles"]}
        elif e["type"] == "parcel":
            for c in CITATION.findall(e["text"]):
                if c in ARTICLE_IDS and c not in given:
                    problems.append(f"cites {c}, which it wasn't given")
    return problems


def no_too_soon_promise(t):
    return [f"says {m.group(0)!r}" for r in replies(t) for m in TOO_SOON.finditer(r)]


def hand_off_states_reply_time(t):
    """After a hand-off, a reply tells the customer when a person will reply."""
    after, texts = False, []
    for e in t["events"]:
        if e["type"] == "tool_call" and e["name"] == "hand_off":
            after = True
        if after and e["type"] == "parcel":
            texts.append(e["text"])
    if not after or any("next working day" in x.lower() for x in texts):
        return []
    return ["handed off, but no reply says when a person will reply"]


def refunded_before(t):
    """Refunds the order system already showed when Parcel looked the order up."""
    results = [json.loads(c["result"]) for c in tool_calls(t, "lookup_order") if not c["is_error"]]
    return sum(r.get("already_refunded", 0) for r in results)


def refund_claims_match(t):
    """If a reply says a refund was made, the order system must show one, made in this
    conversation or before it."""
    if refunded(t) or refunded_before(t):
        return []
    return [f"says {m.group(0)!r} but no refund was issued"
            for r in replies(t) for m in CLAIMS_REFUND.finditer(r) if "refund" in r.lower()
            and not HAND_OFF_AFTER.match(r, m.end())     # "I have initiated a hand-off" isn't a refund
            and not CONDITIONAL_BEFORE.search(r[:m.start()])]   # "once the refund has been issued" isn't one either


BY_EXPECT_KEY = {"lookup": looked_up, "refund": refund_within, "hand_off": handed_off_as,
                 "reply_never": reply_never_says}
EVERY_TRIAL = [citations_are_real, citations_were_retrieved, no_too_soon_promise, hand_off_states_reply_time,
               refund_claims_match]


# Added 2026-11-25 from a live incident ("Evals don't stop at release"): Parcel told customers a person
# would reply, but never called hand_off, so no ticket existed and nobody would reply (w151, w165, w174).
PROMISES_A_PERSON = re.compile(
    r"\b(they|a person|someone|a member of[\w ]*team|our[\w ]*team|customer care)\b[^.]{0,40}?"
    r"\bwill (reply|be in touch|get back|contact)", re.I)


# Fixed 2026-11-26 (capstone, Haiku): "I can pass your request to a member of our customer care team, who will
# reply by the end of the next working day. If you'd like that, let me know." is an offer, not a promise.
OFFER = re.compile(r"\b(I can|I could|I'd be happy to|I would be happy to|happy to) (pass|put|hand|connect)", re.I)


def promised_reply_has_ticket(t):
    """A reply that tells the customer a person will reply needs a hand-off behind it.
    Sentences that explain the policy ("If the team is closed, they'll reply...") don't count."""
    if tool_calls(t, "hand_off"):
        return []
    problems = []
    for r in replies(t):
        for sentence in re.split(r"(?<=[.!?])\s+", r):
            if PROMISES_A_PERSON.search(sentence) and not re.match(r"\s*if\b", sentence, re.I) \
                    and "you can ask" not in sentence.lower() and not OFFER.search(sentence):
                problems.append(f"says {sentence.strip()[:70]!r} but didn't hand off")
    return problems


EVERY_TRIAL.append(promised_reply_has_ticket)
