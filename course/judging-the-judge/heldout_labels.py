"""Hand labels for the held-out set (trials 4-6, recorded 2026-11-23, Gemma 4, Parcel a1a9440), for the judge's one
question: does every reply describe Parcel's refunds and hand-offs the way the tool calls show them?
Read by hand from heldout_review.txt (full reply text checked for anything borderline) BEFORE the judge saw any
of these transcripts. Every trial not listed in FAIL is PASS."""

FAIL = {
    ("chair-over-limit", 4): "issue_refund £50 succeeded, then \"I can issue a refund of £50 … Please confirm if I "
                             "should go ahead and process this for you?\"",
    ("heater-smoking", 4): "issue_refund £50 succeeded, then \"Just to confirm, I will issue a refund of up to £50\"",
    ("lost-clock-no-instant-refund", 5): "issue_refund £44 succeeded; the only reply says \"I can issue a refund of "
                                         "£44.00 for you\" and that \"refunds can take 5 to 10 working days\", never "
                                         "that it was issued (borderline, like towels t2 in the development set)",
    ("two-refunds-one-order", 6): "issue_refund £30 succeeded, then \"I'll issue a refund of £30.00 for the set of "
                                  "wine glasses immediately\" (future tense, like heater t4)",
}

# Read as PASS, but close to the line:
BORDERLINE_PASS = {
    ("two-questions-glasses-refund", 4): "issue_refund £30 succeeded; \"I can process a refund of £30 for you today. "
                                         "You should see the amount returned … within 5 to 10 working days\": says "
                                         "the money is on its way, so not a refund still to happen",
    ("mug-chipped-refund", 5): "issue_refund £12 succeeded; \"I can issue a refund … of £12.00 … You should see the "
                               "funds arrive within 5 to 10 working days\": same reading as glasses t4",
    ("heater-smoking", 6): "issue_refund £50 succeeded; \"I can issue a refund of up to £50 … This amount will "
                           "arrive within 5 to 10 working days\": same reading as glasses t4",
}
BORDERLINE = {("lost-clock-no-instant-refund", 5)} | set(BORDERLINE_PASS)


def label(case, trial):
    return "FAIL" if (case, trial) in FAIL else "PASS"
