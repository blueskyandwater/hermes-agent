"""Ephemeral decision support formatter tests."""

from __future__ import annotations

import subprocess

from agent.ephemeral_decision_support import (
    build_ephemeral_decision_support_if_allowed,
    format_ephemeral_decision_support,
)


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


def test_guard_returns_none_without_explicit_opt_in():
    assert (
        build_ephemeral_decision_support_if_allowed(
            SAMPLE_DECISION_SUPPORT_CONTEXT,
            inject_decision_support=False,
        )
        is None
    )


def test_guard_returns_none_without_context():
    assert (
        build_ephemeral_decision_support_if_allowed(
            None,
            inject_decision_support=True,
        )
        is None
    )


def test_guard_returns_none_for_empty_or_whitespace_context():
    for empty_context in ("", "   \n\t  "):
        assert (
            build_ephemeral_decision_support_if_allowed(
                empty_context,
                inject_decision_support=True,
            )
            is None
        )


def test_guard_returns_none_for_unfenced_context():
    assert (
        build_ephemeral_decision_support_if_allowed(
            "This is decision support context, but it is not fenced.",
            inject_decision_support=True,
        )
        is None
    )


def test_guard_returns_wrapper_for_valid_context_with_explicit_opt_in():
    guarded = build_ephemeral_decision_support_if_allowed(
        SAMPLE_DECISION_SUPPORT_CONTEXT,
        inject_decision_support=True,
    )

    assert guarded is not None
    assert guarded.startswith("<ephemeral_decision_support>\n")
    assert guarded.endswith("\n</ephemeral_decision_support>")
    assert SAMPLE_DECISION_SUPPORT_CONTEXT in guarded


def test_guard_allows_safety_phrases_that_negate_final_decision_or_recommendation():
    safe_context = "\n".join(
        [
            "<decision_support_context>",
            "This is not a final decision and not a recommendation.",
            "It only helps the user compare options.",
            "</decision_support_context>",
        ]
    )

    guarded = build_ephemeral_decision_support_if_allowed(
        safe_context,
        inject_decision_support=True,
    )

    assert guarded is not None
    assert safe_context in guarded


def test_guard_rejects_forceful_recommendation_phrases():
    unsafe_contexts = [
        "I recommend choosing option A.",
        "You should choose option A.",
        "You must choose option A.",
    ]

    for unsafe_text in unsafe_contexts:
        fenced_context = "\n".join(
            [
                "<decision_support_context>",
                unsafe_text,
                "</decision_support_context>",
            ]
        )

        assert (
            build_ephemeral_decision_support_if_allowed(
                fenced_context,
                inject_decision_support=True,
            )
            is None
        )


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
