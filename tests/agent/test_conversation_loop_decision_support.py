from __future__ import annotations

import copy
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from agent.conversation_loop import run_conversation
from agent.memory_manager import build_memory_context_block


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


class _CaptureApiMessages(BaseException):
    pass


class _ToolGuardrails:
    def reset_for_turn(self) -> None:
        return None


class _TodoStore:
    def has_items(self) -> bool:
        return False


class _CheckpointManager:
    def new_turn(self) -> None:
        return None


class _MemoryManager:
    def __init__(self, prefetch_text: str) -> None:
        self.prefetch_text = prefetch_text

    def on_turn_start(self, *_args, **_kwargs) -> None:
        return None

    def prefetch_all(self, _query: str) -> str:
        return self.prefetch_text


class _Agent:
    def __init__(self, *, plugin_context: str, memory_prefetch: str) -> None:
        self.session_id = "test-session"
        self.provider = "test-provider"
        self.model = "test-model"
        self.base_url = ""
        self.api_key = ""
        self.api_mode = "openai"
        self.platform = "cli"
        self.quiet_mode = True
        self.valid_tool_names = []
        self.max_iterations = 3
        self._configured_max_iterations = 3
        self._memory_write_origin = "assistant_tool"
        self._tool_guardrails = _ToolGuardrails()
        self._compression_warning = None
        self._trim_to_last_n = 0
        self._todo_store = _TodoStore()
        self._user_turn_count = 0
        self._memory_nudge_interval = 0
        self._memory_store = None
        self._turns_since_memory = 0
        self._cached_system_prompt = "CACHED_PROMPT"
        self.compression_enabled = False
        self.prefill_messages = []
        self._use_prompt_caching = False
        self.ephemeral_system_prompt = ""
        self._memory_manager = _MemoryManager(memory_prefetch)
        self._checkpoint_mgr = _CheckpointManager()
        self._budget_grace_call = False
        self.step_callback = None
        self._skill_nudge_interval = 0
        self._iters_since_skill = 0
        self._pending_steer = None
        self._pending_steer_lock = None
        self.logger = None
        self.tools = []
        self._force_ascii_payload = False
        self._routing_config = {}
        self._interrupt_requested = False
        self._interrupt_thread_signal_pending = False
        self._stream_callback = None
        self._stream_context_scrubber = None
        self._stream_think_scrubber = None
        self.thinking_callback = lambda *_args, **_kwargs: None
        self.verbose_logging = False
        self._api_max_retries = 1
        self._fallback_activated = False
        self._runtime_provider_fallback_active = False
        self._fallback_chain = []
        self._session_db = MagicMock()
        self.plugin_context = plugin_context
        self.captured_messages_before_api = None
        self.captured_api_messages = None

    def _ensure_db_session(self) -> None:
        return None

    def _restore_primary_runtime(self) -> None:
        return None

    def _cleanup_dead_connections(self) -> bool:
        return False

    def _replay_compression_warning(self) -> None:
        return None

    def _hydrate_todo_store(self, _conversation_history) -> None:
        return None

    def _safe_print(self, *_args, **_kwargs) -> None:
        return None

    def _touch_activity(self, *_args, **_kwargs) -> None:
        return None

    def _drain_pending_steer(self):
        return None

    def _sanitize_api_messages(self, api_messages):
        return api_messages

    def _drop_thinking_only_and_merge_users(self, api_messages):
        return api_messages

    def _sanitize_tool_call_arguments(self, _messages, logger=None, session_id=None) -> int:
        return 0

    def _repair_message_sequence(self, messages) -> int:
        self.captured_messages_before_api = copy.deepcopy(messages)
        return 0

    def _copy_reasoning_content_for_api(self, _msg, _api_msg) -> None:
        return None

    def _should_sanitize_tool_calls(self) -> bool:
        return False

    def _sanitize_tool_calls_for_strict_api(self, _api_msg, model=None) -> None:
        return None

    def _reset_stream_delivery_tracking(self) -> None:
        return None

    def _reapply_reasoning_echo_for_provider(self, _api_messages) -> None:
        return None

    def _build_api_kwargs(self, api_messages):
        self.captured_api_messages = copy.deepcopy(api_messages)
        raise _CaptureApiMessages()


def _stub_run_agent_module():
    return SimpleNamespace(_set_interrupt=lambda *_args, **_kwargs: None)


def test_run_conversation_injects_decision_support_only_into_current_user_api_copy(
    monkeypatch,
):
    plugin_context = "PLUGIN_CONTEXT"
    memory_prefetch = "remembered fact"
    history = [
        {"role": "user", "content": "previous question"},
        {"role": "assistant", "content": "previous answer"},
    ]
    original_history = copy.deepcopy(history)
    agent = _Agent(plugin_context=plugin_context, memory_prefetch=memory_prefetch)

    monkeypatch.setattr("hermes_cli.plugins.invoke_hook", lambda *args, **kwargs: [{"context": plugin_context}])
    monkeypatch.setattr("agent.conversation_loop._ra", _stub_run_agent_module)

    with pytest.raises(_CaptureApiMessages):
        run_conversation(
            agent,
            "current question",
            conversation_history=history,
            decision_support_context=SAMPLE_DECISION_SUPPORT_CONTEXT,
            inject_decision_support=True,
        )

    assert history == original_history
    assert agent._cached_system_prompt == "CACHED_PROMPT"
    assert agent._session_db.mock_calls == []
    assert agent.captured_messages_before_api[-1] == {
        "role": "user",
        "content": "current question",
    }

    api_messages = agent.captured_api_messages
    assert [m["role"] for m in api_messages] == ["system", "user", "assistant", "user"]
    assert api_messages[0]["content"] == "CACHED_PROMPT"
    assert api_messages[1]["content"] == "previous question"
    assert api_messages[2]["content"] == "previous answer"

    current_user_content = api_messages[3]["content"]
    expected_memory_block = build_memory_context_block(memory_prefetch)
    assert current_user_content.startswith("current question\n\n")
    assert expected_memory_block in current_user_content
    assert plugin_context in current_user_content
    assert "<ephemeral_decision_support>" in current_user_content
    assert current_user_content.index(expected_memory_block) < current_user_content.index(plugin_context)
    assert current_user_content.index(plugin_context) < current_user_content.index("<ephemeral_decision_support>")


def test_run_conversation_does_not_inject_decision_support_without_opt_in(monkeypatch):
    plugin_context = "PLUGIN_CONTEXT"
    memory_prefetch = "remembered fact"
    agent = _Agent(plugin_context=plugin_context, memory_prefetch=memory_prefetch)

    monkeypatch.setattr("hermes_cli.plugins.invoke_hook", lambda *args, **kwargs: [{"context": plugin_context}])
    monkeypatch.setattr("agent.conversation_loop._ra", _stub_run_agent_module)

    with pytest.raises(_CaptureApiMessages):
        run_conversation(
            agent,
            "current question",
            conversation_history=[],
            decision_support_context=SAMPLE_DECISION_SUPPORT_CONTEXT,
            inject_decision_support=False,
        )

    current_user_content = agent.captured_api_messages[-1]["content"]
    assert build_memory_context_block(memory_prefetch) in current_user_content
    assert plugin_context in current_user_content
    assert "<ephemeral_decision_support>" not in current_user_content
