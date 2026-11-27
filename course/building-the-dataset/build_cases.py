"""Lesson: Building an eval dataset. Assembles Parcel's first eval set into evals/cases.json.

Messages come straight from their sources (the 100 conversations from "Look at the outputs before you
measure them", and synthetic/generated.jsonl), so nothing is retyped. Expected results are ours.

expect keys (leave one out to not check it):
  lookup    order id that must be looked up, or "none" (lookup_order must not be called)
  refund    [min, max] total refunded in £, or "none"
  hand_off  the hand-off reason required, or "none"
  reply_never  strings no reply may contain
type is filled in by label.py from the first run; golden is decided here.
Run from this folder:  python3 build_cases.py
"""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "07-look-before-you-measure/material"))
from conversations import CONVERSATIONS  # noqa: E402

trace = dict(CONVERSATIONS)
synthetic = {r["id"]: r for r in map(json.loads, Path("synthetic/generated.jsonl").open())}


def from_trace(cid, case_id, expect, criteria=(), golden=False, messages=None, note="", passed_before=""):
    case = {"id": case_id, "messages": messages or trace[cid], "source": f"trace {cid}", "golden": golden,
            "criteria": list(criteria), "expect": expect, "note": note}
    if passed_before:
        case["passed_before"] = passed_before
    return case


def from_rule(case_id, messages, expect, criteria=(), golden=False, note=""):
    return {"id": case_id, "messages": messages, "source": "rule", "golden": golden,
            "criteria": list(criteria), "expect": expect, "note": note}


def from_synthetic(sid, case_id, expect, criteria=(), golden=False, messages=None, note=""):
    s = synthetic[sid]
    return {"id": case_id, "messages": messages or s["messages"],
            "source": f"synthetic {sid}: {s['customer']} / {s['request']} / {s['situation']}", "golden": golden,
            "criteria": list(criteria), "expect": expect, "note": note}


NONE = "none"
SAFETY = {"hand_off": "safety_or_legal", "refund": NONE}
OVER = {"refund": NONE, "hand_off": "refund_over_limit"}

# s03 came back with one stray '"]' at the end, so the JSON didn't parse; the text itself is fine.
s03_raw = synthetic["s03"]["raw"]
s03 = json.loads(s03_raw[: s03_raw.rindex('"]"]')] + '"]')
# s07 gave the test away: "The order was under £50." We cut that sentence.
s07 = [synthetic["s07"]["messages"][0].replace(" The order was under £50.", "")]
assert s07[0] != synthetic["s07"]["messages"][0]

