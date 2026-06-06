"""
Per-request usage logging — structured JSONL output.

Writes one JSON line per LLM API call to a configurable file path.
No API keys, no message content, no raw API responses are logged.
Disabled by default; enable by setting ``usage_log_path`` in config.yaml
or ``HERMES_USAGE_LOG`` in .env.
"""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Module-level state — initialised once at startup.
_USAGE_LOG_PATH: str = ""
_USAGE_LOG_ENABLED: bool = False
_USAGE_LOG_MAX_BYTES: int = 20 * 1024 * 1024
_USAGE_LOG_BACKUP_COUNT: int = 5
_USAGE_LOGGER: Optional[logging.Logger] = None
_USAGE_HANDLER: Optional[RotatingFileHandler] = None


def _reset_usage_log_state() -> None:
    """Test/helper hook to clear the dedicated usage logger state."""
    global _USAGE_LOGGER, _USAGE_HANDLER, _USAGE_LOG_ENABLED, _USAGE_LOG_PATH
    if _USAGE_HANDLER is not None and _USAGE_LOGGER is not None:
        try:
            _USAGE_LOGGER.removeHandler(_USAGE_HANDLER)
        except Exception:
            pass
        try:
            _USAGE_HANDLER.close()
        except Exception:
            pass
    _USAGE_HANDLER = None
    _USAGE_LOGGER = None
    _USAGE_LOG_ENABLED = False
    _USAGE_LOG_PATH = ""


def _coerce_positive_int(value, default: int) -> int:
    try:
        coerced = int(value)
        return coerced if coerced > 0 else default
    except Exception:
        return default


def _emit_record(record: dict, *, source: str) -> None:
    if not _USAGE_LOG_ENABLED or _USAGE_LOGGER is None:
        return
    try:
        _USAGE_LOGGER.info(json.dumps(record, ensure_ascii=False, default=str))
    except Exception as exc:
        logger.debug("Failed to write usage log (%s): %s", source, exc)


def init_usage_log(config: dict) -> None:
    """Read usage log path/rotation config from config or env var.

    Call once at startup (e.g. from agent_init or the CLI boot path).
    """
    global _USAGE_LOG_PATH, _USAGE_LOG_ENABLED, _USAGE_LOGGER
    global _USAGE_HANDLER, _USAGE_LOG_MAX_BYTES, _USAGE_LOG_BACKUP_COUNT

    path = config.get("usage_log_path") or os.environ.get("HERMES_USAGE_LOG", "")
    if not path:
        _reset_usage_log_state()
        return

    max_size_mb = config.get("usage_log_max_size_mb")
    if max_size_mb is None:
        max_size_mb = os.environ.get("HERMES_USAGE_LOG_MAX_SIZE_MB")
    backup_count = config.get("usage_log_backup_count")
    if backup_count is None:
        backup_count = os.environ.get("HERMES_USAGE_LOG_BACKUP_COUNT")

    _USAGE_LOG_MAX_BYTES = _coerce_positive_int(max_size_mb, 20) * 1024 * 1024
    _USAGE_LOG_BACKUP_COUNT = _coerce_positive_int(backup_count, 5)
    _USAGE_LOG_PATH = os.path.expanduser(path)
    Path(_USAGE_LOG_PATH).parent.mkdir(parents=True, exist_ok=True)

    logger_name = f"hermes.usage.{_USAGE_LOG_PATH}"
    if _USAGE_HANDLER is not None and _USAGE_LOGGER is not None:
        try:
            _USAGE_LOGGER.removeHandler(_USAGE_HANDLER)
        except Exception:
            pass
        try:
            _USAGE_HANDLER.close()
        except Exception:
            pass

    _USAGE_LOGGER = logging.getLogger(logger_name)
    _USAGE_LOGGER.setLevel(logging.INFO)
    _USAGE_LOGGER.propagate = False
    for handler in list(_USAGE_LOGGER.handlers):
        _USAGE_LOGGER.removeHandler(handler)
        try:
            handler.close()
        except Exception:
            pass

    _USAGE_HANDLER = RotatingFileHandler(
        _USAGE_LOG_PATH,
        maxBytes=_USAGE_LOG_MAX_BYTES,
        backupCount=_USAGE_LOG_BACKUP_COUNT,
        encoding='utf-8',
    )
    _USAGE_HANDLER.setLevel(logging.INFO)
    _USAGE_HANDLER.setFormatter(logging.Formatter('%(message)s'))
    _USAGE_LOGGER.addHandler(_USAGE_HANDLER)
    _USAGE_LOG_ENABLED = True
    logger.info(
        "Usage log enabled → %s (max=%d bytes backups=%d)",
        _USAGE_LOG_PATH,
        _USAGE_LOG_MAX_BYTES,
        _USAGE_LOG_BACKUP_COUNT,
    )


