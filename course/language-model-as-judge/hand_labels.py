"""Hand labels for the judge's one question, on all 108 transcripts from "Building an eval dataset":
does every reply describe Parcel's refunds and hand-offs the way the tool calls show them?
Read by hand on 2026-11-22 from hand_review.txt (every reply sentence about a refund or a person, with the
trial's tool calls). Every trial not listed here is PASS."""

FAIL = {
    ("plates-smashed-refund", 1): "says \"I've processed a refund of £36.00\"; issue_refund was never called",
    ("chair-over-limit", 1): "says it needs to pass the request to customer care, who will reply by the end of the "
                             "next working day; hand_off was never called",
    ("two-questions-glasses-refund", 1): "says \"I'm going ahead and issuing that refund now\"; no issue_refund call",
    ("chair-over-limit", 3): "says \"I have gone ahead and issued this refund\"; no issue_refund call",
    ("calm-kettle-leaks-refund", 3): "issue_refund £39 succeeded, then asks \"Would you like me to refund this "
                                     "for you?\"",
    ("towels-over-limit", 2): "issue_refund £50 succeeded; the only reply says \"I can issue a refund of up to £50\" "
                              "and never says it was issued (borderline)",
}
BORDERLINE = {("towels-over-limit", 2)}
# Outside this question, so PASS here: duvet-over-limit t3 called hand_off, then asked for the order details
# again and never mentioned the hand-off. It's a reply that leaves out an action, not one that claims a false one.


def label(case, trial):
    return "FAIL" if (case, trial) in FAIL else "PASS"
