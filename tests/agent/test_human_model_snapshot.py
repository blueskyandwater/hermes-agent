"""Explicit Human Model snapshot normalizer tests."""

from __future__ import annotations

import copy
from collections.abc import Mapping

from agent.human_model_snapshot import (
    HumanModelSnapshotProvider,
    normalize_human_model_snapshot,
)


ALLOWED_HUMAN_MODEL_FIELDS = (
    "identity",
    "energy",
    "habit",
    "growth",
    "communication",
    "coaching",
)

DOMAIN_SPECIFIC_FIELDS = (
    "investment",
    "health",
    "career",
    "business",
    "finance",
    "travel",
    "mental_health",
    "learning",
)


def assert_empty_snapshot(snapshot: Mapping[str, Mapping[str, object]]) -> None:
    assert tuple(snapshot) == ALLOWED_HUMAN_MODEL_FIELDS
    assert snapshot == {field: {} for field in ALLOWED_HUMAN_MODEL_FIELDS}


def test_none_normalizes_to_six_empty_sections():
    assert_empty_snapshot(normalize_human_model_snapshot(None))


def test_empty_mapping_normalizes_to_six_empty_sections():
    assert_empty_snapshot(normalize_human_model_snapshot({}))


def test_partial_mapping_fills_missing_sections_with_empty_dicts():
    normalized = normalize_human_model_snapshot(
        {
            "identity": {"values": ["autonomy"]},
            "communication": {"style": "concise"},
        }
    )

    assert normalized == {
        "identity": {"values": ["autonomy"]},
        "energy": {},
        "habit": {},
        "growth": {},
        "communication": {"style": "concise"},
        "coaching": {},
    }


def test_unknown_keys_are_excluded():
    normalized = normalize_human_model_snapshot(
        {
            "identity": {"values": ["autonomy"]},
            "unknown_key": {"ignored": True},
        }
    )

    assert "unknown_key" not in normalized
    assert normalized["identity"] == {"values": ["autonomy"]}


def test_decision_style_is_excluded():
    normalized = normalize_human_model_snapshot(
        {
            "decision_style": {"mode": "fast"},
            "coaching": {"stance": "supportive"},
        }
    )

    assert "decision_style" not in normalized
    assert normalized["coaching"] == {"stance": "supportive"}


def test_domain_specific_keys_are_excluded():
    snapshot: dict[str, object] = {field: {"ignored": True} for field in DOMAIN_SPECIFIC_FIELDS}
    snapshot["growth"] = {"direction": "iterative"}

    normalized = normalize_human_model_snapshot(snapshot)

    for field in DOMAIN_SPECIFIC_FIELDS:
        assert field not in normalized
    assert normalized["growth"] == {"direction": "iterative"}


def test_input_mapping_is_not_mutated():
    snapshot = {
        "identity": {"values": ["autonomy"]},
        "unknown_key": {"keep": True},
        "decision_style": {"keep": True},
        "investment": {"keep": True},
    }
    original = copy.deepcopy(snapshot)

    normalize_human_model_snapshot(snapshot)

    assert snapshot == original


def test_top_level_keys_are_limited_to_six_human_model_sections():
    normalized = normalize_human_model_snapshot(
        {
            "identity": {"values": ["autonomy"]},
            "unknown_key": {"ignored": True},
            "decision_style": {"ignored": True},
            "investment": {"ignored": True},
        }
    )

    assert tuple(normalized) == ALLOWED_HUMAN_MODEL_FIELDS


def test_each_returned_value_is_a_mapping():
    normalized = normalize_human_model_snapshot(
        {
            "identity": {"values": ["autonomy"]},
            "energy": "low",
            "habit": None,
        }
    )

    assert all(isinstance(value, Mapping) for value in normalized.values())
    assert normalized["energy"] == {}
    assert normalized["habit"] == {}


def test_provider_exists():
    assert HumanModelSnapshotProvider is not None


