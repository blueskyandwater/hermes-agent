"""Decision Framework runtime skeleton.

This module is intentionally small and side-effect free. It defines the v1
Decision Framework input/output contract and a pure runtime entrypoint that
returns the minimal output structure without making decisions for the user.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class DecisionFrameworkInput:
    """Allowed Human Model inputs for Decision Framework v1."""

    identity: Mapping[str, Any] = field(default_factory=dict)
    energy: Mapping[str, Any] = field(default_factory=dict)
    habit: Mapping[str, Any] = field(default_factory=dict)
    growth: Mapping[str, Any] = field(default_factory=dict)
    communication: Mapping[str, Any] = field(default_factory=dict)
    coaching: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DecisionFrameworkOutput:
    """Decision-support output contract for Decision Framework v1."""

    perspective: str = ""
    decision_synthesis: Mapping[str, list[Any]] = field(
        default_factory=lambda: {
            "options": [],
            "tradeoffs": [],
            "constraints": [],
            "unknowns": [],
        }
    )
    next_step: str = ""
    review_point: str = ""


def run_decision_framework(
    input_data: DecisionFrameworkInput | Mapping[str, Any],
) -> DecisionFrameworkOutput:
    """Return the minimal Decision Framework output structure.

    The runtime skeleton accepts and normalizes Human Model input but does not
    perform policy logic, domain-specific judgment, final-decision generation,
    Human Model mutation, prompt integration, memory integration, or gateway/API
    integration.
    """

    _normalize_input(input_data)
    return DecisionFrameworkOutput()


def _normalize_input(input_data: DecisionFrameworkInput | Mapping[str, Any]) -> DecisionFrameworkInput:
    if isinstance(input_data, DecisionFrameworkInput):
        return input_data
    if not isinstance(input_data, Mapping):
        return DecisionFrameworkInput()

    allowed_fields = DecisionFrameworkInput.__dataclass_fields__
    values = {
        name: value if isinstance(value, Mapping) else {}
        for name, value in input_data.items()
        if name in allowed_fields
    }
    return DecisionFrameworkInput(**values)
