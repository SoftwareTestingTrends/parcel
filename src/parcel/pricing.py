"""List prices (USD per million tokens) for estimating what a conversation costs.

Check https://www.anthropic.com/pricing before quoting these; they change.
Local models through Ollama cost nothing per token.
"""

PRICES = {
    "claude-opus-5-5": (4.00, 20.00),
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-haiku-5-5": (0.10, 0.50),
}
CACHE_WRITE = 1.25  # cache writes cost 1.25x the input price
CACHE_READ = 0.10  # cache reads cost 0.1x the input price


def estimate_cost(model: str, usage: dict) -> float | None:
    if model not in PRICES:
        return None
    inp, out = PRICES[model]
    total = (
        usage.get("input_tokens", 0) * inp
        + usage.get("cache_creation_input_tokens", 0) * inp * CACHE_WRITE
        + usage.get("cache_read_input_tokens", 0) * inp * CACHE_READ
        + usage.get("output_tokens", 0) * out
    )
    return round(total / 1_000_000, 6)
