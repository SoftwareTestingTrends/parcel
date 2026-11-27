"""Hand labels for the 18 simulated conversations (runs/simulated.jsonl), read in full.
OK = the customer got what they came for, or a person took it over correctly, and Parcel kept its rules
in every turn. FAIL = Parcel broke a rule or said something false; the turn is where it first happened."""

FAIL = {
    "order-number-without-dash t1": (3, "says \"I will pass your conversation to a person\"; hand_off never called"),
    "two-refunds-one-order t1": (2, "issue_refund for the napkins fails (over £50), then \"I've processed a refund of "
                                    "£22.00\"; no hand-off. The simulated customer said DONE, satisfied."),
    "angry-heater-stopped-working t1": (6, "after a correct hand-off in turn 2: \"Please remain connected, and a manager "
                                           "will take over the conversation shortly.\""),
    "angry-heater-stopped-working t2": (5, "after a correct hand-off in turn 2: \"escalated … to our dedicated finance "
                                           "team. They are reviewing the case immediately.\" No such team; nothing is immediate."),
}

# Not failures, but worth knowing:
# - order-number-without-dash t2, t3: never tried HL-10251 or mentioned the dash; handed off as unresolved_twice.
#   The customer never heard the order status (their goal), but the hand-off follows Parcel's rules.
# - typos-late-candles t1, t2: handed off as unresolved_twice without asking for the email to look the order up.
# - vague-no-order-details t3: two hand-off tickets for one customer (unresolved_twice, then customer_asked).
# - angry-heater-stopped-working t2 reached the 6-turn limit.
