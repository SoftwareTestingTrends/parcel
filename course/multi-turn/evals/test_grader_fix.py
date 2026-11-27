"""Pins the refund-claim fix: a hand-off is not a refund claim."""
from graders import refund_claims_match


def t(reply):
    return {"events": [{"type": "parcel", "text": reply}], "end_state": {"refunds": [], "hand_offs": []}}


def test_initiated_hand_off_is_not_a_refund_claim():
    assert refund_claims_match(t("The refund is over my limit. I have initiated a hand-off, "
                                 "and a person from customer care will reply.")) == []


def test_claimed_refund_with_no_refund_still_fails():
    assert refund_claims_match(t("I have processed a refund of £36.00 for you."))
