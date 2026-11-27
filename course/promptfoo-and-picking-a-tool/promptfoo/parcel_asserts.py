"""Our code graders as promptfoo Python assertions. Each returns pass, score and the reason."""
import json

from graders import BY_EXPECT_KEY, EVERY_TRIAL


def _result(problems):
    return {"pass": not problems, "score": 0 if problems else 1, "reason": "; ".join(problems) or "no problems"}


def expected_result(output, context):
    t = context["providerResponse"]["metadata"]["transcript"]
    expect = json.loads(context["vars"]["expect"])
    return _result([p for k, v in expect.items() for p in BY_EXPECT_KEY[k](t, v)])


def every_turn_checks(output, context):
    t = context["providerResponse"]["metadata"]["transcript"]
    return _result([p for grader in EVERY_TRIAL for p in grader(t)])
