"""Formatter for one-turn ephemeral decision support context."""

from __future__ import annotations

import re


EMPTY_DECISION_SUPPORT_CONTEXT = "<decision_support_context>\n</decision_support_context>"
DECISION_SUPPORT_CONTEXT_OPEN_TAG = "<decision_support_context>"
DECISION_SUPPORT_CONTEXT_CLOSE_TAG = "</decision_support_context>"
EPHEMERAL_DECISION_SUPPORT_OPEN_TAG = "<ephemeral_decision_support>"
EPHEMERAL_DECISION_SUPPORT_CLOSE_TAG = "</ephemeral_decision_support>"

_UNSAFE_DECISION_SUPPORT_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bi\s+recommend\b",
        r"\byou\s+should\b",
        r"\byou\s+must\b",
        r"\bmy\s+recommendation\s+is\b",
        r"\bthe\s+recommendation\s+is\b",
        r"\bfinal\s+decision\s*:",
        r"\bthe\s+final\s+decision\s+is\b",
    )
)

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


def _is_valid_decision_support_context(decision_support_context: str | None) -> bool:
    """Return whether context is safe to wrap for explicit opt-in injection."""

    if not isinstance(decision_support_context, str):
        return False

    context = decision_support_context.strip()
    if not context:
        return False

    if not context.startswith(DECISION_SUPPORT_CONTEXT_OPEN_TAG):
        return False
    if not context.endswith(DECISION_SUPPORT_CONTEXT_CLOSE_TAG):
        return False

    inner_context = context[
        len(DECISION_SUPPORT_CONTEXT_OPEN_TAG) : -len(DECISION_SUPPORT_CONTEXT_CLOSE_TAG)
    ].strip()
    if not inner_context:
        return False

    return not any(pattern.search(context) for pattern in _UNSAFE_DECISION_SUPPORT_PATTERNS)


def build_ephemeral_decision_support_if_allowed(
    decision_support_context: str | None,
    *,
    inject_decision_support: bool = False,
) -> str | None:
    """Build one-turn decision support wrapper only when explicit guard allows it.

    This guard is intentionally standalone. It does not connect to the
    conversation loop, call an LLM, read/write memory, mutate Human Model state,
    infer decision-like turns heuristically, or generate recommendations/final
    decisions.
    """

    if not inject_decision_support:
        return None
    if not _is_valid_decision_support_context(decision_support_context):
        return None

    formatted = format_ephemeral_decision_support(decision_support_context)
    formatted_stripped = formatted.strip()
    if not formatted_stripped.startswith(EPHEMERAL_DECISION_SUPPORT_OPEN_TAG):
        return None
    if not formatted_stripped.endswith(EPHEMERAL_DECISION_SUPPORT_CLOSE_TAG):
        return None

    return formatted


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
