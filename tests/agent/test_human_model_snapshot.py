"""Explicit Human Model snapshot normalizer tests."""

from __future__ import annotations

import copy
from collections.abc import Mapping

from agent.human_model_snapshot import normalize_human_model_snapshot


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
