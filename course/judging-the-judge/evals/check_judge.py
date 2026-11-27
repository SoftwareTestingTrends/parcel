"""How well does the judge agree with you? Compares saved judge verdicts with your hand labels.
  uv run python evals/check_judge.py runs/heldout_judgements.jsonl heldout_labels.json
FAIL is the positive class: a true positive is a real failure the judge also failed.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent


def rates(verdicts, labels):
    tp = sum(labels[k] == "FAIL" and verdicts[k] == "FAIL" for k in labels)
    fn = sum(labels[k] == "FAIL" and verdicts[k] != "FAIL" for k in labels)
    tn = sum(labels[k] == "PASS" and verdicts[k] == "PASS" for k in labels)
    fp = sum(labels[k] == "PASS" and verdicts[k] != "PASS" for k in labels)
    return tp / (tp + fn), tn / (tn + fp), (tp, fn, tn, fp)


def corrected_fail_rate(judge_fail_rate, tpr, tnr):
    """The failure rate you'd see with a perfect judge, from the rate this judge reports."""
    return (judge_fail_rate + tnr - 1) / (tpr + tnr - 1)


if __name__ == "__main__":
    verdicts = {(r["case"], r["trial"]): r["verdict"] for r in map(json.loads, (HERE / sys.argv[1]).open())}
    labels = {(r["case"], r["trial"]): r["label"] for r in json.loads((HERE / sys.argv[2]).read_text())}
    tpr, tnr, (tp, fn, tn, fp) = rates(verdicts, labels)
    print(f"real failures caught (TPR): {tp} of {tp + fn} = {tpr:.0%}")
    print(f"real passes agreed (TNR):   {tn} of {tn + fp} = {tnr:.0%}")
    judge_fail = sum(v == "FAIL" for v in verdicts.values()) / len(verdicts)
    fixed = corrected_fail_rate(judge_fail, tpr, tnr)
    print(f"judge pass rate {1 - judge_fail:.1%}, corrected {1 - fixed:.1%}")
