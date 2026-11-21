# Parcel

Parcel is the customer support assistant for **Hollow Lane**, a fictional online homeware shop in the UK. It's the running example for the course *AI Evals Explained for Software Testers* on [softwaretestingtrends.com](https://softwaretestingtrends.com).

It's small on purpose, but it has the three parts that make AI features hard to test:

- **Retrieval.** It answers policy questions from 14 help-centre articles (`src/parcel/data/help_centre/`) and cites them like `[KB-105]`.
- **Tools.** It can look up an order, issue a refund and hand the customer off to a person (`src/parcel/tools.py`), against 20 seeded orders (`src/parcel/data/orders.json`).
- **Rules.** It may refund up to **£50** per order. Anything more, plus safety problems, legal complaints and customers who ask for a person, must be handed off (`src/parcel/policy.py`, `src/parcel/prompts.py`).

Hollow Lane and its customers are made up. Every email address uses `example.com`.

## Quick start

You need [uv](https://docs.astral.sh/uv/).

```bash
make install
make test                              # offline, no model needed
uv run parcel ask "Do you deliver to Spain?"
uv run parcel chat
```

## Choosing a model

Parcel can reach a model in four ways. Pick one with `PARCEL_BACKEND` (or `--backend`):

| Backend | What it uses | Needs | Notes |
|---|---|---|---|
| `mock` (default) | keyword rules, no model | nothing | Same answer every time. For tests and trying the app. |
| `ollama` | a local model, default `gemma4:latest` | [Ollama](https://ollama.com) running, model pulled | Free. The only backend where you can set `--temperature` and `--seed`. |
| `claude-code` | Claude, through your Claude Code login | Claude Code installed and logged in | No API key. Uses your Claude plan's limits. |
| `api` | Claude, through the Anthropic API | `ANTHROPIC_API_KEY` | Pay per token. What most teams use in production. |

```bash
uv run parcel --backend ollama ask "Can I return a pillow?"
uv run parcel --backend claude-code --model claude-haiku-5-5 chat
PARCEL_BACKEND=api PARCEL_MODEL=claude-sonnet-5-5 uv run parcel chat
```

A conversation can have several messages: `parcel ask "first message" "second message"`. Add `--json` to see the whole transcript.

## Traces

Every conversation is saved as one line of JSON in `traces/<date>.jsonl` (turn this off with `--no-trace`). A trace holds:

- what the customer said
- which articles were retrieved, with their scores
- every tool call, with its arguments and result
- what Parcel replied
- tokens used, estimated cost and time taken
- the **end state**: refunds issued and hand-offs made

Evals read traces. They don't need to know which backend produced them.

## Settings

| Variable | Default | Meaning |
|---|---|---|
| `PARCEL_BACKEND` | `mock` | `mock`, `ollama`, `claude-code` or `api` |
| `PARCEL_MODEL` | `gemma4:latest` for ollama, `claude-haiku-5-5` for claude-code and api | any Ollama model or Claude model id |
| `PARCEL_TEMPERATURE`, `PARCEL_SEED` | model default | Ollama only. Current Claude models don't accept a temperature. |
| `PARCEL_EFFORT` | model default | Claude only: `low`, `medium` or `high` |
| `PARCEL_REFUND_GUARD` | `on` | `off` removes the £50 check inside the refund tool, so only the prompt keeps Parcel in line |
| `PARCEL_TRACE_DIR` | `traces` | where traces are written |
| `OLLAMA_HOST` | `http://localhost:11434` | where Ollama listens |

## Known weaknesses (kept on purpose)

Parcel is meant to fail in realistic ways, so the course has real failures to find. Don't fix these without checking the course first:

- Retrieval is plain keyword search (BM25). "How long does a refund take?" ranks the returns article first, because it contains "as long as". "When will I get my money back?" misses the refunds article entirely.
- Retrieval only looks at the latest message. A follow-up like "it's dev.patel@example.com" retrieves nothing.
- The £50-per-order refund limit is enforced in the refund tool, but the hand-off rules live only in the prompt.

## Layout

```
src/parcel/
  assistant.py    Parcel: one conversation, records the transcript
  backends/       mock, ollama, claude_code, api
  knowledge.py    help-centre articles and BM25 search
  orders.py       seeded order system and the refund rules
  tools.py        tool definitions shared by every backend
  prompts.py      the system prompt (PROMPT_VERSION)
  policy.py       the numbers: refund limit, return window, hand-off reasons
  transcript.py   the trace format
tests/            offline tests (mock backend)
```

## Licence

MIT
