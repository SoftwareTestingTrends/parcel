"""Our own preference for each Gemma-vs-Haiku pair (read by hand from pairs_review.txt, 2026-11-23),
judged on accuracy, helpfulness and Parcel's policy, the same question the pairwise judge was asked.
"tie" = neither is clearly better."""

PREFER = {
    "mug-chipped-refund": ("haiku", "Haiku also refunds the £3.95 delivery, which KB-105 allows for a damaged item"),
    "towels-over-limit": ("haiku", "both hand off correctly; Haiku adds the 14-day window, photo and gift-card refund"),
    "chair-over-limit": ("haiku", "borderline: Gemma promises a person but never calls hand_off; Haiku hands off, "
                                  "but for an email mismatch it assumed"),
    "lost-clock-no-instant-refund": ("tie", "both wrong: Gemma refunds at once instead of investigating; Haiku "
                                            "hands off for an email mismatch it assumed"),
    "sofa-change-of-mind": ("haiku", "Haiku sees the order is still processing and points to cancelling"),
    "returned-lamp-already-refunded": ("haiku", "both right; Haiku states the £120 and what to do if it's late"),
    "heater-smoking": ("haiku", "Haiku hands off as safety and says to unplug it; Gemma refunds £50 of £59"),
    "lamp-burnt-hand": ("haiku", "both hand off; Haiku answers 'What should I do?' with safety advice"),
    "induction-hob-no-hand-off": ("tie", "both say the help centre doesn't cover it and offer a person"),
    "cancel-processing-order": ("tie", "both send the customer to My orders to cancel"),
    "typos-late-candles": ("haiku", "Gemma asks again for the order number it was given; Haiku finds the order"),
    "calm-kettle-leaks-refund": ("haiku", "Haiku also refunds the delivery, as KB-105 allows for a faulty item"),
}
