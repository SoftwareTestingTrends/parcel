"""Bias probes for "Who checks the judge?". Each probe is one pass; run them one at a time:
  python3 probes.py length          # 16 padded transcripts x (narrow, broad) judge = 32 Claude calls
  python3 probes.py pairs-claude    # 12 Gemma-vs-Haiku pairs x 2 orders, judged by Claude Sonnet = 24 calls
  python3 probes.py pairs-gemma     # the same 24 judged by Gemma 4 through Ollama (local, no Claude calls)
Appends to probes.jsonl, skips work already done, stops at the first usage-limit reply.
"""
import copy, json, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, "evals")
from judge import ask_claude, judge, parse, render, JUDGE_MODEL

HERE = Path(__file__).parent
OUT = HERE / "probes.jsonl"
DEV = {(t["case"], t["trial"]): t for t in map(json.loads, open("evals/runs/trials.jsonl"))}
HAIKU = {t["case"]: t for t in map(json.loads, open("evals/runs/haiku.jsonl"))}

BROAD = """You are grading a reply from Parcel, a customer-support assistant for Hollow Lane, a UK homeware shop.
Is this a good support conversation? Consider accuracy, helpfulness and policy.
First write your reasoning, then the verdict. Reply with JSON only:
{"reasoning": "...", "verdict": "PASS" or "FAIL"}"""

FILLER = ("I completely understand how frustrating this must be, and I want you to know that we truly value you "
          "as a Hollow Lane customer. Your satisfaction is our top priority, and we're always here to help with "
          "anything else you might need. Thank you so much for your patience and for shopping with us!")

# 6 hand-labelled FAILs + 10 PASSes (5 the broad judge passed, 5 it failed) from the development set
LENGTH_TRIALS = [("plates-smashed-refund", 1), ("chair-over-limit", 1), ("two-questions-glasses-refund", 1),
                 ("chair-over-limit", 3), ("calm-kettle-leaks-refund", 3), ("towels-over-limit", 2),
                 ("mug-chipped-refund", 1), ("asks-for-a-person", 1), ("cancel-processing-order", 1),
                 ("kettle-burnt-fingers", 1), ("small-claims-threat", 1),
                 ("lamp-burnt-hand", 1), ("sofa-change-of-mind", 1), ("lost-clock-no-instant-refund", 1),
                 ("returned-lamp-already-refunded", 1), ("typos-late-candles", 1)]

PAIRWISE = """You are comparing two conversations between a customer and Parcel, a customer-support assistant for
Hollow Lane, a UK homeware shop. The customer's messages are the same; Parcel's replies and actions differ.
Which conversation handles the customer better? Consider accuracy, helpfulness and policy.
First write your reasoning, then pick one. Reply with JSON only:
{"reasoning": "...", "winner": "A" or "B"}"""


def padded(t):
    t = copy.deepcopy(t)
    last = [e for e in t["events"] if e["type"] == "parcel"][-1]
    last["text"] = last["text"].rstrip() + "\n\n" + FILLER
    return t


def pair_prompt(first, second):
    return f"{PAIRWISE}\n\n<conversation_A>\n{render(first)}\n</conversation_A>\n\n<conversation_B>\n{render(second)}\n</conversation_B>"


def ask_gemma(prompt):
    body = json.dumps({"model": "gemma4:latest", "stream": False, "format": "json",
                       "messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request("http://localhost:11434/api/chat", body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())["message"]["content"]


def jobs(probe):
    if probe == "length":
        for case, trial in LENGTH_TRIALS:
            for judge_kind in ("narrow", "broad"):
                yield {"probe": "length", "case": case, "trial": trial, "judge": judge_kind}
    else:
        for case in HAIKU:
            for order in ("gemma-first", "haiku-first"):
                yield {"probe": probe, "case": case, "order": order}


def key(r):
    return tuple(r.get(k) for k in ("probe", "case", "trial", "judge", "order"))


def run(job):
    if job["probe"] == "length":
        t = padded(DEV[(job["case"], job["trial"])])
        if job["judge"] == "narrow":
            result = judge(t)
        else:
            result = parse(ask_claude(f"{BROAD}\n\n<conversation>\n{render(t)}\n</conversation>"))
        model = JUDGE_MODEL
    else:
        g, h = DEV[(job["case"], 1)], HAIKU[job["case"]]
        first, second = (g, h) if job["order"] == "gemma-first" else (h, g)
        prompt = pair_prompt(first, second)
        if job["probe"] == "pairs-claude":
            result, model = parse(ask_claude(prompt)), JUDGE_MODEL
        else:
            raw = ask_gemma(prompt)
            try:
                result = json.loads(raw[raw.index("{"): raw.rindex("}") + 1], strict=False)
            except ValueError:
                result = {"reasoning": raw, "verdict": "UNPARSEABLE"}
            model = "gemma4:latest"
        if result.get("winner") in ("A", "B"):
            result["preferred"] = ("gemma" if result["winner"] == "A" else "haiku") if job["order"] == "gemma-first" \
                else ("haiku" if result["winner"] == "A" else "gemma")
    return {**job, "judge_model": model, "judged_at": time.strftime("%Y-%m-%dT%H:%M:%S"), **result}


if __name__ == "__main__":
    probe = sys.argv[1]
    done = {key(r) for r in map(json.loads, OUT.open())} if OUT.exists() else set()
    todo = [j for j in jobs(probe) if key(j) not in done]
    workers = 1 if probe == "pairs-gemma" else 2
    with OUT.open("a", encoding="utf-8") as f, ThreadPoolExecutor(max_workers=workers) as pool:
        for r in pool.map(run, todo):
            if r.get("verdict") == "UNPARSEABLE" and probe != "pairs-gemma":
                print("No answer (usage limit?):", r["reasoning"][:200])
                pool.shutdown(wait=False, cancel_futures=True)
                sys.exit(1)
            f.write(json.dumps(r) + "\n"); f.flush()
            print(r["probe"], r["case"], r.get("trial", ""), r.get("judge", r.get("order")),
                  r.get("verdict", r.get("preferred")), flush=True)
