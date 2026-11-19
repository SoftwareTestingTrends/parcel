import pytest

from parcel.orders import OrderStore, ToolError

DEV = ("HL-10251", "dev.patel@example.com")  # delivered, total £39.95


def test_lookup_needs_matching_email():
    store = OrderStore.seeded()
    assert store.lookup_order(*DEV)["status"] == "delivered"
    with pytest.raises(ToolError, match="No order matches"):
        store.lookup_order("HL-10251", "someone.else@example.com")


def test_lookup_message_is_same_for_missing_order_and_wrong_email():
    store = OrderStore.seeded()
    with pytest.raises(ToolError) as missing:
        store.lookup_order("HL-99999", "dev.patel@example.com")
    with pytest.raises(ToolError) as wrong_email:
        store.lookup_order("HL-10251", "x@example.com")
    assert str(missing.value) == str(wrong_email.value)


@pytest.mark.parametrize("amount, allowed", [(49.99, True), (50.00, True), (50.01, False)])
def test_refund_limit_boundary(amount, allowed):
    store = OrderStore.seeded()
    order_id, email = "HL-10252", "dev.patel@example.com"  # total £319
    if allowed:
        assert (
            store.issue_refund(order_id, email, amount, "damaged_or_faulty")["amount_gbp"] == amount
        )
    else:
        with pytest.raises(ToolError, match="customer care"):
            store.issue_refund(order_id, email, amount, "damaged_or_faulty")


def test_guard_off_lets_large_refunds_through():
    store = OrderStore.seeded(refund_guard=False)
    refund = store.issue_refund("HL-10252", "dev.patel@example.com", 200, "damaged_or_faulty")
    assert refund["amount_gbp"] == 200


def test_cannot_refund_more_than_remaining():
    store = OrderStore.seeded()
    store.issue_refund(*DEV, 30, "damaged_or_faulty")
    with pytest.raises(ToolError, match="Only £9.95"):
        store.issue_refund(*DEV, 10, "damaged_or_faulty")


def test_returns_are_not_refunded_by_the_assistant():
    with pytest.raises(ToolError, match="warehouse"):
        OrderStore.seeded().issue_refund(*DEV, 10, "return")


def test_lost_in_transit_needs_ten_days_since_dispatch():
    store = OrderStore.seeded()
    with pytest.raises(ToolError, match="overdue"):  # dispatched 4 days ago
        store.issue_refund("HL-10240", "ben.walker@example.com", 20, "lost_in_transit")
    refund = store.issue_refund("HL-10305", "noah.reid@example.com", 44, "lost_in_transit")
    assert refund["amount_gbp"] == 44


def test_gift_card_orders_refund_to_gift_card():
    refund = OrderStore.seeded().issue_refund(
        "HL-10275", "hana.suzuki@example.com", 10, "damaged_or_faulty"
    )
    assert refund["paid_to"] == "new gift card"


def test_each_store_is_independent():
    first, second = OrderStore.seeded(), OrderStore.seeded()
    first.issue_refund(*DEV, 10, "damaged_or_faulty")
    assert second.lookup_order(*DEV)["already_refunded"] == 0


def test_hand_off_needs_a_known_reason():
    store = OrderStore.seeded()
    assert store.hand_off("customer_asked", "wants a person")["ticket_id"] == "CC-0001"
    with pytest.raises(ToolError):
        store.hand_off("bored", "x")
