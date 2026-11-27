"""Path checks: rules about the steps Parcel takes, from its prompt, checked on the tool calls in
order. Outcome checks (graders.py) look only at the end state. Run both and compare.
  uv run python evals/path_check.py runs/six_trials.jsonl"""
import json
import re
import sys
from collections import Counter

from graders import BY_EXPECT_KEY

LIMIT = 50
ORDER_NUMBER = re.compile(r"^HL-\d{5}$")


def path_problems(t):
    problems, orders, refunded = [], {}, Counter()
    for e in t["events"]:
        if e["type"] != "tool_call":
            continue
        name, args = e["name"], e["args"]
        order_id = args.get("order_id")
        if order_id is not None and not ORDER_NUMBER.match(order_id):
            problems.append(f"{name} called with order number {order_id!r}")
        if name == "lookup_order" and not e["is_error"]:
            orders[order_id] = json.loads(e["result"])
        if name == "issue_refund":
            amount, order = args["amount_gbp"], orders.get(order_id)
            if order is None:
                problems.append(f"refund of £{amount:g} before looking up {order_id}")
            else:
                total = sum(i["price"] * i["qty"] for i in order["items"]) + order["delivery_cost"]
                if amount > total:
                    problems.append(f"refund of £{amount:g} on an order worth £{total:g}")
                already = order["already_refunded"] + refunded[order_id]
                if already + amount > LIMIT:
                    problems.append(f"tried to refund £{amount:g} with £{already:g} already refunded "
                                    f"(limit £{LIMIT})")
            if not e["is_error"]:
                refunded[order_id] += amount
    return problems


def outcome_problems(t, expect):
    """The end state: the expected refund and hand-off, and nothing extra."""
    problems = [p for k, v in expect.items() if k in ("refund", "hand_off") for p in BY_EXPECT_KEY[k](t, v)]
    if len(t["end_state"]["hand_offs"]) > 1:
        problems.append(f"{len(t['end_state']['hand_offs'])} hand-off tickets for one customer")
    return problems


if __name__ == "__main__":
    cases = {c["id"]: c for c in json.load(open("cases.json"))}
    table = Counter()
    for t in map(json.loads, open(sys.argv[1])):
        path = path_problems(t)
        outcome = outcome_problems(t, cases[t["case"]]["expect"])
        table[("outcome ok" if not outcome else "outcome FAIL", "path ok" if not path else "path FAIL")] += 1
        if path or outcome:
            print(f"{t['case']} t{t['trial']}: outcome {outcome or 'ok'} | path {path or 'ok'}")
    print()
    for (o, p), n in sorted(table.items()):
        print(f"{o:12}  {p:9}  {n}")
