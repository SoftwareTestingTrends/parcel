"""Summarise runs/temperature.jsonl and runs/next_token.json for the lesson. Run: python3 analyze.py"""
import json, collections
reply = lambda r: [e for e in r["events"] if e.get("type") == "parcel"][-1]["text"]
by = collections.defaultdict(list)
for line in open("runs/temperature.jsonl"):
    r = json.loads(line); by[r["condition"]].append(r)
for c, rs in by.items():
    texts = [reply(r) for r in rs]
    print(f"== {c}: {len(set(texts))} distinct of {len(rs)}; with £9.95: {sum('£9.95' in t for t in texts)};"
          f" with '5 to 8': {sum('5 to 8' in t for t in texts)}; input tokens {sorted({r['usage']['input_tokens'] for r in rs})};"
          f" output tokens {[r['usage']['output_tokens'] for r in rs]}")
    for t in sorted(set(texts)): print("   >>", t.replace("\n", " "))
d = json.load(open("runs/next_token.json"))
print(f"\n== next-token probe (temperature 0, thinking off): input {d['input_tokens']} tokens, output {d['output_tokens']}")
print("reply:", d["reply"])
for i, s in enumerate(d["steps"]):
    if s["probability"] < 0.8:
        alts = ", ".join(f"{a['token']!r} {a['probability']:.2f}" for a in s["alternatives"])
        print(f"step {i}: picked {s['picked']!r} {s['probability']:.2f} | {alts}")
print("tokens:", " | ".join(repr(s["picked"]) for s in d["steps"]))
