import json
from pathlib import Path

import agent.usage_logger as usage_logger


def setup_function():
    usage_logger._reset_usage_log_state()


def teardown_function():
    usage_logger._reset_usage_log_state()


def test_init_usage_log_configures_rotating_handler(tmp_path):
    log_path = tmp_path / "usage.jsonl"
    usage_logger.init_usage_log({
        "usage_log_path": str(log_path),
        "usage_log_max_size_mb": 3,
        "usage_log_backup_count": 7,
    })

    assert usage_logger._USAGE_LOG_ENABLED is True
    assert usage_logger._USAGE_LOG_PATH == str(log_path)
    assert usage_logger._USAGE_HANDLER is not None
    assert usage_logger._USAGE_HANDLER.maxBytes == 3 * 1024 * 1024
    assert usage_logger._USAGE_HANDLER.backupCount == 7


def test_log_llm_call_writes_expanded_observability_fields(tmp_path):
    log_path = tmp_path / "usage.jsonl"
    usage_logger.init_usage_log({"usage_log_path": str(log_path)})

    usage_logger.log_llm_call(
        model="gpt-5.5",
        request_model="gpt-5.3-codex-spark",
        response_model="gpt-5.5",
        executed_model="gpt-5.5",
        provider="openai-codex",
        input_tokens=100,
        output_tokens=50,
        total_tokens=150,
        estimated_cost_usd=0.12,
        latency_ms=321.9,
        route_type="code_light",
        classification_reason="keyword:code_light",
        channel="discord",
        trimmed_messages=2,
        cache_read_tokens=40,
        cache_write_tokens=5,
        reasoning_tokens=7,
        fallback_triggered=True,
        fallback_model="deepseek/deepseek-v4-flash",
        attempt_number=2,
        fallback_from_model="gpt-5.3-codex-spark",
        fallback_to_model="deepseek/deepseek-v4-flash",
        fallback_reason="provider unavailable",
        route_model="gpt-5.3-codex-spark",
        context_token_estimate=12034,
        request_message_count=18,
        fallback_chain_length=2,
        fallback_chain_present=True,
        runtime_provider_fallback_active=True,
        provider_fallback_active=True,
    )

    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["route_model"] == "gpt-5.3-codex-spark"
    assert record["context_token_estimate"] == 12034
    assert record["request_message_count"] == 18
    assert record["fallback_chain_length"] == 2
    assert record["fallback_chain_present"] is True
    assert record["runtime_provider_fallback_active"] is True
    assert record["provider_fallback_active"] is True


def test_usage_log_rotates_when_size_exceeded(tmp_path):
    log_path = tmp_path / "usage.jsonl"
    usage_logger.init_usage_log({
        "usage_log_path": str(log_path),
        "usage_log_max_size_mb": 1,
        "usage_log_backup_count": 2,
    })

    handler = usage_logger._USAGE_HANDLER
    assert handler is not None
    handler.maxBytes = 250

    for i in range(8):
        usage_logger.log_llm_call(
            model="gpt-5.5",
            provider="openai-codex",
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
            estimated_cost_usd=0.12,
            latency_ms=100.0 + i,
            route_type="normal_chat",
            classification_reason="",
            route_model="gpt-5.5",
            context_token_estimate=2000 + i,
            request_message_count=10,
        )

    rotated = Path(str(log_path) + ".1")
    assert log_path.exists()
    assert rotated.exists()
    latest = log_path.read_text(encoding="utf-8")
    older = rotated.read_text(encoding="utf-8")
    assert latest.strip()
    assert older.strip()
