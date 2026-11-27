"""Point Parcel's api backend (the Anthropic SDK) at OpenRouter, an Anthropic-compatible gateway.

Set OPENROUTER_API_KEY in your environment first. The api backend sends only Parcel's own system
prompt, tools and messages: no Claude Code context (account email, date, working directory).
With an Anthropic API key instead, skip this file and set ANTHROPIC_API_KEY and
PARCEL_MODEL=claude-haiku-5-5."""
import os


def use_openrouter(model="anthropic/claude-haiku-5.5"):
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise SystemExit("Set OPENROUTER_API_KEY first.")
    os.environ["ANTHROPIC_API_KEY"] = key
    os.environ["ANTHROPIC_BASE_URL"] = "https://openrouter.ai/api"
    os.environ["PARCEL_BACKEND"] = "api"
    os.environ["PARCEL_MODEL"] = model
