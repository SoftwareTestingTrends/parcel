"""Drift: the same cheap signals, split into week 1, week 2 without Christmas, and week 2's Christmas questions."""
import json, statistics, sys
sys.path.insert(0, "evals")
from live_checks import no_articles, top_score, says_dont_know, handed_off, tokens
traces = [json.loads(l) for l in open("runs/live.jsonl")]
xmas = {f"w{n}" for n in range(246, 276)}
groups = {"week 1": [t for t in traces if t["week"] == "week 1"],
          "week 2, usual": [t for t in traces if t["week"] == "week 2" and t["conversation"] not in xmas],
          "week 2, Christmas": [t for t in traces if t["conversation"] in xmas],
          "week 2, all": [t for t in traces if t["week"] == "week 2"]}
for name, g in groups.items():
    n = len(g); dk = sum(map(says_dont_know, g)); na = sum(map(no_articles, g)); ho = sum(map(handed_off, g))
    print(f"{name:18} n={n:3} | says it doesn't know {dk:2} ({dk/n:4.0%}) | no article found {na:2} ({na/n:3.0%})"
          f" | median top score {statistics.median(map(top_score, g)):.2f} | handed off {ho} ({ho/n:.0%})"
          f" | median tokens {statistics.median(map(tokens, g)):.0f}")
