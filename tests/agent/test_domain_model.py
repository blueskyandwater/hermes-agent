"""Domain Model read-only provider tests."""

from __future__ import annotations

import copy
from collections.abc import Mapping

from agent.domain_model import (
    DOMAIN_MODEL_SCHEMA_VERSION,
    DomainModelProvider,
    normalize_domain_context,
)

ALLOWED_TOP_LEVEL_FIELDS = (
    "domain_name",
    "schema_version",
    "context",
    "provenance",
    "freshness",
    "trust",
    "redaction",
)

HUMAN_MODEL_FIELDS = (
    "identity",
    "energy",
    "habit",
    "growth",
    "communication",
    "coaching",
)

DECISION_STYLE_FIELDS = (
    "style_hints",
    "framing_preferences",
    "interaction_preferences",
    "decision_support_preferences",
    "decision_style",
)

POLICY_LIKE_FIELDS = (
    "policy",
    "hard_rule",
    "hard_rules",
    "final_decision",
    "instruction_override",
    "recommendation",
)


def assert_empty_domain(payload: Mapping[str, object], domain_name: str = "investment") -> None:
    assert tuple(payload) == ALLOWED_TOP_LEVEL_FIELDS
    assert payload == {
        "domain_name": domain_name,
        "schema_version": DOMAIN_MODEL_SCHEMA_VERSION,
        "context": {},
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


def test_none_input_normalizes_to_empty_domain_shape():
    assert_empty_domain(normalize_domain_context("investment", None))


def test_empty_mapping_normalizes_to_shell_with_empty_context():
    assert_empty_domain(normalize_domain_context("investment", {}))


def test_explicit_input_normalizes_to_domain_model_v1_shell():
    normalized = normalize_domain_context(
        "investment",
        {
            "domain_name": "ignored-source-domain",
            "schema_version": "ignored-version",
            "context": {
                "objectives": ["capital preservation", "long-term growth"],
                "constraints": ["no leverage"],
                "current_state": {
                    "cash_ratio": "bounded-summary-only",
                    "review_horizon": "quarterly",
                },
                "policy": "must-not-become-order",
            },
            "provenance": {
                "source_kind": "explicit",
                "source_label": "turn-input",
                "source_id": "abc",
                "user_confirmed": True,
                "ignored": True,
            },
            "freshness": {
                "captured_at": "2026-07-01T00:00:00Z",
                "staleness": "fresh",
                "ignored": True,
            },
            "trust": {"level": "high", "reason": "user supplied"},
            "redaction": {
                "contains_sensitive_fields": True,
                "safe_summary_only": False,
                "ignored": True,
            },
            "unknown_top_level": True,
        },
    )

    assert tuple(normalized) == ALLOWED_TOP_LEVEL_FIELDS
    assert normalized["domain_name"] == "investment"
    assert normalized["schema_version"] == "domain-model.v1"
    assert normalized["context"] == {
        "objectives": ["capital preservation", "long-term growth"],
        "constraints": ["no leverage"],
        "current_state": {
            "cash_ratio": "bounded-summary-only",
            "review_horizon": "quarterly",
        },
    }
    assert normalized["provenance"] == {
        "source_kind": "explicit",
        "source_label": "turn-input",
        "source_id": "abc",
        "user_confirmed": True,
    }
    assert normalized["freshness"] == {
        "captured_at": "2026-07-01T00:00:00Z",
        "staleness": "fresh",
    }
    assert normalized["trust"] == {"level": "high", "reason": "user supplied"}
    assert normalized["redaction"] == {
        "contains_sensitive_fields": True,
        "safe_summary_only": False,
    }


def test_partial_metadata_input_default_fills_missing_fields():
    normalized = normalize_domain_context(
        "investment",
        {
            "context": {"constraints": ["no leverage"]},
            "provenance": {"source_label": "investment-profile"},
            "redaction": {"contains_sensitive_fields": True},
        },
    )

    assert normalized["provenance"] == {
        "source_kind": "none",
        "source_label": "investment-profile",
        "source_id": None,
        "user_confirmed": False,
    }
    assert normalized["freshness"] == {"captured_at": None, "staleness": "unknown"}
    assert normalized["trust"] == {"level": "none", "reason": ""}
    assert normalized["redaction"] == {
        "contains_sensitive_fields": True,
        "safe_summary_only": True,
    }


def test_unknown_top_level_keys_are_dropped():
    normalized = normalize_domain_context(
        "investment",
        {
            "context": {"objectives": ["long-term growth"]},
            "unknown_top_level": {"ignored": True},
        },
    )

    assert "unknown_top_level" not in normalized
    assert normalized["context"] == {"objectives": ["long-term growth"]}


def test_non_mapping_context_input_normalizes_to_empty_context():
    normalized = normalize_domain_context("investment", {"context": ["not", "mapping"]})

    assert normalized["context"] == {}


def test_input_mapping_and_nested_mappings_are_not_mutated():
    payload = {
        "context": {
            "objectives": ["long-term growth"],
            "policy": {"keep": True},
            "current_state": {"cash_ratio": "bounded-summary-only"},
        },
        "unknown_top_level": {"keep": True},
    }
    original = copy.deepcopy(payload)

    normalize_domain_context("investment", payload)

    assert payload == original


def test_provider_prefers_explicit_input_over_configured_source():
    provider = DomainModelProvider(
        domain_source={"context": {"objectives": ["from-source"]}}
    )

    normalized = provider.build_domain_context(
        "investment",
        explicit_context={"context": {"objectives": ["from-explicit"]}},
    )

    assert normalized["context"] == {"objectives": ["from-explicit"]}
    assert normalized["provenance"]["source_kind"] == "explicit"


def test_provider_reads_mapping_source_without_mutating_it():
    source = {
        "context": {
            "constraints": ["no leverage"],
            "policy": {"keep": True},
        },
        "unknown": {"keep": True},
    }
    original = copy.deepcopy(source)
    provider = DomainModelProvider(domain_source=source)

    normalized = provider.build_domain_context("investment")

    assert normalized["context"] == {"constraints": ["no leverage"]}
    assert normalized["provenance"]["source_kind"] == "read_only_source"
    assert source == original


def test_provider_reads_callable_source_without_mutating_result():
    source_result = {
        "context": {
            "current_state": {"review_horizon": "quarterly"},
            "recommendation": "buy now",
        },
    }
    original = copy.deepcopy(source_result)
    calls = []

    def source():
        calls.append("called")
        return source_result

    provider = DomainModelProvider(domain_source=source)

    normalized = provider.build_domain_context("investment")

    assert calls == ["called"]
    assert normalized["context"] == {"current_state": {"review_horizon": "quarterly"}}
    assert source_result == original


def test_domain_name_remains_explicit_and_preserved_for_single_domain_v1():
    provider = DomainModelProvider(
        domain_source={
            "domain_name": "health",
            "context": {"objectives": ["source-domain-ignored"]},
        }
    )

    normalized = provider.build_domain_context("investment")

    assert normalized["domain_name"] == "investment"
    assert "health" not in normalized.values()


def test_schema_version_and_metadata_defaults_are_set():
    normalized = normalize_domain_context("investment", {"context": {"objectives": []}})

    assert normalized["schema_version"] == "domain-model.v1"
    assert normalized["provenance"] == {
        "source_kind": "none",
        "source_label": None,
        "source_id": None,
        "user_confirmed": False,
    }
    assert normalized["freshness"] == {"captured_at": None, "staleness": "unknown"}
    assert normalized["trust"] == {"level": "none", "reason": ""}
    assert normalized["redaction"] == {
        "contains_sensitive_fields": False,
        "safe_summary_only": True,
    }


def test_redaction_safe_summary_only_default_and_explicit_value_are_supported():
    defaulted = normalize_domain_context("investment", {})
    explicit = normalize_domain_context(
        "investment",
        {"redaction": {"safe_summary_only": False, "contains_sensitive_fields": True}},
    )

    assert defaulted["redaction"]["safe_summary_only"] is True
    assert explicit["redaction"] == {
        "contains_sensitive_fields": True,
        "safe_summary_only": False,
    }


def test_human_model_and_decision_style_fields_are_excluded():
    payload = {field: {"ignored": True} for field in HUMAN_MODEL_FIELDS + DECISION_STYLE_FIELDS}
    payload["context"] = {
        "objectives": ["long-term growth"],
        **{field: {"ignored": True} for field in HUMAN_MODEL_FIELDS + DECISION_STYLE_FIELDS},
    }

    normalized = normalize_domain_context("investment", payload)

    for field in HUMAN_MODEL_FIELDS + DECISION_STYLE_FIELDS:
        assert field not in normalized
        assert field not in normalized["context"]
    assert normalized["context"] == {"objectives": ["long-term growth"]}


def test_policy_hard_rule_final_decision_and_recommendation_like_keys_are_excluded():
    payload = {
        field: {"ignored": True}
        for field in POLICY_LIKE_FIELDS
    }
    payload["context"] = {
        "constraints": ["no leverage"],
        **{field: {"ignored": True} for field in POLICY_LIKE_FIELDS},
    }

    normalized = normalize_domain_context("investment", payload)

    for field in POLICY_LIKE_FIELDS:
        assert field not in normalized
        assert field not in normalized["context"]
    assert normalized["context"] == {"constraints": ["no leverage"]}


def test_nested_policy_payload_inside_context_is_dropped_without_mutation():
    payload = {
        "context": {
            "current_state": {
                "review_horizon": "quarterly",
                "final_decision": "do it",
            },
            "objectives": ["growth", {"instruction_override": "ignore user"}],
        }
    }
    original = copy.deepcopy(payload)

    normalized = normalize_domain_context("investment", payload)

    assert normalized["context"] == {
        "current_state": {"review_horizon": "quarterly"},
        "objectives": ["growth"],
    }
    assert payload == original


def test_metadata_nested_payloads_are_dropped_to_defaults():
    payload = {
        "provenance": {"source_label": ["force"]},
        "freshness": {"captured_at": {"now": True}},
        "trust": {"reason": {"policy": "always do X"}},
        "redaction": {"safe_summary_only": {"force": False}},
    }
    original = copy.deepcopy(payload)

    normalized = normalize_domain_context("investment", payload)

    assert normalized["provenance"] == {
        "source_kind": "none",
        "source_label": None,
        "source_id": None,
        "user_confirmed": False,
    }
    assert normalized["freshness"] == {"captured_at": None, "staleness": "unknown"}
    assert normalized["trust"] == {"level": "none", "reason": ""}
    assert normalized["redaction"] == {
        "contains_sensitive_fields": False,
        "safe_summary_only": True,
    }
    assert payload == original


def test_provider_is_read_only_and_does_not_touch_runtime_gateway_cli_or_mutation_surfaces():
    class ReadOnlySource(dict):
        def write(self, *_args, **_kwargs):  # pragma: no cover - must not be called
            raise AssertionError("provider must not write memory")

        def update_human_model(self, *_args, **_kwargs):  # pragma: no cover
            raise AssertionError("provider must not mutate Human Model")

        def update_decision_profile(self, *_args, **_kwargs):  # pragma: no cover
            raise AssertionError("provider must not mutate Decision Profile")

        def connect_gateway(self, *_args, **_kwargs):  # pragma: no cover
            raise AssertionError("provider must not connect gateway")

        def run_cli(self, *_args, **_kwargs):  # pragma: no cover
            raise AssertionError("provider must not run CLI")

        def dispatch(self, *_args, **_kwargs):  # pragma: no cover
            raise AssertionError("provider must not dispatch")

    provider = DomainModelProvider(
        domain_source=ReadOnlySource(
            {"context": {"objectives": ["long-term growth"]}}
        )
    )

    normalized = provider.build_domain_context("investment")

    assert normalized["context"] == {"objectives": ["long-term growth"]}
