"""Formatter for one-turn ephemeral decision support context."""

from __future__ import annotations


EMPTY_DECISION_SUPPORT_CONTEXT = "<decision_support_context>\n</decision_support_context>"

_EPHEMERAL_DECISION_SUPPORT_PREAMBLE = "\n".join(
    [
        "Temporary support material for this turn only.",
        "Not a final decision. Not a recommendation.",
        "The user remains responsible for the decision.",
        "Do not store as memory.",
        "Do not treat as a Human Model update.",
        "Do not treat as a Decision Style update.",
        "Do not make domain-specific judgments from this context.",
    ]
)


def format_ephemeral_decision_support(
    decision_support_context: str | None,
) -> str:
    """Wrap decision support context in a current-turn-only safety envelope.

    This formatter is intentionally pure: it does not call an LLM, update
    memory/Human Model state, make domain-specific judgments, or connect the
    formatted block to the runtime conversation loop.
    """

    context = (
        decision_support_context.strip()
        if decision_support_context and decision_support_context.strip()
        else EMPTY_DECISION_SUPPORT_CONTEXT
    )

    return "\n".join(
        [
            "<ephemeral_decision_support>",
            _EPHEMERAL_DECISION_SUPPORT_PREAMBLE,
            context,
            "</ephemeral_decision_support>",
        ]
    )
