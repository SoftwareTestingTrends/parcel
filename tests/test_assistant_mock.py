"""The whole app end to end, with the offline mock in place of a model."""

import json

from parcel.assistant import Parcel
from parcel.cli import main
from parcel.config import Settings

MOCK = Settings(backend="mock")


def test_policy_question_is_answered_from_an_article():
    parcel = Parcel(MOCK)
    reply = parcel.ask("Do you deliver to Spain?")
    assert "[KB-113]" in reply
    assert parcel.transcript.retrieved_ids[0][0] == "KB-113"


def test_order_lookup_over_two_turns():
    parcel = Parcel(MOCK)
    assert "email" in parcel.ask("Where is order HL-10240?")
    assert "dispatched" in parcel.ask("It's ben.walker@example.com")
    assert [c["name"] for c in parcel.transcript.tool_calls] == ["lookup_order"]


def test_small_damage_refund_is_issued():
    parcel = Parcel(MOCK)
    parcel.ask("My order HL-10251 arrived broken, email dev.patel@example.com")
    assert parcel.transcript.end_state["refunds"][0]["amount_gbp"] == 39.95


def test_large_damage_refund_is_handed_off():
    parcel = Parcel(MOCK)
    parcel.ask("Order HL-10252 arrived damaged. dev.patel@example.com")
    state = parcel.transcript.end_state
    assert state["refunds"] == []
    assert state["hand_offs"][0]["reason"] == "refund_over_limit"


def test_safety_problem_is_handed_off():
    parcel = Parcel(MOCK)
    parcel.ask("The heater I bought caught fire!")
    assert parcel.transcript.end_state["hand_offs"][0]["reason"] == "safety_or_legal"


def test_transcript_records_backend_prompt_and_events():
    parcel = Parcel(MOCK)
    parcel.ask("Do you price match?")
    data = parcel.transcript.to_dict()
    assert data["backend"] == "mock" and data["prompt_version"] == "v2"
    assert [e["type"] for e in data["events"]] == ["customer", "retrieval", "parcel"]


def test_cli_ask_json(capsys):
    assert main(["--backend", "mock", "--no-trace", "ask", "--json", "Do you price match?"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["events"][-1]["type"] == "parcel"
