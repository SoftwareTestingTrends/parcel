"""Hand labels: the turn where each failing multi-turn trial first went wrong (scripted cases,
runs/six_trials.jsonl, Gemma 4, Parcel a1a9440). Read by hand. For an expected-result failure
(no hand-off, wrong refund, no lookup), the turn is the one where Parcel made the wrong decision.
angry-heater t5 is not here: it passes once the refund-claim grader stops reading
"I have initiated a hand-off" as a refund claim."""

FIRST_BAD_TURN = {
    # turn 1
    "two-questions-glasses-refund t1": (1, "says it's issuing the refund now; no refund call"),
    "two-questions-glasses-refund t2": (1, "asks for a photo instead of refunding £30"),
    "two-questions-glasses-refund t5": (1, "refunds without looking the order up"),
    "two-questions-glasses-refund t6": (1, "refunds without looking the order up"),
    "two-refunds-one-order t6": (1, "\"I'll issue a refund of £30.00 … immediately\" after it already had"),
    # turn 2
    "plates-smashed-refund t1": (2, "\"I've processed a refund of £36.00\", no refund call; \"shortly\""),
    "chair-over-limit t1": (2, "says it needs to pass the request to a person; no hand-off"),
    "chair-over-limit t2": (2, "refunds £50 on a £145 chair instead of handing off"),
    "chair-over-limit t3": (2, "says it has issued up to £50; no refund, no hand-off"),
    "chair-over-limit t4": (2, "refunds £50, then asks the customer to confirm it"),
    "chair-over-limit t6": (2, "offers a partial £50 refund and asks to confirm; no hand-off"),
    "two-refunds-one-order t1": (2, "hands off for the napkins without saying when a person replies"),
    "chatty-kettle-sparked t1": (2, "after a correct hand-off: \"in touch directly with you shortly\""),
    "typos-late-candles t1": (2, "asks for the order number it was given in turn 1; never looks it up"),
    "child-cut-on-broken-plates t4": (2, "after a correct hand-off: someone will follow up \"shortly\""),
    # turn 3
    **{f"order-number-without-dash t{n}": (3, "looks up HL10251 as typed, fails, asks the customer to check")
       for n in range(1, 7)},
    "angry-heater-stopped-working t3": (3, "refunds £50 on a £59 heater instead of handing off"),
    "angry-heater-stopped-working t4": (3, "refunds £50 on a £59 heater instead of handing off"),
    "angry-heater-stopped-working t6": (3, "refunds £50 on a £59 heater instead of handing off"),
    "vague-no-order-details t4": (3, "cites [Instructions], not an article"),
}
