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
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Module-level state — initialised once at startup.
_USAGE_LOG_PATH: str = ""
_USAGE_LOG_ENABLED: bool = False


def init_usage_log(config: dict) -> None:
    """Read the usage_log_path from config or env var.

    Call once at startup (e.g. from agent_init or the CLI boot path).
    """
    global _USAGE_LOG_PATH, _USAGE_LOG_ENABLED
    path = config.get("usage_log_path") or os.environ.get("HERMES_USAGE_LOG", "")
    if path:
        _USAGE_LOG_PATH = os.path.expanduser(path)
        _USAGE_LOG_ENABLED = True
        Path(_USAGE_LOG_PATH).parent.mkdir(parents=True, exist_ok=True)
        logger.info("Usage log enabled → %s", _USAGE_LOG_PATH)


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
    }

    try:
        with open(_USAGE_LOG_PATH, "a") as f:
            f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
    except Exception as exc:
        logger.debug("Failed to write usage log (bypass): %s", exc)


def log_llm_call(
    *,
    model: str,
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
        # NOTE: "error" intentionally excluded from the core schema to
        # prevent accidental logging of user message content via error
        # messages. Add it explicitly if you need error-type analysis.
    }

    try:
        with open(_USAGE_LOG_PATH, "a") as f:
            f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
    except Exception as exc:
        logger.debug("Failed to write usage log: %s", exc)
