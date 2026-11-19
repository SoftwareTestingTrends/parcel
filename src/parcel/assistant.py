"""Parcel itself: one conversation with one customer.

parcel = Parcel()                       # settings from environment variables
reply = parcel.ask("Where's my order?")
parcel.transcript                       # everything that happened, for evals
"""

import time

from .backends import new_session
from .config import Settings
from .knowledge import HelpCentre, default_help_centre
from .orders import OrderStore
from .prompts import PROMPT_VERSION, SYSTEM_PROMPT, with_articles
from .transcript import Transcript


class Parcel:
    def __init__(
        self,
        settings: Settings | None = None,
        help_centre: HelpCentre | None = None,
        system_prompt: str = SYSTEM_PROMPT,
        prompt_version: str = PROMPT_VERSION,
    ):
        self.settings = settings or Settings.from_env()
        self.help_centre = help_centre or default_help_centre()
        self.store = OrderStore.seeded(refund_guard=self.settings.refund_guard)
        self.session = new_session(self.settings, self.store, system_prompt)
        self.transcript = Transcript(
            backend=self.settings.backend,
            model=self.settings.model,
            prompt_version=prompt_version,
            refund_guard=self.settings.refund_guard,
        )

    def ask(self, message: str) -> str:
        """Send one customer message and return Parcel's reply."""
        started = time.perf_counter()
        hits = self.help_centre.search(message, k=self.settings.top_k)
        self.transcript.add("customer", text=message)
        self.transcript.add(
            "retrieval",
            query=message,
            articles=[
                {"id": h.article.id, "title": h.article.title, "score": h.score} for h in hits
            ],
        )
        turn = self.session.send(with_articles(message, hits))
        for call in turn.tool_calls:
            self.transcript.add(
                "tool_call",
                name=call.name,
                args=call.args,
                result=call.result,
                is_error=call.is_error,
            )
        self.transcript.add("parcel", text=turn.text, stop_reason=turn.stop_reason)
        self.transcript.add_usage(turn.usage, turn.cost_usd)
        self.transcript.seconds = round(self.transcript.seconds + time.perf_counter() - started, 3)
        self.transcript.end_state = {
            "refunds": list(self.store.refunds),
            "hand_offs": list(self.store.hand_offs),
        }
        return turn.text

    def save(self):
        return self.transcript.save(self.settings.trace_dir)
