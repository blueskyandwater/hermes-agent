"""Tests for trusted internal Decision Support caller helper."""

from __future__ import annotations

import inspect

import pytest

import agent.internal_decision_support as internal_decision_support
from agent.internal_decision_support import run_conversation_with_internal_decision_support


class FakeAgent:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def run_conversation(self, user_message: str, **kwargs: object) -> dict[str, object]:
        self.calls.append({"user_message": user_message, "kwargs": kwargs})
        return {"final_response": "ok"}


def _snapshot() -> dict[str, dict[str, object]]:
    return {"identity": {"values": ["autonomy"]}}


def test_none_snapshot_does_not_build_or_inject(monkeypatch: pytest.MonkeyPatch):
    def fail_build(*args: object, **kwargs: object) -> str:
        raise AssertionError("build_decision_support_context should not be called")

    monkeypatch.setattr(internal_decision_support, "build_decision_support_context", fail_build)
    agent = FakeAgent()

    result = run_conversation_with_internal_decision_support(agent, "hello")

    assert result == {"final_response": "ok"}
    assert agent.calls == [
        {
            "user_message": "hello",
            "kwargs": {"inject_decision_support": False},
        }
    ]


def test_empty_snapshot_does_not_build_or_inject(monkeypatch: pytest.MonkeyPatch):
    def fail_build(*args: object, **kwargs: object) -> str:
        raise AssertionError("build_decision_support_context should not be called")

    monkeypatch.setattr(internal_decision_support, "build_decision_support_context", fail_build)
    agent = FakeAgent()

    run_conversation_with_internal_decision_support(agent, "hello", human_model_snapshot={})

    assert agent.calls[0]["kwargs"]["inject_decision_support"] is False
    assert "decision_support_context" not in agent.calls[0]["kwargs"]


def test_snapshot_with_only_empty_sections_does_not_build_or_inject(
    monkeypatch: pytest.MonkeyPatch,
):
    def fail_build(*args: object, **kwargs: object) -> str:
        raise AssertionError("build_decision_support_context should not be called")

    monkeypatch.setattr(internal_decision_support, "build_decision_support_context", fail_build)
    agent = FakeAgent()

    run_conversation_with_internal_decision_support(
        agent,
        "hello",
        human_model_snapshot={"identity": {}, "energy": {}},
    )

    assert agent.calls[0]["kwargs"]["inject_decision_support"] is False
    assert "decision_support_context" not in agent.calls[0]["kwargs"]


def test_snapshot_builds_context_and_injects(monkeypatch: pytest.MonkeyPatch):
    captured: dict[str, object] = {}

    def fake_build(human_model_snapshot: object, turn_context: object = None) -> str:
        captured["human_model_snapshot"] = human_model_snapshot
        captured["turn_context"] = turn_context
        return "<decision_support_context>prebuilt</decision_support_context>"

    monkeypatch.setattr(internal_decision_support, "build_decision_support_context", fake_build)
    agent = FakeAgent()
    snapshot = _snapshot()

    run_conversation_with_internal_decision_support(
        agent,
        "Should I choose A?",
        human_model_snapshot=snapshot,
    )

    assert captured["human_model_snapshot"] is snapshot
    assert captured["turn_context"] == {
        "user_message": "Should I choose A?",
        "task_id": None,
        "source": "internal",
    }
    assert agent.calls[0]["kwargs"]["decision_support_context"] == (
        "<decision_support_context>prebuilt</decision_support_context>"
    )
    assert agent.calls[0]["kwargs"]["inject_decision_support"] is True


def test_default_turn_context_includes_task_id_from_conversation_kwargs(
    monkeypatch: pytest.MonkeyPatch,
):
    captured: dict[str, object] = {}

    def fake_build(human_model_snapshot: object, turn_context: object = None) -> str:
        captured["turn_context"] = turn_context
        return "<decision_support_context>prebuilt</decision_support_context>"

    monkeypatch.setattr(internal_decision_support, "build_decision_support_context", fake_build)
    agent = FakeAgent()

    run_conversation_with_internal_decision_support(
        agent,
        "hello",
        human_model_snapshot=_snapshot(),
        task_id="task-123",
    )

    assert captured["turn_context"] == {
        "user_message": "hello",
        "task_id": "task-123",
        "source": "internal",
    }


def test_explicit_turn_context_is_used(monkeypatch: pytest.MonkeyPatch):
    captured: dict[str, object] = {}

    def fake_build(human_model_snapshot: object, turn_context: object = None) -> str:
        captured["turn_context"] = turn_context
        return "<decision_support_context>prebuilt</decision_support_context>"

    monkeypatch.setattr(internal_decision_support, "build_decision_support_context", fake_build)
    agent = FakeAgent()
    turn_context = {"source": "scheduler", "task_id": "task-999"}

    run_conversation_with_internal_decision_support(
        agent,
        "hello",
        human_model_snapshot=_snapshot(),
        turn_context=turn_context,
    )

    assert captured["turn_context"] is turn_context


def test_conversation_kwargs_are_preserved(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        internal_decision_support,
        "build_decision_support_context",
        lambda *args, **kwargs: "<decision_support_context>prebuilt</decision_support_context>",
    )
    agent = FakeAgent()
    history = [{"role": "user", "content": "previous"}]

    run_conversation_with_internal_decision_support(
        agent,
        "hello",
        human_model_snapshot=_snapshot(),
        system_message="system",
        conversation_history=history,
        task_id="task-1",
        stream_callback="callback",
        persist_user_message="persist me",
    )

    assert agent.calls[0]["kwargs"] == {
        "system_message": "system",
        "conversation_history": history,
        "task_id": "task-1",
        "stream_callback": "callback",
        "persist_user_message": "persist me",
        "decision_support_context": "<decision_support_context>prebuilt</decision_support_context>",
        "inject_decision_support": True,
    }


def test_helper_boundary_does_not_touch_memory_human_model_gateway_api_or_cli():
    source = inspect.getsource(internal_decision_support)

    forbidden_fragments = (
        "memory",
        "gateway",
        "api_server",
        "cli",
        "HumanModelSnapshotProvider",
        "build_snapshot",
        "normalize_human_model_snapshot",
        "run_decision_framework",
    )
    for fragment in forbidden_fragments:
        assert fragment not in source
