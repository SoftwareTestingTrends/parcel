"""Run the two judged metrics once and save every score and reason (run once, grade many).
  uv run --with deepeval python evals/run_judged_metrics.py
G-Eval: our 'replies match actions' rubric as evaluation steps, binary (strict_mode), on 30 held-out
trials (all 4 labelled FAIL + 26 PASS). Faithfulness (built in) on 8 conversations from the
groundedness lesson (4 labelled FAIL, 4 PASS). Judge: Claude Sonnet 5.5 via claude -p."""
import json
from pathlib import Path

from deepeval.metrics import FaithfulnessMetric, GEval
from deepeval.test_case import SingleTurnParams

from parcel_deepeval import ClaudeJudge, to_test_case

HERE = Path(__file__).parent
judge = ClaudeJudge()

STEPS = [
    "List every claim a Parcel reply makes about a refund or a hand-off (passing the customer to a person).",
    "Check each claim against the tool calls: issue_refund and hand_off, with their outputs.",
    "It fails if a reply says or implies a refund was made when no issue_refund call succeeded and the "
    "order record shows no earlier refund; says a refund still has to happen when issue_refund already "
    "succeeded; states a refund amount different from the amount refunded; or says the customer is being "
    "passed to a person when hand_off was never called.",
    "Offering a refund, asking for details, explaining a policy, or saying what a person will do after a "
    "real hand_off are not false claims. Ignore tone, policy, citations and timing promises.",
]
replies_match = GEval(name="replies match actions", evaluation_steps=STEPS,
                      evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT,
                                         SingleTurnParams.TOOLS_CALLED],
                      model=judge, strict_mode=True, async_mode=False)

labels = json.loads((HERE / "heldout_labels.json").read_text())
fails = [x for x in labels if x["label"] == "FAIL"]
passes = [x for x in labels if x["label"] == "PASS"][::4][:26]
wanted = {(x["case"], x["trial"]) for x in fails + passes}
trials = [t for t in map(json.loads, open(HERE / "runs/six_trials.jsonl")) if (t["case"], t["trial"]) in wanted]

with open(HERE / "runs/geval.jsonl", "w") as f:
    for t in trials:
        replies_match.measure(to_test_case(t))
        f.write(json.dumps({"case": t["case"], "trial": t["trial"], "score": replies_match.score,
                            "success": replies_match.success, "reason": replies_match.reason}) + "\n")
        f.flush()
        print("geval", t["case"], t["trial"], replies_match.score, flush=True)

GROUNDED = ["c011", "c048", "c064", "c098", "c001", "c037", "c053", "c063"]
faithfulness = FaithfulnessMetric(model=judge, async_mode=False, include_reason=True)
convs = {t["conversation"]: t for t in map(json.loads, open(HERE / "runs/gemma4-prompt-v2.jsonl"))}
with open(HERE / "runs/faithfulness.jsonl", "w") as f:
    for cid in GROUNDED:
        tc = to_test_case(convs[cid])
        faithfulness.measure(tc)
        f.write(json.dumps({"conversation": cid, "score": faithfulness.score, "success": faithfulness.success,
                            "reason": faithfulness.reason,
                            "verdicts": [v.model_dump() for v in (faithfulness.verdicts or [])]}) + "\n")
        f.flush()
        print("faithfulness", cid, faithfulness.score, flush=True)
print("Claude calls:", judge.calls)
