"""Writes heldout_review.txt: for each held-out trial, the tool calls (with refund amounts, hand-off reasons and
any earlier refund) and every reply sentence that mentions a refund, money, a person, a team or a hand-off.
Read it by hand to label each trial for the judge's one question; replies are cut to those sentences."""
import json, re

WORDS = re.compile(r"refund|£|person|team|pass|connect|hand|transfer|escalat|colleague|issu|process|money|"
                   r"credit|reimburs|sent|on its way|ticket|someone", re.I)
with open("heldout_review.txt", "w") as out:
    for t in map(json.loads, open("evals/runs/heldout.jsonl")):
        tools, prior = [], "-"
        for e in t["events"]:
            if e["type"] == "tool_call":
                name = e["name"] + ("(ERROR)" if e["is_error"] else "")
                if e["name"] == "issue_refund" and not e["is_error"]:
                    name += f"£{e['args'].get('amount_gbp')}"
                if e["name"] == "hand_off" and not e["is_error"]:
                    name += f"[{e['args'].get('reason')}]"
                if e["name"] == "lookup_order" and not e["is_error"]:
                    prior = json.loads(e["result"]).get("already_refunded")
                tools.append(name)
        out.write(f"##### {t['case']} t{t['trial']} | tools: {', '.join(tools) or '-'} | prior refund: {prior}\n")
        for e in t["events"]:
            if e["type"] == "tool_call":
                out.write(f"   >> {e['name']}\n")
            elif e["type"] == "parcel":
                hits = [s for s in re.split(r"(?<=[.!?])\s+", e["text"].replace("\n", " ")) if WORDS.search(s)]
                out.write("   P: " + (" ".join(hits) if hits else "(no refund/person sentence)") + "\n")
