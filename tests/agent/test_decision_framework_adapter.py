"""Decision Framework adapter tests."""

from __future__ import annotations

import copy
import subprocess
from dataclasses import asdict

from agent.decision_framework import DecisionFrameworkOutput
from agent.decision_framework_adapter import build_decision_support_context
import agent.decision_framework_adapter as adapter


FORBIDDEN_DECISION_LANGUAGE = (
    "final decision:",
    "recommendation",
    "i recommend",
    "you should",
)

DOMAIN_SPECIFIC_TERMS = (
    "investment",
    "finance",
    "career",
    "health",
    "business",
    "domain model",
    "decision style",
)

ALLOWED_INPUT_FIELDS = {
    "identity",
    "energy",
    "habit",
    "growth",
    "communication",
    "coaching",
}


def test_none_empty_and_incomplete_inputs_return_fenced_context():
    for human_model_snapshot in (None, {}, {"identity": {"name": "user"}}):
        context = build_decision_support_context(human_model_snapshot)

        assert context.startswith("<decision_support_context>\n")
        assert context.endswith("\n</decision_support_context>")
        assert "This is decision support context, not a final decision." in context
        assert "The user remains responsible for the decision." in context
        assert "Perspective:" in context
        assert "Decision Synthesis:" in context
        assert "Next Step:" in context
        assert "Review Point:" in context


def test_adapter_does_not_add_final_decision_or_recommendation_language():
    context = build_decision_support_context({})
    lowered = context.lower()

    for forbidden in FORBIDDEN_DECISION_LANGUAGE:
        assert forbidden not in lowered


def test_adapter_does_not_invent_domain_specific_terms():
    context = build_decision_support_context({})
    lowered = context.lower()

    for term in DOMAIN_SPECIFIC_TERMS:
        assert term not in lowered


def test_decision_style_is_not_required_and_is_ignored(monkeypatch):
    captured = {}

    def fake_run(input_data):
        captured["input"] = input_data
        return DecisionFrameworkOutput()

    monkeypatch.setattr(adapter, "run_decision_framework", fake_run)

    build_decision_support_context({"decision_style": {"mode": "fast"}})

    assert asdict(captured["input"]) == {
        "identity": {},
        "energy": {},
        "habit": {},
        "growth": {},
        "communication": {},
        "coaching": {},
    }


def test_unknown_keys_do_not_enter_decision_framework_input(monkeypatch):
    captured = {}

    def fake_run(input_data):
        captured["input"] = input_data
        return DecisionFrameworkOutput()

    monkeypatch.setattr(adapter, "run_decision_framework", fake_run)

    build_decision_support_context(
        {
            "identity": {"values": ["autonomy"]},
            "energy": {"level": "low"},
            "habit": {"shape": "small-step"},
            "growth": {"direction": "iterative"},
            "communication": {"style": "concise"},
            "coaching": {"stance": "supportive"},
            "unknown_key": {"ignored": True},
            "decision_style": {"ignored": True},
        },
        turn_context={"message": "current turn is accepted but not mapped yet"},
    )

    input_data = asdict(captured["input"])
    assert set(input_data) == ALLOWED_INPUT_FIELDS
    assert input_data["identity"] == {"values": ["autonomy"]}
    assert "unknown_key" not in input_data
    assert "decision_style" not in input_data


def test_input_dicts_are_not_mutated():
    human_model_snapshot = {
        "identity": {"values": ["autonomy"]},
        "unknown_key": {"keep": True},
    }
    turn_context = {"message": {"text": "hello"}}
    original_human_model_snapshot = copy.deepcopy(human_model_snapshot)
    original_turn_context = copy.deepcopy(turn_context)

    build_decision_support_context(human_model_snapshot, turn_context=turn_context)

    assert human_model_snapshot == original_human_model_snapshot
    assert turn_context == original_turn_context


def test_fenced_context_formats_decision_framework_output(monkeypatch):
    def fake_run(input_data):
        return DecisionFrameworkOutput(
            perspective="Pause and compare the available paths.",
            decision_synthesis={
                "options": ["Option A", "Option B"],
                "tradeoffs": ["Speed vs confidence"],
                "constraints": ["Limited energy"],
                "unknowns": ["External timing"],
            },
            next_step="List one reversible next action.",
            review_point="Review after the next concrete result.",
        )

    monkeypatch.setattr(adapter, "run_decision_framework", fake_run)

    context = build_decision_support_context({})

    assert context == "\n".join(
        [
            "<decision_support_context>",
            "This is decision support context, not a final decision.",
            "The user remains responsible for the decision.",
            "Perspective:",
            "Pause and compare the available paths.",
            "Decision Synthesis:",
            "Options:",
            "- Option A",
            "- Option B",
            "Tradeoffs:",
            "- Speed vs confidence",
            "Constraints:",
            "- Limited energy",
            "Unknowns:",
            "- External timing",
            "Next Step:",
            "List one reversible next action.",
            "Review Point:",
            "Review after the next concrete result.",
            "</decision_support_context>",
        ]
    )


def test_guardrail_files_are_not_changed_by_adapter_story():
    result = subprocess.run(
        [
            "git",
            "diff",
            "--name-only",
            "--",
            "conversation_loop.py",
            "run_agent.py",
            "agent/prompt_builder.py",
            "gateway",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout == ""
