"""Backends: the different ways Parcel can reach a model.

Every backend makes a Session for one conversation. A session takes the text
for one customer message (articles included) and returns a TurnResult. Tools
always run through parcel.tools.run_tool, so the order system behaves the same
whichever model is answering.
"""

from ..config import Settings
from ..orders import OrderStore


def new_session(settings: Settings, store: OrderStore, system_prompt: str):
    if settings.backend == "mock":
        from .mock import MockSession

        return MockSession(settings, store, system_prompt)
    if settings.backend == "ollama":
        from .ollama import OllamaSession

        return OllamaSession(settings, store, system_prompt)
    if settings.backend == "api":
        from .api import ApiSession

        return ApiSession(settings, store, system_prompt)
    if settings.backend == "claude-code":
        from .claude_code import ClaudeCodeSession

        return ClaudeCodeSession(settings, store, system_prompt)
    raise ValueError(f"Unknown backend {settings.backend!r}")
