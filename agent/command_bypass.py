"""Command bypass — handle known slash commands without calling the LLM.

Phase 1 of PR 4: Cache Optimisation.
Intercepts commands classified as ``simple_command`` by the route classifier
and generates a direct response, skipping the LLM API call entirely.

Only active when both ``routing.enabled`` and ``command_bypass.enabled``
are set to ``true`` in config.yaml.
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ── Commands that the bypass handles — safe to match by canonical name ────
_BYPASS_COMMANDS: frozenset[str] = frozenset({
    "help",
    "status",
    "sethome",
})


def _command_name(text: str) -> str:
    """Extract the canonical command name from ``/help`` or ``/sethome here``."""
    stripped = text.strip().lstrip("/")
    return stripped.split()[0].lower() if stripped else ""


def _build_help_response() -> str:
    """Generate a help message listing gateway-available commands.

    Delegates to ``hermes_cli.commands.gateway_help_lines()`` for the
    authoritative list.  Falls back to a minimal hardcoded list if the
    helper is unavailable (e.g. cli-only commands module not imported).
    """
    try:
        from hermes_cli.commands import gateway_help_lines
        lines = gateway_help_lines()
        if lines:
            return "**Hermes Agent — Available commands**\n\n" + "\n".join(lines)
    except Exception:
        logger.debug("gateway_help_lines() unavailable, using fallback")

    # Minimal fallback — covers the common gateway commands.
    return (
        "**Hermes Agent — Available commands**\n\n"
        "`/help`     — Show this help message\n"
        "`/status`   — Show session and platform information\n"
        "`/sethome`  — Set this chat as the home channel\n"
        "`/new`      — Start a new session\n"
        "`/clear`    — Clear the current session\n"
        "`/undo`     — Remove the last exchange\n"
        "`/retry`    — Retry the last message\n"
        "`/stop`     — Kill running background processes\n"
        "`/bg`       — Run a prompt in the background\n"
        "Say anything else to start a conversation."
    )


def _build_status_response(agent: Any) -> str:
    """Return a short status summary from the agent's current state."""
    import platform as _platform

    model = getattr(agent, "model", "unknown") or "unknown"
    provider = getattr(agent, "provider", "unknown") or "unknown"
    platform_name = getattr(agent, "platform", None) or "cli"
    session_id = getattr(agent, "session_id", "—") or "—"

    lines = [
        "**Hermes Agent — Status**",
        "",
        f"Model…… {model}",
        f"Provider… {provider}",
        f"Platform… {platform_name}",
        f"Session… {session_id[:12]}…" if len(session_id) > 12 else f"Session… {session_id}",
        "",
    ]

    # Include route config state when routing is enabled.
    routing = getattr(agent, "_routing_config", None) or {}
    if routing.get("enabled", False):
        route_type = getattr(agent, "_route_type", "—")
        line_parts = [f"**Routing enabled**  ({route_type})"]
        for rtype in ("normal_chat", "code_implementation", "code_design",
                       "code_debug", "code_light", "code_or_debug",
                       "long_context", "research", "simple_command"):
            rcfg = routing.get(rtype) or {}
            rmodel = rcfg.get("model", "") if isinstance(rcfg, dict) else ""
            if rmodel:
                line_parts.append(f"  {rtype}: {rmodel}")
        lines.extend(line_parts)
        lines.append("")

    # Gateway info.
    lines.append(f"Host…… {_platform.node()}")
    if provider == "openrouter" or getattr(agent, "base_url", "").find("openrouter") >= 0:
        lines.append("Cost… tracked via usage.log (JSONL)")

    return "\n".join(lines)


def _build_sethome_response(agent: Any, command_text: str) -> str:
    """Acknowledge the /sethome request.

    The actual routing change is handled by the gateway after the response
    is delivered — the purpose of the bypass is simply to confirm the
    intent without consuming LLM tokens.
    """
    return (
        "**/sethome** — This chat has been requested as the home channel.\n"
        "The gateway will route future scheduled deliveries here."
    )


def _log_bypass(agent: Any, command: str, response_text: str) -> None:
    """Log a bypass event to the usage log."""
    try:
        from agent.usage_logger import log_bypass_call
        log_bypass_call(
            command=command,
            route_type="simple_command",
            channel=getattr(agent, "platform", ""),
        )
    except Exception:
        pass  # Logging is best-effort


# ── Public API ──────────────────────────────────────────────────────────


def is_bypass_enabled(agent: Any) -> bool:
    """Check whether command bypass is enabled in the agent's config.

    Requires **both** ``routing.enabled`` **and** ``command_bypass.enabled``.
    """
    routing = getattr(agent, "_routing_config", None) or {}
    if not routing.get("enabled", False):
        return False
    return bool(getattr(agent, "_command_bypass_enabled", True))


def handle_simple_command(agent: Any, user_message: str) -> Optional[Dict[str, Any]]:
    """Handle a ``simple_command`` route without calling the LLM.

    Returns a result dict suitable for ``run_conversation``'s return type,
    or ``None`` when the command should fall through to the LLM (unknown
    command, bypass disabled, etc.).
    """
    command = _command_name(user_message)
    if not command or command not in _BYPASS_COMMANDS:
        return None

    # Build the appropriate response.
    if command == "help":
        response_text = _build_help_response()
    elif command == "status":
        response_text = _build_status_response(agent)
    elif command == "sethome":
        response_text = _build_sethome_response(agent, user_message)
    else:
        return None  # Should not reach here, but be safe

    # Log the bypass event.
    _log_bypass(agent, command, response_text)

    logger.info(
        "Command bypass for /%s (%d chars) — LLM skipped",
        command, len(response_text),
    )

    # Return a minimal result dict compatible with run_conversation()
    return {
        "final_response": response_text,
        "last_reasoning": "",
        "messages": [],
        "api_calls": 0,
        "completed": True,
        "turn_exit_reason": "command_bypass",
        "failed": False,
        "partial": False,
        "interrupted": False,
        "response_transformed": False,
        "response_previewed": False,
        "model": getattr(agent, "model", ""),
        "provider": getattr(agent, "provider", ""),
        "base_url": getattr(agent, "base_url", ""),
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
        "reasoning_tokens": 0,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "last_prompt_tokens": 0,
        "estimated_cost_usd": 0.0,
        "cost_status": "bypassed",
        "cost_source": "",
        "session_id": getattr(agent, "session_id", ""),
    }
