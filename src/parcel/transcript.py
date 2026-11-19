"""What a conversation looked like, in one neutral format for every backend.

A transcript is a list of events in order:
  customer   what the customer typed
  retrieval  which help-centre articles were found, with scores
  tool_call  a tool Parcel called, its arguments and its result
  parcel     what Parcel replied
Evals read transcripts; they never need to know which backend produced one.
"""

import json
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class ToolCall:
    name: str
    args: dict
    result: str
    is_error: bool


@dataclass
class TurnResult:
    text: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    usage: dict = field(default_factory=dict)
    cost_usd: float | None = None
    stop_reason: str = ""


@dataclass
class Transcript:
    backend: str
    model: str
    prompt_version: str
    refund_guard: bool
    conversation_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    started_at: float = field(default_factory=time.time)
    events: list[dict] = field(default_factory=list)
    usage: dict = field(default_factory=dict)
    cost_usd: float | None = None
    seconds: float = 0.0
    end_state: dict = field(default_factory=dict)

    def add(self, kind: str, **data) -> None:
        self.events.append({"type": kind, **data})

    def add_usage(self, usage: dict, cost: float | None) -> None:
        for key, value in usage.items():
            if isinstance(value, int | float):
                self.usage[key] = self.usage.get(key, 0) + value
        if cost is not None:
            self.cost_usd = round((self.cost_usd or 0) + cost, 6)

    # Convenience views for evals --------------------------------------------

    @property
    def replies(self) -> list[str]:
        return [e["text"] for e in self.events if e["type"] == "parcel"]

    @property
    def final_reply(self) -> str:
        return self.replies[-1] if self.replies else ""

    @property
    def tool_calls(self) -> list[dict]:
        return [e for e in self.events if e["type"] == "tool_call"]

    @property
    def retrieved_ids(self) -> list[list[str]]:
        return [[a["id"] for a in e["articles"]] for e in self.events if e["type"] == "retrieval"]

    def to_dict(self) -> dict:
        return asdict(self)

    def save(self, directory: str | Path) -> Path:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        file = path / f"{time.strftime('%Y-%m-%d')}.jsonl"
        with file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(self.to_dict()) + "\n")
        return file
