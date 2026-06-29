"""Ephemeral decision support formatter tests."""

from __future__ import annotations

import subprocess

from agent.ephemeral_decision_support import format_ephemeral_decision_support


SAMPLE_DECISION_SUPPORT_CONTEXT = "\n".join(
    [
        "<decision_support_context>",
        "This is decision support context, not a final decision.",
        "The user remains responsible for the decision.",
        "Perspective:",
        "Pause and compare the available paths.",
        "</decision_support_context>",
    ]
)


def test_wrapper_starts_and_ends_with_ephemeral_decision_support_tags():
    formatted = format_ephemeral_decision_support(SAMPLE_DECISION_SUPPORT_CONTEXT)

    assert formatted.startswith("<ephemeral_decision_support>\n")
    assert formatted.endswith("\n</ephemeral_decision_support>")


def test_input_decision_support_context_is_preserved_inside_wrapper():
    formatted = format_ephemeral_decision_support(SAMPLE_DECISION_SUPPORT_CONTEXT)

    assert SAMPLE_DECISION_SUPPORT_CONTEXT in formatted


def test_wrapper_declares_current_turn_only_context():
    formatted = format_ephemeral_decision_support(SAMPLE_DECISION_SUPPORT_CONTEXT)

    assert "Temporary support material for this turn only." in formatted


def test_wrapper_declares_not_final_decision_or_recommendation():
    formatted = format_ephemeral_decision_support(SAMPLE_DECISION_SUPPORT_CONTEXT)

    assert "Not a final decision. Not a recommendation." in formatted


def test_wrapper_keeps_user_responsible_for_decision():
    formatted = format_ephemeral_decision_support(SAMPLE_DECISION_SUPPORT_CONTEXT)

    assert "The user remains responsible for the decision." in formatted


def test_wrapper_forbids_memory_storage():
    formatted = format_ephemeral_decision_support(SAMPLE_DECISION_SUPPORT_CONTEXT)

    assert "Do not store as memory." in formatted


def test_wrapper_forbids_human_model_and_decision_style_updates():
    formatted = format_ephemeral_decision_support(SAMPLE_DECISION_SUPPORT_CONTEXT)

    assert "Do not treat as a Human Model update." in formatted
    assert "Do not treat as a Decision Style update." in formatted


def test_wrapper_forbids_domain_specific_judgments():
    formatted = format_ephemeral_decision_support(SAMPLE_DECISION_SUPPORT_CONTEXT)

    assert "Do not make domain-specific judgments from this context." in formatted


def test_empty_inputs_return_safe_empty_decision_support_context():
    for empty_input in (None, "", "   \n\t  "):
        formatted = format_ephemeral_decision_support(empty_input)

        assert formatted.startswith("<ephemeral_decision_support>\n")
        assert "<decision_support_context>\n</decision_support_context>" in formatted
        assert formatted.endswith("\n</ephemeral_decision_support>")


def test_guardrail_files_are_not_changed_by_formatter_story():
    result = subprocess.run(
        [
            "git",
            "diff",
            "--name-only",
            "--",
            "agent/conversation_loop.py",
            "run_agent.py",
            "agent/prompt_builder.py",
            "gateway",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout == ""
