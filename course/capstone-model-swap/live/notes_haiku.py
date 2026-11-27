"""All 150 live conversations on Haiku 5.5 (api via OpenRouter) read in full by the course author (with Claude),
against the help centre, the system prompt and the order data, on 2026-11-26. Same standard as the Gemma notes
(notes.py), with search misses kept in their own list."""
FAILURES = {
    "w138": "sofa build time: handed off as customer_asked though the customer never asked for a person",
    "w146": "two cracked plates: asks for photos before any refund (photo question, as in the suite)",
    "w148": "chipped mug: asks for photos before any refund (photo question)",
    "w269": "'can the person I'm gifting exchange it?': answers about gift cards instead (same as Gemma)",
}
# The article that answers the question wasn't retrieved; Haiku said it didn't have the information and offered a person.
# Honest, but the customer leaves without an answer the help centre has. (Gemma's notes count 3 of these as failures:
# w104, w132, w238.)
SEARCH_MISSES = {
    "w103": "dining chair delivery time: KB-101 not retrieved",
    "w104": "used once: KB-104 not retrieved",
    "w132": "opened bedding: KB-109 not retrieved (says it doesn't have the list)",
    "w170": "final-sale cushion: KB-109 not retrieved",
    "w238": "returns question in French: nothing retrieved; replied in French that it has no returns information",
    "w265": "rug by 20 December: KB-101 not retrieved",
}
# Gemma failures that Haiku got right, for comparison: w149 one glass £5 (Gemma £30), w230 one napkin £5.50
# (Gemma £22), w151/w165/w174 no false promise, w103/w245/w250 no silent hand-off, w152 towels and w229 duvet
# (Gemma refunded £50; Haiku handed off w152, and on w229 noticed the order was a duvet, not a throw), w153 sparking
# heater handed off as safety_or_legal, w223 no invented dispatch date, w242 no made-up error text.
# Notes: w163 and w238 replied in the customer's language (German, French); the prompt says "Use British English".
