"""Decision Style read-only provider tests."""

from __future__ import annotations

import copy
from collections.abc import Mapping

from agent.decision_style import (
    DECISION_STYLE_SCHEMA_VERSION,
    DecisionStyleProvider,
    normalize_decision_style,
)

ALLOWED_TOP_LEVEL_FIELDS = (
    "schema_version",
    "style_hints",
    "provenance",
    "freshness",
    "trust",
    "redaction",
)

ALLOWED_STYLE_HINT_FIELDS = (
    "framing_preferences",
    "interaction_preferences",
    "decision_support_preferences",
)

HUMAN_MODEL_FIELDS = (
    "identity",
    "energy",
    "habit",
    "growth",
    "communication",
    "coaching",
)

DOMAIN_MODEL_FIELDS = (
    "investment",
    "health",
    "career",
    "business",
    "finance",
    "travel",
    "mental_health",
    "learning",
    "domain_model",
)

POLICY_LIKE_FIELDS = (
    "policy",
    "hard_rule",
    "hard_rules",
    "final_decision",
    "instruction_override",
    "recommendation",
)


def assert_empty_style(payload: Mapping[str, object]) -> None:
    assert tuple(payload) == ALLOWED_TOP_LEVEL_FIELDS
    assert payload == {
        "schema_version": DECISION_STYLE_SCHEMA_VERSION,
        "style_hints": {},
        "provenance": {
            "source_kind": "none",
            "source_label": None,
            "source_id": None,
            "user_confirmed": False,
        },
        "freshness": {"captured_at": None, "staleness": "unknown"},
        "trust": {"level": "none", "reason": ""},
        "redaction": {
            "contains_sensitive_fields": False,
            "safe_summary_only": True,
        },
    }


def test_none_normalizes_to_empty_read_only_shape():
    assert_empty_style(normalize_decision_style(None))


def test_explicit_input_normalizes_to_minimal_schema():
    normalized = normalize_decision_style(
        {
            "style_hints": {
                "framing_preferences": {
                    "brevity": "prefer-concise",
                    "comparison_style": "options-side-by-side",
                    "drop_me": True,
                },
                "interaction_preferences": {
                    "pace": "steady",
                    "depth_default": "practical-first",
                },
                "decision_support_preferences": {
                    "option_count_default": 3,
                    "highlight_tradeoffs": True,
                    "separate_fact_and_opinion": True,
                },
            },
            "provenance": {
                "source_kind": "explicit",
                "source_label": "turn-input",
                "source_id": "abc",
                "user_confirmed": True,
                "ignored": True,
            },
            "freshness": {
                "captured_at": "2026-06-30T00:00:00Z",
                "staleness": "fresh",
                "ignored": True,
            },
            "trust": {"level": "high", "reason": "user supplied"},
            "redaction": {
                "contains_sensitive_fields": False,
                "safe_summary_only": True,
                "ignored": True,
            },
            "ignored_top_level": True,
        }
    )

    assert tuple(normalized) == ALLOWED_TOP_LEVEL_FIELDS
    assert tuple(normalized["style_hints"]) == ALLOWED_STYLE_HINT_FIELDS
    assert normalized["style_hints"]["framing_preferences"] == {
        "brevity": "prefer-concise",
        "comparison_style": "options-side-by-side",
    }
    assert normalized["style_hints"]["interaction_preferences"] == {
        "pace": "steady",
        "depth_default": "practical-first",
    }
    assert normalized["style_hints"]["decision_support_preferences"] == {
        "option_count_default": 3,
        "highlight_tradeoffs": True,
        "separate_fact_and_opinion": True,
    }
    assert normalized["provenance"] == {
        "source_kind": "explicit",
        "source_label": "turn-input",
        "source_id": "abc",
        "user_confirmed": True,
    }
    assert normalized["freshness"] == {
        "captured_at": "2026-06-30T00:00:00Z",
        "staleness": "fresh",
    }
    assert normalized["trust"] == {"level": "high", "reason": "user supplied"}
    assert normalized["redaction"] == {
        "contains_sensitive_fields": False,
        "safe_summary_only": True,
    }


