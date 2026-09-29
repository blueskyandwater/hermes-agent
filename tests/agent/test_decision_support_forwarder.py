"""Tests for AIAgent.run_conversation Decision Support forwarding."""

from __future__ import annotations

import inspect
from run_agent import AIAgent


def test_run_conversation_signature_keeps_existing_args_and_adds_defaulted_decision_support_args():
    signature = inspect.signature(AIAgent.run_conversation)
    assert list(signature.parameters)[:7] == [
        "self", "user_message", "system_message", "conversation_history", "task_id",
        "stream_callback", "persist_user_message",
    ]
    assert list(signature.parameters)[-2:] == ["decision_support_context", "inject_decision_support"]
    assert signature.parameters["decision_support_context"].default is None
    assert signature.parameters["inject_decision_support"].default is False


def test_run_conversation_default_call_forwards_no_decision_support(monkeypatch):
    captured = {}

    def fake_run_conversation(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return {"final_response": "ok"}

    monkeypatch.setattr("agent.conversation_loop.run_conversation", fake_run_conversation)
    agent = object.__new__(AIAgent)
    result = agent.run_conversation("hello")
    assert result == {"final_response": "ok"}
    assert captured["args"][:3] == (agent, "hello", None)
    assert captured["kwargs"]["decision_support_context"] is None
    assert captured["kwargs"]["inject_decision_support"] is False


def test_run_conversation_forwards_decision_support_context_and_opt_in(monkeypatch):
    captured = {}

    def fake_run_conversation(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return {"final_response": "ok"}

    monkeypatch.setattr("agent.conversation_loop.run_conversation", fake_run_conversation)
    agent = object.__new__(AIAgent)
    history = [{"role": "user", "content": "previous"}]
    result = agent.run_conversation(
        "hello", system_message="system", conversation_history=history, task_id="task-1",
        stream_callback="callback", persist_user_message="persist me",
        decision_support_context="prebuilt decision support", inject_decision_support=True,
    )
    assert result == {"final_response": "ok"}
    assert captured["args"][:7] == (
        agent, "hello", "system", history, "task-1", "callback", "persist me",
    )
    assert captured["kwargs"]["decision_support_context"] == "prebuilt decision support"
    assert captured["kwargs"]["inject_decision_support"] is True


def test_forwarder_does_not_execute_decision_framework_or_human_model_snapshot():
    source = inspect.getsource(AIAgent.run_conversation)
    assert "build_decision_support_context" not in source
    assert "DecisionFramework" not in source
    assert "HumanModel" not in source
    assert "snapshot" not in source.lower()
