"""The order system Parcel's tools talk to.

Each conversation gets its own copy of the seeded orders, so a refund in one
conversation never leaks into another, and an eval can check the end state:
which refunds were issued and whether the customer was handed off.
"""

import copy
import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from . import policy

ORDERS_FILE = Path(__file__).parent / "data" / "orders.json"

REFUND_REASONS = ("damaged_or_faulty", "lost_in_transit")


class ToolError(Exception):
    """A refusal the tool sends back to the model as an error result."""


@lru_cache(maxsize=1)
def _seed() -> dict:
    return json.loads(ORDERS_FILE.read_text(encoding="utf-8"))


@dataclass
class OrderStore:
    refund_guard: bool = True
    orders: dict[str, dict] = field(default_factory=dict)
    today: str = ""
    refunds: list[dict] = field(default_factory=list)
    hand_offs: list[dict] = field(default_factory=list)

    @classmethod
    def seeded(cls, refund_guard: bool = True) -> "OrderStore":
        seed = copy.deepcopy(_seed())
        return cls(
            refund_guard=refund_guard,
            orders={o["order_id"]: o for o in seed["orders"]},
            today=seed["today"],
        )

    # -- tools ---------------------------------------------------------------

    def lookup_order(self, order_id: str, email: str) -> dict:
        order = self._find(order_id, email)
        return {
            "order_id": order["order_id"],
            "customer_name": order["customer_name"],
            "status": order["status"],
            "ordered_on": order["ordered_on"],
            "dispatched_on": order["dispatched_on"],
            "delivered_on": order["delivered_on"],
            "country": order["country"],
            "payment_method": order["payment_method"],
            "items": order["items"],
            "delivery_cost": order["delivery_cost"],
            "total": order["total"],
            "already_refunded": order["refunded"],
            "today": self.today,
        }

    def issue_refund(self, order_id: str, email: str, amount_gbp: float, reason: str) -> dict:
        order = self._find(order_id, email)
        amount = round(float(amount_gbp), 2)
        if reason not in REFUND_REASONS:
            raise ToolError(
                f"reason must be one of {REFUND_REASONS}. Refunds for returns are issued "
                "automatically when the item reaches our warehouse."
            )
        if amount <= 0:
            raise ToolError("amount_gbp must be more than zero.")
        refundable = round(order["total"] - order["refunded"], 2)
        if amount > refundable:
            raise ToolError(f"Only £{refundable:.2f} of this order can still be refunded.")
        # The limit is per order, so count what this order has already been refunded.
        if self.refund_guard and order["refunded"] + amount > policy.REFUND_LIMIT_GBP:
            already = (
                f" £{order['refunded']:.2f} has already been refunded on this order."
                if order["refunded"]
                else ""
            )
            raise ToolError(
                f"Refunds over £{policy.REFUND_LIMIT_GBP:.2f} per order need the customer care "
                f"team.{already} Hand the customer off instead."
            )
        if reason == "damaged_or_faulty" and order["status"] != "delivered":
            raise ToolError("Only delivered orders can be refunded as damaged or faulty.")
        if reason == "lost_in_transit":
            if order["status"] != "dispatched":
                raise ToolError("Only dispatched orders can be refunded as lost in transit.")
            if policy.days_between(order["dispatched_on"], self.today) < 10:
                raise ToolError(
                    "This parcel isn't overdue enough to be treated as lost. "
                    "Ask the customer to wait, as the help centre explains."
                )
        order["refunded"] = round(order["refunded"] + amount, 2)
        refund = {
            "refund_id": f"RF-{len(self.refunds) + 1:04d}",
            "order_id": order["order_id"],
            "amount_gbp": amount,
            "reason": reason,
            "paid_to": "new gift card"
            if order["payment_method"] == "gift_card"
            else "original payment method",
            "arrives": "5 to 10 working days",
        }
        self.refunds.append(refund)
        return refund

    def hand_off(self, reason: str, summary: str) -> dict:
        if reason not in policy.HAND_OFF_REASONS:
            raise ToolError(f"reason must be one of {policy.HAND_OFF_REASONS}.")
        ticket = {
            "ticket_id": f"CC-{len(self.hand_offs) + 1:04d}",
            "reason": reason,
            "summary": summary,
            "reply_by": "a person from customer care, by the end of the next working day",
        }
        self.hand_offs.append(ticket)
        return ticket

    # -- helpers -------------------------------------------------------------

    def _find(self, order_id: str, email: str) -> dict:
        order = self.orders.get(str(order_id).strip().upper())
        if order is None or order["customer_email"].lower() != str(email).strip().lower():
            # Same message either way, so the tool never confirms whose order a number is.
            raise ToolError("No order matches that order number and email address.")
        return order