def test_unknown_keys_are_dropped():
    normalized = normalize_decision_style(
        {
            "style_hints": {
                "framing_preferences": {"brevity": "prefer-concise"},
                "unknown_bucket": {"ignored": True},
            },
            "unknown_top_level": {"ignored": True},
        }
    )

    assert "unknown_top_level" not in normalized
    assert "unknown_bucket" not in normalized["style_hints"]


def test_input_mapping_is_not_mutated():
    payload = {
        "style_hints": {
            "framing_preferences": {"brevity": "prefer-concise"},
            "unknown_bucket": {"keep": True},
        },
        "identity": {"keep": True},
        "policy": {"keep": True},
    }
    original = copy.deepcopy(payload)

    normalize_decision_style(payload)

    assert payload == original



def test_human_model_and_domain_model_keys_are_dropped():
    payload = {
        field: {"ignored": True}
        for field in HUMAN_MODEL_FIELDS + DOMAIN_MODEL_FIELDS
    }
    payload["style_hints"] = {
        "interaction_preferences": {"pace": "steady"},
    }

    normalized = normalize_decision_style(payload)

    for field in HUMAN_MODEL_FIELDS + DOMAIN_MODEL_FIELDS:
        assert field not in normalized
    assert normalized["style_hints"] == {
        "framing_preferences": {},
        "interaction_preferences": {"pace": "steady"},
        "decision_support_preferences": {},
    }



def test_policy_hard_rule_and_override_keys_are_dropped():
    payload = {
        "style_hints": {
            "framing_preferences": {"brevity": "prefer-concise"},
            "policy": {"ignored": True},
        },
        "policy": {"ignored": True},
        "hard_rule": {"ignored": True},
        "hard_rules": ["ignored"],
        "final_decision": {"ignored": True},
        "instruction_override": {"ignored": True},
        "recommendation": {"ignored": True},
    }

    normalized = normalize_decision_style(payload)

    for field in POLICY_LIKE_FIELDS:
        assert field not in normalized
    assert normalized["style_hints"] == {
        "framing_preferences": {"brevity": "prefer-concise"},
        "interaction_preferences": {},
        "decision_support_preferences": {},
    }



def test_nested_policy_payload_inside_allowed_leaf_is_dropped():
    payload = {
        "style_hints": {
            "framing_preferences": {
                "action_posture": {"policy": "always do X"},
            }
        }
    }
    original = copy.deepcopy(payload)

    normalized = normalize_decision_style(payload)

    assert normalized["style_hints"] == {
        "framing_preferences": {},
        "interaction_preferences": {},
        "decision_support_preferences": {},
    }
    assert payload == original



def test_list_payload_inside_allowed_leaf_is_dropped():
    payload = {
        "style_hints": {
            "interaction_preferences": {
                "depth_default": ["force", "ranking"],
            }
        }
    }

    normalized = normalize_decision_style(payload)

    assert normalized["style_hints"] == {
        "framing_preferences": {},
        "interaction_preferences": {},
        "decision_support_preferences": {},
    }



def test_scalar_leaf_values_are_preserved():
    normalized = normalize_decision_style(
        {
            "style_hints": {
                "framing_preferences": {
                    "brevity": "prefer-concise",
                    "comparison_style": None,
                },
                "interaction_preferences": {
                    "pace": "steady",
                    "depth_default": 1.5,
                },
                "decision_support_preferences": {
                    "option_count_default": 3,
                    "highlight_tradeoffs": True,
                },
            }
        }
    )

    assert normalized["style_hints"] == {
        "framing_preferences": {
            "brevity": "prefer-concise",
            "comparison_style": None,
        },
        "interaction_preferences": {
            "pace": "steady",
            "depth_default": 1.5,
        },
        "decision_support_preferences": {
            "option_count_default": 3,
            "highlight_tradeoffs": True,
        },
    }



