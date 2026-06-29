"""Trusted internal caller helper for prebuilt Decision Support context."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from agent.decision_framework_adapter import build_decision_support_context

__all__ = ["run_conversation_with_internal_decision_support"]


def run_conversation_with_internal_decision_support(
    agent: Any,
    user_message: str,
    *,
    human_model_snapshot: Mapping[str, Any] | None = None,
    turn_context: Mapping[str, Any] | None = None,
    **conversation_kwargs: Any,
) -> Any:
    """Run a conversation with explicit trusted Decision Support input.

    The helper is intentionally narrow: callers must pass a snapshot explicitly,
    and this function only prebuilds context before forwarding to the agent's
    existing ``run_conversation`` entrypoint.
    """

    if not _has_snapshot_content(human_model_snapshot):
        return agent.run_conversation(
            user_message,
            **conversation_kwargs,
            inject_decision_support=False,
        )

    resolved_turn_context = turn_context or _default_turn_context(
        user_message,
        conversation_kwargs,
    )
    decision_support_context = build_decision_support_context(
        human_model_snapshot,
        turn_context=resolved_turn_context,
    )
    return agent.run_conversation(
        user_message,
        **conversation_kwargs,
        decision_support_context=decision_support_context,
        inject_decision_support=True,
    )


def _has_snapshot_content(human_model_snapshot: Mapping[str, Any] | None) -> bool:
    if not isinstance(human_model_snapshot, Mapping):
        return False
    if not human_model_snapshot:
        return False
    return any(_has_value(value) for value in human_model_snapshot.values())


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Mapping):
        return any(_has_value(nested_value) for nested_value in value.values())
    if isinstance(value, list | tuple | set | frozenset):
        return any(_has_value(item) for item in value)
    return True


def _default_turn_context(
    user_message: str,
    conversation_kwargs: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "user_message": user_message,
        "task_id": conversation_kwargs.get("task_id"),
        "source": "internal",
    }
