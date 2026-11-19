"""An offline stand-in for a model: simple keyword rules, same answer every time.

Use it to run the app and the test suite with no model at all. It's not meant to
be good; real evals run against ollama, claude-code or api.
"""

import json
import re

from ..policy import REFUND_LIMIT_GBP
from ..tools import run_tool
from ..transcript import ToolCall, TurnResult

ORDER_RE = re.compile(r"\bHL-\d{5}\b", re.I)
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
ARTICLE_RE = re.compile(r'<article id="(KB-\d+)">\n(.*?)\n</article>', re.S)
CUSTOMER_RE = re.compile(r"<customer_message>\n(.*)\n</customer_message>", re.S)

PERSON_WORDS = ("person", "human", "real agent", "someone", "manager")
SAFETY_WORDS = ("injur", "fire", "burn", "smoke", "lawyer", "legal", "sue ", "court")
DAMAGE_WORDS = ("damaged", "broken", "cracked", "faulty", "smashed", "doesn't work")


class MockSession:
    def __init__(self, settings, store, system_prompt):
        self.store = store
        self.order_id: str | None = None
        self.email: str | None = None

    def _call(self, result: TurnResult, name: str, args: dict) -> tuple[str, bool]:
        output, is_error = run_tool(self.store, name, args)
        result.tool_calls.append(ToolCall(name, args, output, is_error))
        return output, is_error

    def send(self, text: str) -> TurnResult:
        match = CUSTOMER_RE.search(text)
        message = match.group(1) if match else text
        lower = message.lower()
        articles = ARTICLE_RE.findall(text)
        if m := ORDER_RE.search(message):
            self.order_id = m.group(0).upper()
        if m := EMAIL_RE.search(message):
            self.email = m.group(0)
        result = TurnResult(text="", stop_reason="mock")

        if any(w in lower for w in SAFETY_WORDS):
            self._call(result, "hand_off", {"reason": "safety_or_legal", "summary": message[:200]})
            result.text = (
                "I'm sorry to hear that. Please stop using the item. I've passed this to our "
                "customer care team, who'll be in touch by the end of the next working day."
            )
            return result
        if any(w in lower for w in PERSON_WORDS):
            self._call(result, "hand_off", {"reason": "customer_asked", "summary": message[:200]})
            result.text = "Of course. I've passed you to our customer care team [KB-112]."
            return result
        if self.order_id and not self.email:
            result.text = f"I can look up {self.order_id}. What email address is on the order?"
            return result
        if self.order_id and self.email:
            output, is_error = self._call(
                result, "lookup_order", {"order_id": self.order_id, "email": self.email}
            )
            if is_error:
                result.text = "I couldn't find an order with that number and email address."
                return result
            order = json.loads(output)
            if any(w in lower for w in DAMAGE_WORDS):
                due = round(order["total"] - order["already_refunded"], 2)
                if due > REFUND_LIMIT_GBP:
                    self._call(
                        result,
                        "hand_off",
                        {"reason": "refund_over_limit", "summary": f"Damaged {self.order_id}"},
                    )
                    result.text = (
                        f"I'm sorry it arrived damaged. A refund of £{due:.2f} needs our customer "
                        "care team, so I've passed it to them [KB-105]."
                    )
                    return result
                refund, is_error = self._call(
                    result,
                    "issue_refund",
                    {
                        "order_id": self.order_id,
                        "email": self.email,
                        "amount_gbp": due,
                        "reason": "damaged_or_faulty",
                    },
                )
                if is_error:
                    result.text = "I'm sorry, I can't refund that order here."
                else:
                    result.text = (
                        f"I'm sorry it arrived damaged. I've refunded £{due:.2f}; it'll reach "
                        "you in 5 to 10 working days [KB-105]."
                    )
                return result
            result.text = f"Your order {self.order_id} is {order['status']} [KB-102]."
            return result
        if articles:
            article_id, body = articles[0]
            paragraphs = [p for p in body.split("\n\n")[1:] if p.strip()]
            first = paragraphs[0].strip() if paragraphs else body
            result.text = f"{first} [{article_id}]"
            return result
        result.text = (
            "I'm sorry, I don't know the answer to that. Would you like me to pass you to a person?"
        )
        return result
