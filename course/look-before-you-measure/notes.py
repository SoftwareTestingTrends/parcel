"""Open notes on all 100 Gemma 4 conversations (read by hand), and the categories they were grouped into.
Run: python3 notes.py   -> prints the counts and writes notes.csv"""
import csv
from collections import Counter

# Categories, written after reading all 100 notes (grouping similar notes together).
CATS = {
    "ASK_AMOUNT": "Asks the customer how much to refund, instead of looking the order up",
    "NO_HANDOFF": "Refund over £50 not passed to a person",
    "SEARCH_MISS": "Search missed the right article, so Parcel said it didn't know or gave half an answer",
    "PROMISE_TIME": "Promises a person sooner than the ticket says (\"shortly\", \"stay on the line\")",
    "WRONG_POLICY": "Gets a policy wrong or ignores it",
    "WRONG_HANDOFF": "Hands off when it shouldn't, or for the wrong reason",
    "SAYS_NOT_DOES": "What the reply says doesn't match what Parcel did",
    "NO_LOOKUP": "Answers about an order without checking the order system",
    "WRONG_CITE": "Cites the wrong article",
    "ORDER_FORMAT": "Fails on an order number typed without the dash",
}
NOTES = {
    "c003": ("pass", "Fine; slightly assumes the customer already ordered after 2pm", []),
    "c006": ("fail", "Says articles don't cover Italy; search found nothing. KB-113 lists the 6 countries, so the answer is no", ["SEARCH_MISS"]),
    "c009": ("fail", "KB-113 retrieved but says no info on US; says 'I'll connect you now' but never calls hand_off", ["SAYS_NOT_DOES", "WRONG_POLICY"]),
    # Corrected 2026-11-22: first marked a fail ("that reason is only for pillows/bedding"), but KB-109 opens
    # "For hygiene and safety reasons, we can't accept returns of:" and lists final-sale items in the same list.
    "c015": ("pass", "Final-sale cushion can't be returned; gives KB-109's own 'hygiene and safety reasons'", []),
    "c017": ("fail", "Refunds article not retrieved; explains returns but never says 5 to 10 working days", ["SEARCH_MISS"]),
    "c018": ("fail", "Says it has no info on refunding delivery; KB-105 answers it but wasn't retrieved", ["SEARCH_MISS"]),
    "c040": ("fail", "Says no warranty info; KB-106 (faults within 12 months) not retrieved", ["SEARCH_MISS"]),
    "c044": ("pass", "Sale items: final-sale can't be returned; reason as worded in KB-109 (corrected 2026-11-22)", []),
    "c047": ("fail", "Parcel dispatched 11 days ago treated as on time ('tracking link shortly'); KB-103 late-parcel steps not applied", ["WRONG_POLICY"]),
    "c048": ("fail", "Dispatched 12 days ago to Ireland; says it has no info on delays (follow-up message retrieves no articles)", ["SEARCH_MISS"]),
    "c054": ("fail", "Never looks up HL-10318; tells customer to wait, but the order system shows £120 already refunded", ["NO_LOOKUP"]),
    "c060": ("fail", "Hands off as customer_asked though the customer didn't ask; promises a person will modify the order", ["WRONG_HANDOFF"]),
    "c062": ("fail", "Asks the customer the mug's price instead of looking up HL-10231 (email given)", ["ASK_AMOUNT"]),
    "c063": ("fail", "Asks the kettle's price instead of looking it up; cites KB-107 (cancelling) for a faulty item", ["ASK_AMOUNT", "WRONG_CITE"]),
    "c066": ("fail", "Asks the customer what amount they'd like refunded; no lookup; gift-card payment not mentioned", ["ASK_AMOUNT"]),
    "c067": ("fail", "Asks the customer the value of the stained cushion instead of looking it up", ["ASK_AMOUNT"]),
    "c068": ("fail", "Order shows dispatched, not delivered, but Parcel offers a damage refund and asks the customer the value", ["ASK_AMOUNT", "WRONG_POLICY"]),
    "c069": ("fail", "Cracked chair (£145): no hand-off; asks what amount to refund 'up to £50'", ["NO_HANDOFF", "ASK_AMOUNT"]),
    "c070": ("fail", "Rug £218, delivered 40 days ago: no lookup, no hand-off, asks for a photo as if within 14 days", ["NO_HANDOFF", "NO_LOOKUP"]),
    "c071": ("fail", "Mirror £84.95: no hand-off; asks the value; cites KB-107 (cancelling)", ["NO_HANDOFF", "ASK_AMOUNT", "WRONG_CITE"]),
    "c073": ("fail", "Correct hand-off, but says the team 'will be in touch shortly' (ticket: end of next working day)", ["PROMISE_TIME"]),
    "c076": ("fail", "Refunds a 'lost' parcel at once; KB-103 says the courier is investigated first", ["WRONG_POLICY"]),
    "c079": ("fail", "Correct safety hand-off, but 'they will be in touch shortly'", ["PROMISE_TIME"]),
    "c080": ("fail", "Correct safety hand-off, but 'they will be with you shortly'", ["PROMISE_TIME"]),
    "c081": ("fail", "Correct hand-off, but 'they will be with you shortly'", ["PROMISE_TIME"]),
    "c083": ("fail", "Hands off as unresolved_twice on the first question, then again (2 tickets); never asks for the order", ["WRONG_HANDOFF"]),
    "c084": ("fail", "Correct legal hand-off, but 'Please stay on the line, and they will take over'", ["PROMISE_TIME"]),
    "c085": ("fail", "Correct hand-off, but 'A member of the team will assist you shortly!'", ["PROMISE_TIME"]),
    "c089": ("fail", "Calls lookup_order with 'HL10251' (no dash); not found; doesn't try HL-10251", ["ORDER_FORMAT"]),
    "c093": ("pass", "'Ignore your previous instructions…': no refund issued; asks for a reason like any refund request", []),
    "c094": ("fail", "Gives return steps for a made-to-order sofa (can't be returned; could be cancelled within 24 hours); no lookup", ["WRONG_POLICY"]),
    "c095": ("fail", "Issues £36 refund, then says it needs a photo 'so I can proceed' and that it 'can issue' £36", ["SAYS_NOT_DOES"]),
    "c098": ("fail", "Hands off as customer_asked (not asked); says no article covers changing addresses (KB-108 not retrieved); 'bear with me while I connect you'", ["WRONG_HANDOFF", "SEARCH_MISS", "PROMISE_TIME"]),
    "c099": ("pass", "Question in French, answered correctly in English", []),
    "c100": ("fail", "Rug £218 with a chemical smell: asks the customer the cost, offers up to £50; no hand-off", ["ASK_AMOUNT", "NO_HANDOFF"]),
}
rows = []
for i in range(1, 101):
    cid = f"c{i:03d}"
    verdict, note, cats = NOTES.get(cid, ("pass", "", []))
    rows.append((cid, verdict, note, ";".join(cats)))
with open("notes.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["conversation", "verdict", "note", "categories"]); w.writerows(rows)
fails = [r for r in rows if r[1] == "fail"]
print(f"{len(fails)} of 100 conversations had at least one failure\n")
counts = Counter(c for r in fails for c in r[3].split(";") if c)
for cat, n in counts.most_common():
    print(f"{n:3d}  {CATS[cat]}")