def test_metadata_nested_payloads_are_dropped():
    payload = {
        "trust": {"reason": {"policy": "always do X"}},
        "provenance": {"source_label": ["force", "ranking"]},
    }
    original = copy.deepcopy(payload)

    normalized = normalize_decision_style(payload)

    assert normalized["trust"] == {"level": "none", "reason": ""}
    assert normalized["provenance"] == {
        "source_kind": "none",
        "source_label": None,
        "source_id": None,
        "user_confirmed": False,
    }
    assert payload == original



def test_metadata_scalar_values_are_preserved():
    normalized = normalize_decision_style(
        {
            "provenance": {
                "source_kind": "explicit",
                "source_label": "turn-input",
                "source_id": 123,
                "user_confirmed": True,
            },
            "freshness": {
                "captured_at": "2026-06-30T00:00:00Z",
                "staleness": None,
            },
            "trust": {"level": "high", "reason": "user supplied"},
            "redaction": {
                "contains_sensitive_fields": False,
                "safe_summary_only": True,
            },
        }
    )

    assert normalized["provenance"] == {
        "source_kind": "explicit",
        "source_label": "turn-input",
        "source_id": 123,
        "user_confirmed": True,
    }
    assert normalized["freshness"] == {
        "captured_at": "2026-06-30T00:00:00Z",
        "staleness": None,
    }
    assert normalized["trust"] == {"level": "high", "reason": "user supplied"}
    assert normalized["redaction"] == {
        "contains_sensitive_fields": False,
        "safe_summary_only": True,
    }



def test_provider_prefers_explicit_input_over_source():
    provider = DecisionStyleProvider(
        style_source={
            "style_hints": {
                "framing_preferences": {"brevity": "from-source"},
            }
        }
    )

    normalized = provider.build_decision_style(
        explicit_style={
            "style_hints": {
                "framing_preferences": {"brevity": "from-explicit"},
            }
        }
    )

    assert normalized["style_hints"]["framing_preferences"] == {
        "brevity": "from-explicit"
    }



def test_provider_reads_mapping_source_without_mutating_it():
    source = {
        "style_hints": {
            "interaction_preferences": {"pace": "steady"},
        },
        "unknown": {"keep": True},
    }
    original = copy.deepcopy(source)
    provider = DecisionStyleProvider(style_source=source)

    normalized = provider.build_decision_style()

    assert normalized["style_hints"]["interaction_preferences"] == {"pace": "steady"}
    assert source == original



def test_provider_reads_callable_source_without_mutating_result():
    source_result = {
        "style_hints": {
            "decision_support_preferences": {"highlight_tradeoffs": True},
        },
        "policy": {"keep": True},
    }
    original = copy.deepcopy(source_result)
    calls = []

    def source():
        calls.append("called")
        return source_result

    provider = DecisionStyleProvider(style_source=source)

    normalized = provider.build_decision_style()

    assert calls == ["called"]
    assert normalized["style_hints"]["decision_support_preferences"] == {
        "highlight_tradeoffs": True,
    }
    assert source_result == original



def test_provider_with_none_source_returns_empty_shape():
    provider = DecisionStyleProvider(style_source=None)

    assert_empty_style(provider.build_decision_style())



def test_provider_is_read_only_and_does_not_touch_memory_gateway_cli_or_dispatcher():
    class ReadOnlySource(dict):
        def write(self, *_args, **_kwargs):  # pragma: no cover - must not be called
            raise AssertionError("provider must not write memory")

        def update_human_model(self, *_args, **_kwargs):  # pragma: no cover
            raise AssertionError("provider must not mutate Human Model")

        def connect_gateway(self, *_args, **_kwargs):  # pragma: no cover
            raise AssertionError("provider must not connect gateway")

        def run_cli(self, *_args, **_kwargs):  # pragma: no cover
            raise AssertionError("provider must not run CLI")

        def dispatch(self, *_args, **_kwargs):  # pragma: no cover
            raise AssertionError("provider must not dispatch")

    provider = DecisionStyleProvider(
        style_source=ReadOnlySource(
            {
                "style_hints": {
                    "framing_preferences": {"brevity": "prefer-concise"},
                }
            }
        )
    )

    normalized = provider.build_decision_style()

    assert normalized["style_hints"]["framing_preferences"] == {
        "brevity": "prefer-concise"
    }
