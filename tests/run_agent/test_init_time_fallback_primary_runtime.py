"""Regression tests for init-time provider fallback runtime snapshots."""

from unittest.mock import MagicMock, patch

from run_agent import AIAgent


def _mock_openai_client(base_url="https://openrouter.ai/api/v1", api_key="sk-fallback"):
    client = MagicMock()
    client.api_key = api_key
    client.base_url = base_url
    client._custom_headers = {}
    return client


def test_init_time_auth_fallback_snapshot_keeps_config_primary_runtime(monkeypatch, tmp_path):
    """When primary auth is unavailable at init, fallback may bootstrap the
    client, but the per-turn primary snapshot must remain the configured
    primary model/provider.

    Otherwise restore_primary_runtime() treats the fallback as primary and
    subsequent routed turns can send the config primary model (gpt-5.5) through
    the fallback provider (OpenRouter).
    """

    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        """
model:
  default: gpt-5.5
  provider: openai-codex
  base_url: https://chatgpt.com/backend-api/codex
  api_mode: codex_responses
routing:
  enabled: true
  normal_chat:
    model: gpt-5.5
fallback_providers:
  - provider: openrouter
    model: deepseek/deepseek-v4-flash
""".lstrip(),
        encoding="utf-8",
    )
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))

    fallback_client = _mock_openai_client()

    def fake_resolve_provider_client(provider, **kwargs):
        if provider == "openai-codex":
            return None, None
        assert provider == "openrouter"
        return fallback_client, kwargs.get("model")

    with (
        patch("agent.auxiliary_client.resolve_provider_client", side_effect=fake_resolve_provider_client),
        patch("run_agent.get_tool_definitions", return_value=[]),
        patch("run_agent.check_toolset_requirements", return_value={}),
        patch("run_agent.OpenAI", return_value=MagicMock()),
    ):
        agent = AIAgent(
            provider="openai-codex",
            model="gpt-5.5",
            base_url="https://chatgpt.com/backend-api/codex",
            api_mode="codex_responses",
            api_key="",
            fallback_model=[{"provider": "openrouter", "model": "deepseek/deepseek-v4-flash"}],
            quiet_mode=True,
            skip_context_files=True,
            skip_memory=True,
        )

        assert agent.provider == "openrouter"
        assert agent.model == "deepseek/deepseek-v4-flash"
        assert agent._fallback_activated is True

        # The snapshot represents the configured primary, not the bootstrap
        # fallback runtime.
        assert agent._primary_runtime["provider"] == "openai-codex"
        assert agent._primary_runtime["model"] == "gpt-5.5"
        assert agent._primary_runtime["base_url"] == "https://chatgpt.com/backend-api/codex"
        assert agent._primary_runtime["api_mode"] == "codex_responses"

        # While the primary rate-limit cooldown is active, restoring is a no-op
        # and the active fallback model/provider pair stays coherent.
        agent._rate_limited_until = 9999999999
        assert agent._restore_primary_runtime() is False
        assert agent.provider == "openrouter"
        assert agent.model == "deepseek/deepseek-v4-flash"