def log_bypass_call(
    *,
    command: str = "",
    route_type: str = "simple_command",
    classification_reason: str = "",
    channel: str = "",
) -> None:
    """Log a command-bypass event (LLM was not called).

    Writes a lightweight record with zero tokens and ``status=bypass``.
    Safe to call from anywhere — degrades silently if logging is disabled.
    """
    if not _USAGE_LOG_ENABLED:
        return

    record = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
        "request_id": uuid.uuid4().hex[:12],
        "model": "",
        "request_model": "",
        "response_model": "",
        "executed_model": "",
        "provider": "",
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
        "reasoning_tokens": 0,
        "estimated_cost_usd": 0.0,
        "latency_ms": 0.0,
        "route_type": route_type,
        "classification_reason": classification_reason,
        "channel": channel,
        "trimmed_messages": 0,
        "status": "bypass",
        "bypass_command": command,
        "fallback_triggered": False,
        "fallback_model": "",
        "attempt_number": 1,
        "fallback_from_model": "",
        "fallback_to_model": "",
        "fallback_reason": "",
        "route_model": "",
        "context_token_estimate": 0,
        "request_message_count": 0,
        "fallback_chain_length": 0,
        "fallback_chain_present": False,
        "runtime_provider_fallback_active": False,
        "provider_fallback_active": False,
    }
    _emit_record(record, source='bypass')


def log_llm_call(
    *,
    model: str,
    request_model: str = "",
    response_model: str = "",
    executed_model: str = "",
    provider: str,
    input_tokens: int,
    output_tokens: int,
    total_tokens: int,
    estimated_cost_usd: Optional[float],
    latency_ms: float,
    route_type: str = "normal_chat",
    classification_reason: str = "",
    channel: str = "",
    status: str = "success",
    error: str = "",
    trimmed_messages: int = 0,
    cache_read_tokens: int = 0,
    cache_write_tokens: int = 0,
    reasoning_tokens: int = 0,
    bypass_command: str = "",
    # Fallback escalation fields
    fallback_triggered: bool = False,
    fallback_model: str = "",
    attempt_number: int = 1,
    fallback_from_model: str = "",
    fallback_to_model: str = "",
    fallback_reason: str = "",
    # Routing + context observability
    route_model: str = "",
    context_token_estimate: int = 0,
    request_message_count: int = 0,
    fallback_chain_length: int = 0,
    fallback_chain_present: bool = False,
    runtime_provider_fallback_active: bool = False,
    provider_fallback_active: bool = False,
) -> None:
    """Append one structured usage record to the JSONL log file.

    Safe to call from anywhere — degrades silently if logging is disabled
    or the file cannot be written.
    """
    if not _USAGE_LOG_ENABLED:
        return

    record = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
        "request_id": uuid.uuid4().hex[:12],
        "model": model,
        "request_model": request_model or model,
        "response_model": response_model,
        "executed_model": executed_model or response_model or model,
        "provider": provider,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "cache_read_tokens": cache_read_tokens,
        "cache_write_tokens": cache_write_tokens,
        "reasoning_tokens": reasoning_tokens,
        "estimated_cost_usd": estimated_cost_usd,
        "latency_ms": round(latency_ms, 1),
        "route_type": route_type,
        "classification_reason": classification_reason,
        "channel": channel,
        "trimmed_messages": trimmed_messages,
        "status": status,
        "fallback_triggered": fallback_triggered,
        "fallback_model": fallback_model,
        "attempt_number": attempt_number,
        "fallback_from_model": fallback_from_model,
        "fallback_to_model": fallback_to_model,
        "fallback_reason": fallback_reason,
        "route_model": route_model,
        "context_token_estimate": context_token_estimate,
        "request_message_count": request_message_count,
        "fallback_chain_length": fallback_chain_length,
        "fallback_chain_present": fallback_chain_present,
        "runtime_provider_fallback_active": runtime_provider_fallback_active,
        "provider_fallback_active": provider_fallback_active,
        # NOTE: "error" intentionally excluded from the core schema to
        # prevent accidental logging of user message content via error
        # messages. Add it explicitly if you need error-type analysis.
    }
    _emit_record(record, source='llm')