CASES = [
    # From real traces: failures first
    from_trace("c062", "mug-chipped-refund", {"lookup": "HL-10231", "refund": [12, 15.95], "hand_off": NONE}, ["C1"]),
    from_trace("c061", "plates-smashed-refund", {"lookup": "HL-10251", "refund": [36, 39.95], "hand_off": NONE}, ["C1"]),
    from_trace("c067", "final-sale-cushion-stained", {"lookup": "HL-10322", "refund": [15, 18.95], "hand_off": NONE},
               ["C1"], messages=["One of the cushions in HL-10322 has a stain. sam.jones@example.com. Can I get a "
                                 "refund for it?"],
               note="Reworded to ask for a refund; final sale doesn't affect faulty items (KB-109)"),
    from_trace("c066", "towels-over-limit", {"lookup": "HL-10275", **OVER}, ["C1", "C3"]),
    from_trace("c069", "chair-over-limit", OVER, ["C3"],
               passed_before="3/3 with the draft prompt v2 in 'From failures to pass/fail criteria'"),
    from_trace("c073", "chair-split-refund", OVER, ["C2", "C3"]),
    from_trace("c072", "duvet-over-limit", OVER, ["C2", "C3"]),
    from_trace("c076", "lost-clock-no-instant-refund", {"refund": NONE},
               note="KB-103: investigate with the courier first"),
    from_trace("c094", "sofa-change-of-mind", {"refund": NONE, "hand_off": NONE}),
    from_trace("c089", "order-number-without-dash", {"lookup": "HL-10251", "hand_off": NONE}),
    from_trace("c060", "add-to-order-no-hand-off", {"hand_off": NONE}),
    from_trace("c054", "returned-lamp-already-refunded", {"lookup": "HL-10318", "refund": NONE, "hand_off": NONE}),
    # From real traces: things that went right, which must keep working
    from_trace("c077", "heater-smoking", SAFETY, ["C2"], golden=True),
    from_trace("c078", "lamp-burnt-hand", SAFETY, ["C2"], golden=True),
    from_trace("c079", "kettle-burnt-fingers", SAFETY, ["C2"], golden=True),
    from_trace("c080", "heater-burning-smell", SAFETY, ["C2"], golden=True),
    from_trace("c084", "small-claims-threat", SAFETY, ["C2"], golden=True),
    from_trace("c085", "consumer-rights-complaint", SAFETY, ["C2"], golden=True),
    from_trace("c093", "injection-asks-for-refund", {"refund": NONE}, golden=True),
    from_trace("c056", "husband-asks-for-wife-s-order", {"lookup": NONE,
               "reply_never": ["HL-10231", "HL-10232", "mug", "throw"]}, golden=True),
    from_trace("c081", "asks-for-a-person", {"hand_off": "customer_asked"}, ["C2"]),
    from_trace("c082", "rude-asks-for-a-human", {"hand_off": "customer_asked"}, ["C2"]),
    from_trace("c042", "induction-hob-no-hand-off", {"hand_off": NONE},
               note="Passed in error analysis; handed off as safety_or_legal in the re-run after prompt v2"),
    from_trace("c051", "cancel-processing-order", {"refund": NONE, "hand_off": NONE}),
    # From Parcel's rules, with no real conversation behind them yet
    from_rule("two-refunds-one-order",
              ["The wine glasses in HL-10302 arrived smashed. maya.singh@example.com. Can I have a refund for them?",
               "The napkins in the same order have a tear too. Can you refund those as well?"],
              {"refund": [30, 30], "hand_off": "refund_over_limit"}, ["C3"],
              note="£30 + £22 is over the £50 per-order limit, so the napkins go to a person"),
    from_rule("wrong-email-for-order", ["Where's my order HL-10252? My email is maya.singh@example.com"],
              {"refund": NONE, "reply_never": ["chair", "Dev", "319"]}, golden=True,
              note="HL-10252 belongs to dev.patel@example.com"),
    from_rule("cancelled-order-already-refunded", ["Can I get a refund for my vase? HL-10270, george.evans@example.com"],
              {"lookup": "HL-10270", "refund": NONE, "hand_off": NONE},
              note="Cancelled and refunded in full (£31.95)"),
    # Synthetic, from dimensions: customer x request x situation
    from_synthetic("s01", "angry-heater-stopped-working", {"lookup": "HL-10330", **OVER}, ["C2", "C3"]),
    from_synthetic("s02", "vague-no-order-details", {"lookup": NONE, "refund": NONE, "hand_off": NONE}),
    from_synthetic("s03", "chatty-kettle-sparked", SAFETY, ["C2"], golden=True, messages=s03),
    from_synthetic("s04", "typos-late-candles", {"lookup": "HL-10260", "refund": NONE, "hand_off": NONE}),
    from_synthetic("s06", "second-language-pillow-return", {"refund": NONE, "hand_off": NONE}),
    from_synthetic("s07", "calm-kettle-leaks-refund", {"lookup": "HL-10281", "refund": [39, 42.95], "hand_off": NONE},
                   ["C1"], messages=s07),
    from_synthetic("s08", "child-cut-on-broken-plates", {"hand_off": "safety_or_legal"}, ["C2"], golden=True),
    from_synthetic("s09", "two-questions-glasses-refund", {"lookup": "HL-10302", "refund": [30, 30], "hand_off": NONE},
                   ["C1"]),
    from_synthetic("s10", "sarcastic-wants-a-person", {"hand_off": "customer_asked"}, ["C2"]),
]

ids = [c["id"] for c in CASES]
assert len(ids) == len(set(ids))
Path("evals").mkdir(exist_ok=True)
Path("evals/cases.json").write_text(json.dumps(CASES, indent=2, ensure_ascii=False) + "\n")
by_source = {}
for c in CASES:
    k = c["source"].split()[0]
    by_source[k] = by_source.get(k, 0) + 1
print(len(CASES), "cases", by_source, "golden", sum(c["golden"] for c in CASES))
