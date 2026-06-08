"""Model-level fallback escalation — switch model on API failure.

When the selected model fails with a transient error (timeout, 5xx, 429),
this module allows retrying with a different model on the same provider.

Config:
  fallback:
    enabled: true           # Enable model-level fallback
    max_attempts: 2         # 1 primary + 1 fallback attempt
    models:
      deepseek/deepseek-chat-v4-flash:
        fallback: anthropic/claude-sonnet-4
      google/gemini-2.5-flash:
        fallback: anthropic/claude-sonnet-4
      anthropic/claude-sonnet-4:
        fallback: deepseek/deepseek-chat-v4-flash

Transient error types considered for fallback:
  - API timeout (connection timeout, read timeout)
  - Provider unavailable (503, 529)
  - Model unavailable (502, 503, 504, 524)
  - HTTP 500, 5xx
  - Rate limit (429)

Non-transient errors (4xx except 429) are NOT escalated.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Optional

logger = logging.getLogger(__name__)


_FALLBACK_CONFIG_ENABLED: bool = False
_FALLBACK_CONFIG: dict = {}

# Model → fallback model mapping, populated from config
_FALLBACK_MODEL_MAP: dict[str, str] = {}

# Optional self-escalation policy: allows a model to request a stronger model
# by emitting a sentinel phrase in its response.
_SELF_ESCALATION_CONFIG_ENABLED: bool = False
_SELF_ESCALATION_SENTINEL: str = "ESCALATE_TO_STRONGER_MODEL"


def init_fallback_config(config: dict) -> None:
    """Read fallback config from the agent config dict."""
    global _FALLBACK_CONFIG_ENABLED, _FALLBACK_CONFIG, _FALLBACK_MODEL_MAP
    global _SELF_ESCALATION_CONFIG_ENABLED, _SELF_ESCALATION_SENTINEL
    cfg = config.get("fallback", {})
    _FALLBACK_CONFIG_ENABLED = bool(cfg.get("enabled", False))
    _FALLBACK_CONFIG = cfg
    _SELF_ESCALATION_CONFIG_ENABLED = bool(
        cfg.get("self_escalation", {}).get("enabled", False)
    )
    _SELF_ESCALATION_SENTINEL = str(
        cfg.get("self_escalation", {}).get("sentinel", "ESCALATE_TO_STRONGER_MODEL")
    )
    _FALLBACK_MODEL_MAP = {}
    models = cfg.get("models", {})
    if isinstance(models, dict):
        for primary, opts in models.items():
            if isinstance(opts, dict) and opts.get("fallback"):
                _FALLBACK_MODEL_MAP[primary] = opts["fallback"]
            elif isinstance(opts, str):
                _FALLBACK_MODEL_MAP[primary] = opts

def is_fallback_enabled() -> bool:
    """Is model-level fallback configured and enabled?"""
    return _FALLBACK_CONFIG_ENABLED


def get_fallback_model(selected_model: str) -> Optional[str]:
    """Return the fallback model for the given selected model, or None."""
    return _FALLBACK_MODEL_MAP.get(selected_model)


def is_self_escalation_enabled() -> bool:
    """Is model self-escalation enabled in config?"""
    return _SELF_ESCALATION_CONFIG_ENABLED


def get_self_escalation_sentinel() -> str:
    """Return the configured escalation sentinel string."""
    return (_SELF_ESCALATION_SENTINEL or "ESCALATE_TO_STRONGER_MODEL").strip()


def detect_self_escalation_request(text: str) -> Optional[str]:
    """Detect self-escalation request in assistant final response.

    Accepted formats:
      - ESCALATE_TO_STRONGER_MODEL
      - ESCALATE_TO_STRONGER_MODEL: need stronger reasoning
      - [System: ESCALATE_TO_STRONGER_MODEL — model is too weak]

    Returns a stripped reason string when detected, else None.
    """
    if not text:
        return None

    sentinel = get_self_escalation_sentinel()
    if not sentinel:
        return None

    pattern = re.compile(
        rf"^(?:\s*\[?System:\s*)?\s*{re.escape(sentinel)}\b(?:\s*[:：\-—]\s*(?P<reason>.*))?",
        re.IGNORECASE | re.MULTILINE,
    )
    match = pattern.search(text)
    if not match:
        return None

    reason = (match.group("reason") or "").strip()
    return reason.rstrip("] ")


def get_max_attempts() -> int:
    """Return max attempts (primary + fallback)."""
    return int(_FALLBACK_CONFIG.get("max_attempts", 2))


def is_transient_api_error(api_error: Exception, status_code: Optional[int]) -> bool:
    """Check if an error is transient and worth falling back on.

    Returns True for:
     - Timeout errors (Timeout, ConnectionError, ReadTimeout, etc.)
     - HTTP 5xx (500, 502, 503, 504, 524, 529)
     - Rate limit (429)
     - Network errors (ConnectionError, ConnectionReset)
    """
    if status_code is not None:
        if status_code == 429:
            return True
        if 500 <= status_code < 600:
            return True
        # 4xx except 429 is NOT transient
        return False

    # No status code — check error type
    err_name = type(api_error).__name__
    err_msg = str(api_error).lower()

    if err_name in (
        "Timeout", "ReadTimeout", "ConnectTimeout",
        "ConnectionError", "ConnectionResetError",
        "ConnectionAbortedError",
    ):
        return True

    if any(phrase in err_msg for phrase in (
        "timed out", "timeout", "connection reset",
        "connection refused", "connection closed",
        "connection aborted", "network error",
        "service unavailable", "overloaded",
        "upstream", "provider", "model overloaded",
    )):
        return True

    return False


# ── Fallback reason derivation ─────────────────────────────────────────

def derive_fallback_reason(classified, api_error=None, status_code=None) -> str:
    """Map an API error to a fallback_reason string for usage.log.

    Categories:
      - api_error       — generic API error (5xx, timeout, rate_limit, etc.)
      - context_overflow — context/token limit exceeded
      - empty_response   — model returned no content
      - unknown          — unclassifiable
    """
    if classified is not None:
        try:
            from agent.error_classifier import FailoverReason
            r = classified.reason
            if r == FailoverReason.context_overflow:
                return "context_overflow"
            if r == FailoverReason.payload_too_large:
                return "api_error"
            if r in (FailoverReason.timeout, FailoverReason.rate_limit,
                     FailoverReason.billing, FailoverReason.overloaded,
                     FailoverReason.server_error, FailoverReason.model_not_found,
                     FailoverReason.content_policy_blocked,
                     FailoverReason.provider_policy_blocked):
                return "api_error"
        except Exception:
            pass

    # Fallback: derive from error type/status
    if status_code is not None:
        if status_code == 429:
            return "api_error"
        if 500 <= status_code < 600:
            return "api_error"

    if api_error is not None:
        err_name = type(api_error).__name__
        if err_name in ("Timeout", "ReadTimeout", "ConnectTimeout"):
            return "api_error"

    return "unknown"
