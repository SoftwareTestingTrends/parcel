"""Tests for the graders themselves, on small hand-made transcripts with known answers.
If a grader is wrong, every result it gives is wrong, so it gets tests like any other code."""
from graders import citations_were_retrieved, no_too_soon_promise, refund_claims_match


def transcript(*events, refunds=()):
    return {"events": list(events), "end_state": {"refunds": list(refunds), "hand_offs": []}}


def customer(text):
    return {"type": "customer", "text": text}


def given(*ids):
    return {"type": "retrieval", "articles": [{"id": i} for i in ids]}


def parcel(text):
    return {"type": "parcel", "text": text}


def lookup(already_refunded):
    return {"type": "tool_call", "name": "lookup_order", "is_error": False,
            "result": f'{{"order_id": "HL-10318", "already_refunded": {already_refunded}}}'}


def test_article_given_earlier_in_the_conversation_counts():
    t = transcript(customer("My chair is cracked"), given("KB-106"), parcel("Can I have your email?"),
                   customer("dev.patel@example.com"), given(), parcel("We'll put it right [KB-106]."))
    assert citations_were_retrieved(t) == []


def test_article_never_given_is_flagged():
    t = transcript(customer("Hi"), given("KB-101"), parcel("Refunds take 5 to 10 working days [KB-105]."))
    assert citations_were_retrieved(t) == ["cites KB-105, which it wasn't given"]


def test_refund_made_before_the_conversation_is_not_a_false_claim():
    t = transcript(lookup(120.0), parcel("The refund for your floor lamp has been processed."))
    assert refund_claims_match(t) == []


def test_refund_claim_with_no_refund_is_flagged():
    t = transcript(lookup(0.0), parcel("I've processed a refund of £36.00."))
    assert refund_claims_match(t) != []


def test_shortly_is_flagged():
    assert no_too_soon_promise(transcript(parcel("They will be with you shortly."))) == ["says 'shortly'"]
