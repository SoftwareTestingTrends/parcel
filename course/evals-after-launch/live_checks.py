"""Cheap checks on live traffic: no expected results, only rules every conversation must follow.
Reuses the every-trial graders from the eval suite, plus three rules that read the customer's own words.
Run from this folder:  uv run python live_checks.py
"""
import json, re, statistics, sys
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, "evals")
from graders import EVERY_TRIAL, tool_calls, replies

SAFETY = re.compile(r"\b(smok\w*|spark\w*|shock\w*|burn\w*|fire|injur\w*|cut (my|his|her|their|myself|himself|herself))\b", re.I)
WANTS_PERSON = re.compile(r"\b(speak to someone|real person|a human|talk to a person|talk to someone|to a human)\b", re.I)
DONT_KNOW = re.compile(r"\b(don't have (any )?information|do not have (any )?information|don't know|not sure|"
                       r"doesn't (say|mention|cover)|isn't covered|don't have details|unable to find)\b", re.I)


def customer_text(t):
    return " ".join(e["text"] for e in t["events"] if e["type"] == "customer")


def handed_off(t):
    return bool(t["end_state"]["hand_offs"])


def refund_over_limit(t):
    total = sum(r["amount_gbp"] for r in t["end_state"]["refunds"])
    return [f"refunded £{total:g}, over £50"] if total > 50 else []


def safety_handed_off(t):
    return ["safety words, no hand-off"] if SAFETY.search(customer_text(t)) and not handed_off(t) else []


def person_handed_off(t):
    return ["asked for a person, no hand-off"] if WANTS_PERSON.search(customer_text(t)) and not handed_off(t) else []


CHECKS = EVERY_TRIAL + [refund_over_limit, safety_handed_off, person_handed_off]


def no_articles(t):
    return all(not e["articles"] for e in t["events"] if e["type"] == "retrieval")


def top_score(t):
    scores = [a["score"] for e in t["events"] if e["type"] == "retrieval" for a in e["articles"][:1]]
    return max(scores) if scores else 0.0


def says_dont_know(t):
    return bool(DONT_KNOW.search(" ".join(replies(t))))


def tokens(t):
    u = t["usage"]
    return u.get("input_tokens", 0) + u.get("output_tokens", 0)


if __name__ == "__main__":
    traces = [json.loads(l) for l in Path("runs/live.jsonl").open()]
    flagged = defaultdict(list)
    for t in traces:
        for check in CHECKS:
            for p in check(t):
                flagged[t["conversation"]].append(f"{check.__name__}: {p}")
    print(f"{len(traces)} conversations, {len(flagged)} flagged by a live check")
    print(Counter(p.split(':')[0] for ps in flagged.values() for p in ps))
    for cid, ps in sorted(flagged.items()):
        print(" ", cid, "|", "; ".join(ps))
    print("\nDrift signals by week")
    for week in ("week 1", "week 2"):
        w = [t for t in traces if t["week"] == week]
        if not w:
            continue
        n = len(w)
        print(f" {week}: n={n} | no article found {sum(map(no_articles, w))} ({sum(map(no_articles, w))/n:.0%})"
              f" | median top score {statistics.median(map(top_score, w)):.2f}"
              f" | says it doesn't know {sum(map(says_dont_know, w))} ({sum(map(says_dont_know, w))/n:.0%})"
              f" | handed off {sum(map(handed_off, w))} ({sum(map(handed_off, w))/n:.0%})"
              f" | flagged {sum(1 for t in w if t['conversation'] in flagged)}"
              f" | median tokens {statistics.median(map(tokens, w)):.0f} | median s {statistics.median(t['seconds'] for t in w):.1f}")
