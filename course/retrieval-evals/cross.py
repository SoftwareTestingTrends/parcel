"""Cross search results with what the answer did (error-analysis notes on the recorded Gemma 4 run, prompt v1).
Also checks that today's search returns exactly what Parcel retrieved in that run."""
import csv, json, sys
from pathlib import Path
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / "evals")); sys.path.insert(0, str(HERE))
from test_search import search, MESSAGES
from search_labels import LABELS

recorded = {}
for line in open(HERE / "runs/error_analysis_gemma4.jsonl"):
    t = json.loads(line); i = 0
    for e in t["events"]:
        if e["type"] == "customer": i += 1
        if e["type"] == "retrieval": recorded[(t["conversation"], i)] = [a["id"] for a in e["articles"]]
same = sum(recorded.get(k) == search(MESSAGES[k], 3) for k in LABELS)
print(f"today's search matches the recorded run on {same} of {len(LABELS)} labelled messages")

notes = {r["conversation"]: r for r in csv.DictReader(open(HERE / "notes.csv"))}
KNOWLEDGE = {"SEARCH_MISS", "WRONG_POLICY", "WRONG_CITE"}
quad = {}
for key, rel in LABELS.items():
    if not rel: continue
    found = rel <= set(search(MESSAGES[key], 3))   # found every article it needs
    cats = set(filter(None, notes[key[0]]["categories"].split(";")))
    bad = bool(cats & KNOWLEDGE)
    quad.setdefault((found, bad), []).append((key, sorted(cats & KNOWLEDGE), notes[key[0]]["note"][:100]))
names = {(True, False): "found all it needs, no knowledge failure", (True, True): "found all it needs, answer wrong -> answer problem",
         (False, True): "missed an article, answer wrong -> search problem", (False, False): "missed an article, no knowledge failure noted"}
for q in [(True, False), (True, True), (False, True), (False, False)]:
    print(f"\n{names[q]}: {len(quad.get(q, []))}")
    if q != (True, False):
        for key, c, n in quad.get(q, []): print(f"   {key[0]} msg {key[1]} {c} | {MESSAGES[key][:70]!r} | {n}")
