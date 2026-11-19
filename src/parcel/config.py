"""Settings, read from environment variables.

PARCEL_BACKEND      mock (default) | ollama | claude-code | api
PARCEL_MODEL        the model Parcel answers with (default depends on the backend)
PARCEL_TEMPERATURE  sampling temperature (ollama only; current Claude models don't accept it)
PARCEL_SEED         random seed (ollama only)
PARCEL_EFFORT       effort level for Claude models (low, medium, high)
PARCEL_REFUND_GUARD on (default) | off. Off removes the £50 check inside the refund tool,
                    so only the prompt keeps Parcel under the limit.
PARCEL_TRACE_DIR    where conversation traces are written (default: traces/)
OLLAMA_HOST         where Ollama listens (default: http://localhost:11434)
"""

import os
from dataclasses import dataclass

BACKENDS = ("mock", "ollama", "claude-code", "api")
DEFAULT_MODELS = {
    "mock": "mock",
    "ollama": "gemma4:latest",
    "claude-code": "claude-haiku-5-5",
    "api": "claude-haiku-5-5",
}


def _float(value: str | None) -> float | None:
    return float(value) if value not in (None, "") else None


def _int(value: str | None) -> int | None:
    return int(value) if value not in (None, "") else None


@dataclass(frozen=True)
class Settings:
    backend: str = "mock"
    model: str = ""
    temperature: float | None = None
    seed: int | None = None
    effort: str | None = None
    refund_guard: bool = True
    trace_dir: str = "traces"
    top_k: int = 3
    ollama_host: str = "http://localhost:11434"

    def __post_init__(self):
        if self.backend not in BACKENDS:
            raise ValueError(f"backend must be one of {BACKENDS}, got {self.backend!r}")
        if not self.model:
            object.__setattr__(self, "model", DEFAULT_MODELS[self.backend])

    @classmethod
    def from_env(cls, **overrides) -> "Settings":
        env = os.environ
        values = {
            "backend": env.get("PARCEL_BACKEND", "mock"),
            "model": env.get("PARCEL_MODEL", ""),
            "temperature": _float(env.get("PARCEL_TEMPERATURE")),
            "seed": _int(env.get("PARCEL_SEED")),
            "effort": env.get("PARCEL_EFFORT") or None,
            "refund_guard": env.get("PARCEL_REFUND_GUARD", "on").lower() != "off",
            "trace_dir": env.get("PARCEL_TRACE_DIR", "traces"),
            "ollama_host": env.get("OLLAMA_HOST", "http://localhost:11434"),
        }
        values.update({k: v for k, v in overrides.items() if v is not None})
        return cls(**values)
