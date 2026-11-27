"""Lesson: Meet Parcel. Records the terminal output the lesson shows, all offline (mock backend
and direct calls into Parcel's code), so anyone can reproduce it without a model.

Run from this folder:  uv run python record_terminal.py
"""
import json, subprocess
from pathlib import Path
from parcel.knowledge import HelpCentre
from parcel.orders import OrderStore
from parcel.tools import run_tool

REPO = Path(__file__).resolve().parents[2]
OUT = Path("terminal"); OUT.mkdir(exist_ok=True)

def sh(name, cmd):
    r = subprocess.run(cmd, cwd=REPO, shell=True, capture_output=True, text=True)
    (OUT / f"{name}.txt").write_text(f"$ {cmd}\n{r.stdout}{r.stderr}")
    print(f"== {name}\n$ {cmd}\n{(r.stdout + r.stderr)[-1500:]}")

sh("make-test", "make test")
sh("ask-mock", 'uv run parcel --no-trace ask "Do you deliver to Spain?"')

hc = HelpCentre()
lines = [f"{len(hc.articles)} articles: " + ", ".join(f"{a.id} {a.title}" for a in hc.articles)]
for q in ["How long does a refund take?", "When will I get my money back?", "Do you deliver to Spain?"]:
    lines.append(f"\nsearch({q!r}):")
    lines += [f"  {h.article.id}  {h.score:5.2f}  {h.article.title}" for h in hc.search(q, k=3)]
(OUT / "search.txt").write_text("\n".join(lines)); print("\n".join(lines))

store = OrderStore.seeded()
calls = [
    ("lookup_order", {"order_id": "HL-10252", "email": "someone@example.com"}),
    ("lookup_order", {"order_id": "HL-10252", "email": "dev.patel@example.com"}),
    ("issue_refund", {"order_id": "HL-10252", "email": "dev.patel@example.com", "amount_gbp": 60, "reason": "damaged_or_faulty"}),
    ("hand_off", {"reason": "refund_over_limit", "summary": "Cracked chair leg on HL-10252; refund over £50."}),
]
out = []
for name, args in calls:
    result, err = run_tool(store, name, args)
    out.append(f"{name}({json.dumps(args)})\n  -> {'ERROR ' if err else ''}{result}")
unguarded = OrderStore.seeded(refund_guard=False)
result, err = run_tool(unguarded, "issue_refund", calls[2][1])
out.append(f"[PARCEL_REFUND_GUARD=off] issue_refund({json.dumps(calls[2][1])})\n  -> {'ERROR ' if err else ''}{result}")
out.append(f"end state (guarded store): refunds={store.refunds} hand_offs={[h['ticket_id'] for h in store.hand_offs]}")
(OUT / "tools.txt").write_text("\n".join(out)); print("\n".join(out))
