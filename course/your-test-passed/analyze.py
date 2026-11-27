"""Summarise the recorded runs for the lesson. Writes analysis.txt.

    python3 analyze.py
"""

import json
from collections import defaultdict
from pathlib import Path

CHECKS = {  # a plain "contains" check for each conversation, as a tester might first write it
    "spain": lambda r: "£9.95" in r["final"] and "5 to 8" in r["final"],
    "refund-time": lambda r: "5 to 10" in r["final"],
    "money-back": lambda r: "5 to 10" in r["final"],
    "cracked-chair": lambda r: any(h["reason"] == "refund_over_limit" for h in r["hand_offs"])
    and not r["refunds"],
}
CHECK_TEXT = {
    "spain": 'reply contains "£9.95" and "5 to 8"',
    "refund-time": 'reply contains "5 to 10"',
    "money-back": 'reply contains "5 to 10"',
    "cracked-chair": "handed off as refund_over_limit and issued no refund (end state)",
}

out = []
for path in sorted(Path("runs").glob("*.jsonl")):
    groups = defaultdict(list)
    for line in path.open(encoding="utf-8"):
        rec = json.loads(line)
        groups[rec["conversation"]].append(
            {
                "repeat": rec["repeat"],
                "model": rec["model"],
                "final": rec["events"][-1]["text"],
                "seconds": rec["seconds"],
                "cost": rec["cost_usd"] or 0,
                "tokens_out": rec["usage"].get("output_tokens", 0),
                "tools": [e["name"] for e in rec["events"] if e["type"] == "tool_call"],
                "retrieved": [
                    [a["id"] for a in e["articles"]] for e in rec["events"] if e["type"] == "retrieval"
                ],
                "hand_offs": rec["end_state"]["hand_offs"],
                "refunds": rec["end_state"]["refunds"],
                "commit": rec["parcel_commit"],
            }
        )
    for name, runs in groups.items():
        runs.sort(key=lambda r: r["repeat"])
        first = runs[0]["final"]
        exact = sum(r["final"] == first for r in runs)
        contains = sum(CHECKS[name](r) for r in runs)
        lengths = [len(r["final"].split()) for r in runs]
        out.append(f"== {path.stem} / {runs[0]['model']} / {name}  (parcel {runs[0]['commit']})")
        out.append(f"   runs: {len(runs)}")
        out.append(f"   distinct final replies: {len({r['final'] for r in runs})}")
        out.append(f"   exact match with run 1: {exact}/{len(runs)} (run 1 always matches itself)")
        out.append(f"   contains check [{CHECK_TEXT[name]}]: {contains}/{len(runs)}")
        out.append(f"   reply length in words: {min(lengths)}-{max(lengths)}")
        out.append(f"   retrieved (per turn): {runs[0]['retrieved']}")
        out.append(f"   tool calls per run: {[r['tools'] for r in runs]}")
        out.append(
            f"   seconds: {min(r['seconds'] for r in runs):.1f}-{max(r['seconds'] for r in runs):.1f};"
            f" total est. cost ${sum(r['cost'] for r in runs):.4f}"
        )
        for r in runs:
            out.append(f"   [{r['repeat']}] {r['final']}".replace("\n", " / "))
        out.append("")
Path("analysis.txt").write_text("\n".join(out), encoding="utf-8")
print("\n".join(line for line in out if not line.startswith("   [")))
