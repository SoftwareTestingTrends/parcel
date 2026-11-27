"""Hand labels: is every claim in Parcel's replies supported by something Parcel was given?
Run: gemma4-prompt-v2.jsonl (the 100 written conversations, Gemma 4, Parcel a1a9440, prompt v2).
Sources that count: the articles retrieved so far in the conversation, the order record from
lookup_order, the result of a tool call, Parcel's own rules (the £50 limit, the hand-off reply time),
and the customer's own words. Written by reading every conversation, before running any judge.

FAIL = a reply states a fact or an action that none of those sources supports, even if it happens to
be true. Wrong citations are labelled separately (CITATIONS below), because the claim can be
supported while the citation points to the wrong article."""

FAIL = {
    "c048": "Says the order was dispatched on 5 November; the order record says dispatched 6 November "
            "(5 November is the order date).",
    "c064": "Says \"I have gone ahead and issued a refund of £42.00\"; issue_refund was never called.",
    "c098": "Tells the customer to organise the change \"through the courier service or through your account "
            "settings\"; the address article (KB-108) wasn't retrieved. General knowledge, which the prompt forbids.",
    "c100": "\"Since the item is faulty\": the customer only asked whether a chemical smell is normal; "
            "nothing Parcel was given says the rug is faulty.",
    # Added after rereading the judge's disagreements (the judge failed them; we had passed them):
    "c011": "\"You can return most items, including a rug\": KB-104 says most items and that some can't be "
            "returned; the list (KB-109) wasn't given, so nothing says rugs can be returned.",
    "c049": "\"We will let you know as soon as it has been dispatched\": the tracking article (KB-102) wasn't "
            "given. Noticed on the first read and wrongly let through as minor.",
    "c071": "\"They will be able to process a full resolution for the damaged item\": nothing given says what "
            "the team will do.",
}

# Rereading the judge's disagreements, we kept our label:
#   c024 judge FAIL, ours PASS: "unable to refund the difference if an item goes on sale after your order"
#        is broader than KB-114, but the next sentence gives the exact rule (within 7 days).
#   c100 judge PASS, ours FAIL: the judge read "the item is faulty" as following from the customer's report.

# c074 refunds £36.00: first labelled FAIL from a summary that left out the quantity; the order record
# has 2 candles at £18, so the amount is supported. Its citation is still wrong (below).

# Citations whose article doesn't say what the sentence claims (of 77 citations in this run).
CITATIONS = {
    "c069": "Cites KB-106 (damaged or faulty) for \"a refund of up to £50\"; the £50 limit is in KB-105 "
            "and Parcel's rules, not KB-106.",
    "c074": "Cites KB-102 (tracking) for a refund because of the delay; KB-102 says nothing about refunds.",
}

# Questions the help centre can't answer, or whose article the search missed: did Parcel say it
# didn't know (or hand off) instead of answering?
SAYS_IT_DOESNT_KNOW = {
    # no article answers it
    "c035": True, "c036": True, "c037": True, "c038": True, "c039": True, "c041": True,
    "c042": True, "c060": True, "c092": True, "c100": True,
    # an article answers it, but the search missed it
    "c006": True, "c017": True, "c018": True, "c040": True,
}
