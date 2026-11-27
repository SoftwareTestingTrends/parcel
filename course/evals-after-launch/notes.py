"""Every one of the 150 live conversations was read in full by the course author (with Claude), checked
against the help centre, the system prompt and the order data. One note per conversation with a failure.
FLAGGED_BY = which live check (from live_checks.py, before the new grader) flagged it, or None."""
NOTES = {
    "w103": ("silent hand-off: called hand_off, reply only offers one; KB-101 (furniture 5-10 days) not retrieved", "hand_off_states_reply_time"),
    "w104": ("doesn't answer 'used once': misses KB-104's unused rule, cites KB-109 only", None),
    "w132": ("opened bedding: says most items can be returned; KB-109 (unsealed duvets) not retrieved", None),
    "w143": ("second message: forgets the order number given in the first", None),
    "w149": ("one glass of six smashed: refunded £30, the whole set; also cites the order number as an article", "citations_are_real"),
    "w151": ("£319 chair, full refund asked: says a person will reply, no hand_off called", None),
    "w152": ("towels £54: refunded £50 on a full-value fault; over-limit refund due, no hand-off", None),
    "w153": ("heater sparked: handed off as refund_over_limit, not safety_or_legal", None),
    "w160": ("asks for another customer's email: refused correctly, then handed off for no reason", None),
    "w165": ("stock question: 'They will reply by the end of the next working day', no hand_off called", None),
    "w170": ("final-sale cushion: explains how to return it, then 'may impact' eligibility; KB-109 says no", None),
    "w174": ("discount for hassle: 'They will reply by the end of the next working day', no hand_off called", None),
    "w223": ("processing order: invents 'shipped within the next 1-2 working days'", None),
    "w229": ("£79 duvet with a hole: refunded £50, no hand-off; reply says 'I will go ahead' after issuing", None),
    "w230": ("one napkin of four stained: refunded £22, the whole set", None),
    "w237": ("clock dispatched 11 days ago: 'should arrive shortly'; KB-103 late-parcel steps not given", "no_too_soon_promise"),
    "w238": ("returns question in French: says the help centre doesn't cover returns (search found nothing)", None),
    "w242": ("misspelt personalised bowl: invents '[Error: The system needs more information…]' in the reply", "citations_are_real"),
    "w245": ("silent hand-off: called hand_off, reply asks 'Would you like me to pass you…?'", "hand_off_states_reply_time"),
    "w250": ("silent hand-off: called hand_off, reply asks 'Would you like me to pass you…?'", "hand_off_states_reply_time"),
    "w269": ("'can the person I'm gifting exchange it?': answers about gift cards instead", None),
    "w275": ("candles to Dublin before Christmas: handed off as unresolved_twice after one question", None),
}
FALSE_ALARMS = {
    "w172": "citations_are_real: '[KB-110, KB-108, KB-103]' is three real articles in one bracket (format, not a wrong source)",
    "w263": "safety_handed_off: 'Christmas delivery cut off for Germany' matched 'cut'",
}
