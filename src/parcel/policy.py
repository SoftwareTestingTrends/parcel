"""Hollow Lane's support policy, in one place.

The help-centre articles say the same things in words. Code that enforces a rule
(the refund tool) reads its numbers from here.
"""

from datetime import date

REFUND_LIMIT_GBP = 50.00  # Parcel may refund up to this much per order
RETURN_WINDOW_DAYS = 30  # days after delivery
DAMAGE_REPORT_DAYS = 14  # days after delivery to report damage in transit

# When Parcel must pass the customer to a person (see the system prompt).
HAND_OFF_REASONS = (
    "customer_asked",  # the customer asks for a person
    "refund_over_limit",  # a refund over the limit is due or requested
    "safety_or_legal",  # injury, fire, other safety problem, or a legal complaint
    "unresolved_twice",  # the customer asked the same thing twice without a resolution
    "account_security",  # suspected fraud or someone else's account
)


def days_between(earlier: str, later: str) -> int:
    return (date.fromisoformat(later) - date.fromisoformat(earlier)).days
