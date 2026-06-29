"""Adapter for Decision Framework decision-support context generation.

This module keeps the core Decision Framework runtime pure while providing a
small boundary that can later be called by runtime integration code. It does
not connect itself to conversation flow, memory, tools, or gateway surfaces.
"""

from __future__ import annotations

from typing import Any, Mapping

from agent.decision_framework import (
    DecisionFrameworkInput,
    DecisionFrameworkOutput,
    run_decision_framework,
)
from agent.human_model_snapshot import normalize_human_model_snapshot

__all__ = ["build_decision_support_context"]

_SYNTHESIS_SECTIONS = (
    ("options", "Options"),
    ("tradeoffs", "Tradeoffs"),
    ("constraints", "Constraints"),
    ("unknowns", "Unknowns"),
)


def build_decision_support_context(
    human_model_snapshot: Mapping[str, Any] | None,
    turn_context: Mapping[str, Any] | None = None,
) -> str:
    """Build fenced decision-support context from safe adapter inputs."""

    _ = turn_context if isinstance(turn_context, Mapping) else {}
    input_data = _build_decision_framework_input(human_model_snapshot)
    output = run_decision_framework(input_data)
    return _format_decision_support_context(output)


def _build_decision_framework_input(
    human_model_snapshot: Mapping[str, Any] | None,
) -> DecisionFrameworkInput:
    values = normalize_human_model_snapshot(human_model_snapshot)
    return DecisionFrameworkInput(**values)


def _format_decision_support_context(output: DecisionFrameworkOutput) -> str:
    lines = [
        "<decision_support_context>",
        "This is decision support context, not a final decision.",
        "The user remains responsible for the decision.",
        "Perspective:",
        output.perspective,
        "Decision Synthesis:",
    ]

    synthesis = output.decision_synthesis if isinstance(output.decision_synthesis, Mapping) else {}
    for key, label in _SYNTHESIS_SECTIONS:
        lines.append(f"{label}:")
        lines.extend(_format_bullets(synthesis.get(key, [])))

    lines.extend(
        [
            "Next Step:",
            output.next_step,
            "Review Point:",
            output.review_point,
            "</decision_support_context>",
        ]
    )
    return "\n".join(str(line) for line in lines)


def _format_bullets(items: Any) -> list[str]:
    if isinstance(items, str):
        normalized_items = [items]
    elif isinstance(items, list | tuple):
        normalized_items = list(items)
    else:
        normalized_items = []

    if not normalized_items:
        return ["-"]
    return [f"- {item}" for item in normalized_items]
