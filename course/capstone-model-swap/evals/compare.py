"""Capstone: Gemma 4 (local) vs Claude Haiku 5.5, all 39 cases × 3 trials, same graders as the gate."""
import json, statistics
from collections import defaultdict
import sys
from gate import load, problems
from parcel.pricing import estimate_cost

cases = {c["id"]: c for c in json.load(open("cases.json"))}
runs = {"gemma": load("runs/gemma_t1-3.jsonl")[0], "haiku": load("runs/haiku_api_t1-3.jsonl")[0]}

def by_case(rs):
    d = defaultdict(list)
    for t in rs:
        d[t["case"]].append(not problems(t))
    return d

def total_tokens(t):
    u = t["usage"]
    return sum(u.get(k, 0) for k in ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))

def cost(t):
    # OpenRouter runs record no cost; estimate at Anthropic's Haiku 5.5 list price (OpenRouter lists the same).
    if t["backend"] == "ollama":
        return 0.0
    return estimate_cost("claude-haiku-5-5", t["usage"]) or 0.0


res = {m: by_case(rs) for m, rs in runs.items()}
for m, rs in runs.items():
    d = res[m]
    trials = sum(len(v) for v in d.values()); passed = sum(sum(v) for v in d.values())
    gold = [c for c in cases if cases[c]["golden"]]
    print(f"{m}: trials passed {passed}/{trials} ({passed/trials:.0%}) | cases 3/3 {sum(all(v) for v in d.values())}/{len(d)}"
          f" | golden all-3 {sum(all(d[c]) for c in gold)}/{len(gold)}"
          f" | regression cases 3/3 {sum(all(d[c]) for c in cases if cases[c]['type']=='regression' and not cases[c]['golden'])}/{sum(1 for c in cases if cases[c]['type']=='regression' and not cases[c]['golden'])}"
          f" | capability trials {sum(sum(d[c]) for c in cases if cases[c]['type']=='capability')}/{3*sum(1 for c in cases if cases[c]['type']=='capability')}")
    print(f"   median s {statistics.median(t['seconds'] for t in rs):.1f}, p95 s {sorted(t['seconds'] for t in rs)[int(.95*len(rs))-1]:.1f},"
          f" median total tokens {statistics.median(map(total_tokens, rs)):.0f},"
          f" est. cost total ${sum(cost(t) for t in rs):.4f}, per conversation ${statistics.mean(cost(t) for t in rs):.5f}")
print("\ncase | type | golden | gemma | haiku")
for c in cases:
    g, h = sum(res["gemma"][c]), sum(res["haiku"][c])
    flag = "  <-- worse" if h < g else ("  better" if h > g else "")
    print(f"{c} | {cases[c]['type']} | {cases[c]['golden']} | {g}/3 | {h}/3{flag}")
