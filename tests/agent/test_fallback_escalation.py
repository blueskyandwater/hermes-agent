"""Tests for self-escalation sentinel handling in fallback_escalation."""

import pytest

from agent import fallback_escalation


def test_self_escalation_defaults_disabled_when_not_configured():
    fallback_escalation.init_fallback_config({
        "fallback": {
            "enabled": True,
            "models": {"x": "y"},
        }
    })

    assert fallback_escalation.is_self_escalation_enabled() is False
    assert fallback_escalation.get_self_escalation_sentinel() == "ESCALATE_TO_STRONGER_MODEL"


def test_self_escalation_detects_simple_form_with_reason_and_prefix():
    fallback_escalation.init_fallback_config({
        "fallback": {
            "enabled": True,
            "self_escalation": {
                "enabled": True,
                "sentinel": "ESCALATE_TO_STRONGER_MODEL",
            },
            "models": {},
        }
    })

    assert fallback_escalation.detect_self_escalation_request(
        "ESCALATE_TO_STRONGER_MODEL: Need a model with deeper reasoning"
    ) == "Need a model with deeper reasoning"

    assert fallback_escalation.detect_self_escalation_request(
        "[System: ESCALATE_TO_STRONGER_MODEL - please escalate]"
    ) == "please escalate"


@pytest.mark.parametrize(
    "text",
    [
        "Please continue as normal",
        "not a request: escalate_to_strongermodel",
    ],
)
def test_self_escalation_not_detected_for_non_matching(text: str):
    fallback_escalation.init_fallback_config({
        "fallback": {
            "enabled": True,
            "self_escalation": {"enabled": True},
            "models": {},
        }
    })

    assert fallback_escalation.detect_self_escalation_request(text) is None


def test_self_escalation_resolves_fallback_model_map():
    fallback_escalation.init_fallback_config({
        "fallback": {
            "enabled": True,
            "self_escalation": {
                "enabled": True,
            },
            "models": {
                "deepseek/deepseek-chat-v4-flash": "anthropic/claude-sonnet-4",
            },
        }
    })

    assert (
        fallback_escalation.get_fallback_model("deepseek/deepseek-chat-v4-flash")
        == "anthropic/claude-sonnet-4"
    )
    assert fallback_escalation.get_fallback_model("unknown/model") is None
