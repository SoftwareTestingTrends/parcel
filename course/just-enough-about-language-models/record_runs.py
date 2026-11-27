"""Lesson: Just enough about language models.

Records the real runs this lesson's numbers come from, all on Gemma 4 through Ollama
(the only Parcel backend where temperature and seed can be set):

1. runs/temperature.jsonl  Parcel answers "Do you deliver to Spain?" under three settings:
                           temperature 0 (x5), temperature 1 (x5), temperature 1 with seed 42 (x3).
2. runs/next_token.json    one reply to the same question with Parcel's real system prompt and
                           articles, recording every token Gemma picked and its top 5 alternatives.

Run from this folder:
  uv run python record_runs.py
"""

import json
import math
import subprocess
import time
import urllib.request
from pathlib import Path

from parcel import __version__
from parcel.assistant import Parcel
from parcel.config import Settings
from parcel.knowledge import HelpCentre
from parcel.prompts import SYSTEM_PROMPT, with_articles

QUESTION = "Do you deliver to Spain?"
CONDITIONS = [
    ("temperature-0", {"temperature": 0.0}, 5),
    ("temperature-1", {"temperature": 1.0}, 5),
    ("temperature-1-seed-42", {"temperature": 1.0, "seed": 42}, 3),
]

parcel_repo = Path(__file__).resolve().parents[2]
commit = subprocess.run(
    ["git", "-C", str(parcel_repo), "rev-parse", "--short", "HEAD"], capture_output=True, text=True
).stdout.strip()
runs = Path("runs")
runs.mkdir(exist_ok=True)

# 1. The same question under different temperature settings, through Parcel itself.
with (runs / "temperature.jsonl").open("a", encoding="utf-8") as f:
    for name, overrides, repeats in CONDITIONS:
        for i in range(1, repeats + 1):
            parcel = Parcel(Settings.from_env(backend="ollama", trace_dir="runs/traces", **overrides))
            parcel.ask(QUESTION)
            record = {
                "condition": name,
                "settings": overrides,
                "repeat": i,
                "parcel_version": __version__,
                "parcel_commit": commit,
                "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                **parcel.transcript.to_dict(),
            }
            f.write(json.dumps(record) + "\n")
            f.flush()
            print(name, i, "|", parcel.transcript.final_reply[:100])

# 2. Next-token choices for one reply, with Parcel's real prompt and retrieved articles.
hits = HelpCentre().search(QUESTION, k=3)
body = {
    "model": "gemma4:latest",
    "messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": with_articles(QUESTION, hits)},
    ],
    "stream": False,
    "think": False,
    "logprobs": True,
    "top_logprobs": 5,
    "options": {"temperature": 0, "num_predict": 80},
}
request = urllib.request.Request(
    "http://localhost:11434/api/chat", data=json.dumps(body).encode(),
    headers={"Content-Type": "application/json"},
)
with urllib.request.urlopen(request, timeout=600) as response:
    data = json.loads(response.read())
steps = [
    {
        "picked": step["token"],
        "probability": round(math.exp(step["logprob"]), 4),
        "alternatives": [
            {"token": alt["token"], "probability": round(math.exp(alt["logprob"]), 4)}
            for alt in step["top_logprobs"]
        ],
    }
    for step in data["logprobs"]
]
(runs / "next_token.json").write_text(json.dumps({
    "question": QUESTION,
    "articles": [h.article.id for h in hits],
    "reply": data["message"]["content"],
    "input_tokens": data.get("prompt_eval_count"),
    "output_tokens": data.get("eval_count"),
    "parcel_commit": commit,
    "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    "steps": steps,
}, indent=1, ensure_ascii=False))
print("next-token probe:", data["message"]["content"][:120])