def test_provider_normalizes_explicit_snapshot():
    provider = HumanModelSnapshotProvider()

    normalized = provider.build_snapshot(
        explicit_snapshot={
            "identity": {"values": ["autonomy"]},
            "communication": {"style": "concise"},
            "unknown": {"ignored": True},
        }
    )

    assert normalized == {
        "identity": {"values": ["autonomy"]},
        "energy": {},
        "habit": {},
        "growth": {},
        "communication": {"style": "concise"},
        "coaching": {},
    }


def test_provider_returns_only_allowed_six_sections():
    provider = HumanModelSnapshotProvider()

    normalized = provider.build_snapshot(
        explicit_snapshot={
            "identity": {"values": ["autonomy"]},
            "decision_style": {"speed": "fast"},
            "investment": {"risk": "balanced"},
            "domain_model": {"ignored": True},
            "unknown": {"ignored": True},
        }
    )

    assert tuple(normalized) == ALLOWED_HUMAN_MODEL_FIELDS
    assert "decision_style" not in normalized
    assert "investment" not in normalized
    assert "domain_model" not in normalized
    assert "unknown" not in normalized


def test_provider_prefers_explicit_snapshot_over_source():
    provider = HumanModelSnapshotProvider(
        snapshot_source={"identity": {"values": ["from-source"]}}
    )

    normalized = provider.build_snapshot(
        explicit_snapshot={"identity": {"values": ["from-explicit"]}}
    )

    assert normalized["identity"] == {"values": ["from-explicit"]}


def test_provider_reads_mapping_source_without_mutating_it():
    source = {
        "identity": {"values": ["from-source"]},
        "unknown": {"keep": True},
    }
    original = copy.deepcopy(source)
    provider = HumanModelSnapshotProvider(snapshot_source=source)

    normalized = provider.build_snapshot()

    assert normalized["identity"] == {"values": ["from-source"]}
    assert source == original


def test_provider_reads_callable_source_without_mutating_result():
    source_result = {
        "growth": {"direction": "iterative"},
        "decision_style": {"keep": True},
    }
    original = copy.deepcopy(source_result)
    calls = []

    def source():
        calls.append("called")
        return source_result

    provider = HumanModelSnapshotProvider(snapshot_source=source)

    normalized = provider.build_snapshot()

    assert calls == ["called"]
    assert normalized["growth"] == {"direction": "iterative"}
    assert "decision_style" not in normalized
    assert source_result == original


def test_provider_with_none_source_returns_empty_normalized_snapshot():
    provider = HumanModelSnapshotProvider(snapshot_source=None)

    assert_empty_snapshot(provider.build_snapshot())


def test_provider_does_not_mutate_explicit_snapshot():
    explicit_snapshot = {
        "identity": {"values": ["autonomy"]},
        "unknown": {"keep": True},
        "decision_style": {"keep": True},
        "investment": {"keep": True},
    }
    original = copy.deepcopy(explicit_snapshot)
    provider = HumanModelSnapshotProvider()

    provider.build_snapshot(explicit_snapshot=explicit_snapshot)

    assert explicit_snapshot == original


def test_provider_does_not_call_memory_write_or_runtime_hooks():
    class ReadOnlySource(dict):
        def write(self, *_args, **_kwargs):  # pragma: no cover - must not be called
            raise AssertionError("provider must not write memory")

        def update_human_model(self, *_args, **_kwargs):  # pragma: no cover
            raise AssertionError("provider must not mutate Human Model")

        def connect_runtime(self, *_args, **_kwargs):  # pragma: no cover
            raise AssertionError("provider must not connect runtime")

    provider = HumanModelSnapshotProvider(
        snapshot_source=ReadOnlySource({"coaching": {"stance": "supportive"}})
    )

    normalized = provider.build_snapshot()

    assert normalized["coaching"] == {"stance": "supportive"}
