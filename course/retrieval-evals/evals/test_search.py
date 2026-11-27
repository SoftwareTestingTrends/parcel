"""Evaluate Parcel's search on its own: no model, no conversation, just the search.
  uv run python evals/test_search.py
For every labelled message: run the search, compare the top k articles with the labels."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from parcel.knowledge import default_help_centre

from conversations import CONVERSATIONS
from search_labels import LABELS

MESSAGES = {(cid, i): text for cid, msgs in CONVERSATIONS for i, text in enumerate(msgs, 1)}


def search(message, k):
    return [hit.article.id for hit in default_help_centre().search(message, k=k)]


def recall_at_k(found, relevant):     # of the articles that answer it, how many came back?
    return len(set(found) & relevant) / len(relevant)


def precision_at_k(found, relevant):  # of the articles that came back, how many answer it?
    return len(set(found) & relevant) / len(found) if found else 0.0


def report(k=3):
    answerable = {key: rel for key, rel in LABELS.items() if rel}
    rows = []
    for key, relevant in answerable.items():
        found = search(MESSAGES[key], k)
        rows.append((key, found, relevant, recall_at_k(found, relevant), precision_at_k(found, relevant)))
    n = len(rows)
    print(f"k={k}: {n} questions the help centre answers")
    print(f"  recall@{k}:    {sum(r[3] for r in rows) / n:.0%}")
    print(f"  precision@{k}: {sum(r[4] for r in rows) / n:.0%}")
    print(f"  found every article needed: {sum(r[3] == 1 for r in rows)} of {n}")
    print(f"  found none of them:         {sum(r[3] == 0 for r in rows)} of {n}")
    return rows


if __name__ == "__main__":
    rows = report(3)
    print("\nmissed (no article that answers it in the top 3):")
    for (cid, i), found, relevant, rec, _ in rows:
        if rec == 0:
            print(f"  {cid} msg {i}: {MESSAGES[(cid, i)]!r}\n      wanted {sorted(relevant)}, got {found}")
    unanswerable = [key for key, rel in LABELS.items() if not rel]
    got = sum(bool(search(MESSAGES[key], 3)) for key in unanswerable)
    print(f"\nquestions no article answers: {len(unanswerable)}; search still returned articles for {got}")
