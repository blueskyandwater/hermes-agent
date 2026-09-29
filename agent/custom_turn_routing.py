"""Fork routing policy at the extracted turn boundaries.

Request model overrides never mutate the configured primary runtime. Provider
fallback always outranks a primary-provider route or model escalation.
"""
from typing import Any, Optional
import logging
from agent.iteration_budget import IterationBudget
from agent.ephemeral_decision_support import build_ephemeral_decision_support_if_allowed

logger = logging.getLogger(__name__)


def _apply_route_max_turns(agent: Any, route_max_turns: Optional[int], base_max_iterations: int) -> bool:
    if not route_max_turns or route_max_turns == agent.max_iterations:
        return False
    agent.max_iterations = route_max_turns
    agent._route_max_turns = route_max_turns
    agent.iteration_budget = IterationBudget(route_max_turns)
    return True


def _with_ephemeral_decision_support_for_api_msg(api_msg, *, is_current_turn_user,
                                               decision_support_context, inject_decision_support=False):
    copied = api_msg.copy()
    if not is_current_turn_user or copied.get("role") != "user" or not isinstance(copied.get("content", ""), str):
        return copied
    guarded = build_ephemeral_decision_support_if_allowed(
        decision_support_context, inject_decision_support=inject_decision_support)
    if guarded is not None:
        copied["content"] = copied.get("content", "") + "\n\n" + guarded
    return copied


def reset_turn(agent):
    agent._fallback_attempted = False
    agent._fallback_from_model = agent._fallback_to_model = agent._fallback_reason = ""
    agent._custom_model_override = None
    agent._custom_override_provider = None
    agent._self_escalation_fallback_active = False
    agent._self_escalation_fallback_model = None
    agent._request_model_used = agent._actual_model_used = agent._executed_model_used = agent.model
    agent._response_model_reported = ""
    agent._trimmed_count = 0


def apply_request_route(agent, api_kwargs, original_user_message, messages, approx_tokens):
    from agent.route_classifier import classify_message, get_route_model, get_route_max_turns, get_fallback_route_model
    config = getattr(agent, "_routing_config", {})
    enabled = isinstance(config, dict) and bool(config.get("enabled", False))
    if enabled:
        agent._route_type, agent._classification_reason = classify_message(
            original_user_message, messages, context_token_estimate=approx_tokens)
        agent._route_model = get_route_model(agent._route_type, config)
        _apply_route_max_turns(agent, get_route_max_turns(agent._route_type, config),
                              getattr(agent, "_configured_max_iterations", agent.max_iterations))
    else:
        agent._route_type, agent._route_model, agent._classification_reason = "normal_chat", "", ""
    provider_fallback = bool(getattr(agent, "_fallback_activated", False) or
                             getattr(agent, "_runtime_provider_fallback_active", False))
    override = getattr(agent, "_custom_model_override", None)
    if provider_fallback:
        # A provider transition invalidates every primary-provider override.
        agent._custom_model_override = None
        if enabled:
            model = get_fallback_route_model(agent._route_type, config)
            if model:
                api_kwargs["model"] = model
    elif override and getattr(agent, "_custom_override_provider", None) == agent.provider:
        api_kwargs["model"] = override
    elif enabled and agent._route_model:
        api_kwargs["model"] = agent._route_model


def note_request_model(agent, api_kwargs):
    agent._actual_model_used = agent._request_model_used = api_kwargs.get("model") or agent.model
    agent._executed_model_used = agent._request_model_used
    agent._response_model_reported = ""


def escalate_model(agent, model, *, reason):
    from agent.fallback_escalation import get_fallback_model, is_fallback_enabled
    if (not is_fallback_enabled() or getattr(agent, "_fallback_attempted", False)
            or getattr(agent, "_fallback_activated", False)
            or getattr(agent, "_runtime_provider_fallback_active", False)):
        return False
    target = get_fallback_model(model)
    if not target:
        return False
    agent._fallback_attempted = True
    agent._fallback_from_model, agent._fallback_to_model, agent._fallback_reason = model, target, reason
    agent._custom_model_override, agent._custom_override_provider = target, agent.provider
    agent._buffer_status(f"⚠️ {model} — retrying with {target} ({reason})")
    return True
