# Course files: AI Evals Explained for Software Testers

Every run, grader, eval case and script behind the course, one folder per lesson, so you can check any number yourself or pick up a "Try it yourself" exercise.

Run a lesson's commands from its own folder. `uv run` finds Parcel's environment from there:

```bash
cd course/code-graders
uv run pytest evals/
```

The saved runs (`*.jsonl`) are the recorded conversations the lesson's numbers come from. Grading them needs no model and takes seconds. Recording new runs needs a model: Gemma 4 through Ollama, or Claude through the `api` backend.

| Lesson | Folder |
|---|---|
| Your test passed. Was the answer any good? | `your-test-passed/` |
| Just enough about language models | `just-enough-about-language-models/` |
| Meet Parcel, the support assistant | `meet-parcel/` |
| The anatomy of an eval | `anatomy-of-an-eval/` |
| Your first eval in ten minutes | `your-first-eval/` |
| Look at the outputs before you measure them | `look-before-you-measure/` |
| From failures to pass/fail criteria | `failures-to-criteria/` |
| Building an eval dataset | `building-the-dataset/` |
| Checks a script can make | `code-graders/` |
| When a model does the grading | `language-model-as-judge/` |
| Who checks the judge? | `judging-the-judge/` |
| Run it once, run it ten times | `run-it-more-than-once/` |
| Did it find the right article? | `retrieval-evals/` |
| Grounded or made up | `grounded-answers/` |
| Conversations, not single answers | `multi-turn/` |
| Grading what the agent did, not just what it said | `agent-actions/` |
| Trying to break it on purpose | `breaking-it-on-purpose/` |
| Moving the suite to DeepEval | `moving-to-deepeval/` |
| The same suite in promptfoo | `promptfoo-and-picking-a-tool/` (run promptfoo from its `promptfoo/` folder) |
| Evals as a release gate | `evals-as-a-gate/` |
| Evals don't stop at release | `evals-after-launch/` |
| Capstone: should we switch models? | `capstone-model-swap/` |

Some things to know:

- **Each lesson has its own copy of `graders.py` and `cases.json`,** as they stood in that lesson. Graders got fixes as the course went on, so a later lesson's copy can grade a few trials differently. The newest copy is in `capstone-model-swap/evals/`.
- **The judge scripts call Claude** through the Claude Code command line (`claude -p`) and count against your Claude plan. They don't ask for confirmation, so read a script before you run it on a whole set.
- **The capstone's Haiku runs used Parcel's `api` backend through OpenRouter.** To rerun them, set `OPENROUTER_API_KEY` (see `capstone-model-swap/evals/openrouter_env.py`), or set `ANTHROPIC_API_KEY` and `PARCEL_MODEL=claude-haiku-5-5` to call Anthropic directly.
- **Commit IDs in the recordings** (`parcel_commit`) are from before Parcel's history was rewritten on 26 November 2026, so some don't exist any more. The code they ran is unchanged: `a1a9440` is now `8a8ee1c`, `3c6f95e` is now `8fb7131`, `17e3350` is now `b8c3f4b`, `e42e346` is now `d6c45fe`.
- These scripts are teaching material, written to be read. They aren't part of Parcel's test suite or lint checks.
