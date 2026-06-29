"""Utilities for normalizing explicit Human Model snapshots.

This module is intentionally pure and source-agnostic. It only accepts an
explicit caller-provided snapshot and returns the six Decision Framework Human
Model sections that are safe to pass onward. It does not read memory, parse
profile/docs, mutate Human Model state, or connect to runtime surfaces.
"""

from __future__ import annotations

from typing import Any, Mapping

__all__ = ["HUMAN_MODEL_SNAPSHOT_FIELDS", "normalize_human_model_snapshot"]

HUMAN_MODEL_SNAPSHOT_FIELDS = (
    "identity",
    "energy",
    "habit",
    "growth",
    "communication",
    "coaching",
)


def normalize_human_model_snapshot(
    snapshot: Mapping[str, Any] | None,
) -> Mapping[str, Mapping[str, Any]]:
    """Normalize an explicit Human Model snapshot to the six allowed sections.

    Unknown keys, decision-style keys, and domain-specific keys are ignored by
    construction because only the six allowed Human Model sections are copied.
    Missing or non-mapping section values become empty dictionaries. The input
    mapping and nested mappings are not mutated.
    """

    source = snapshot if isinstance(snapshot, Mapping) else {}
    return {
        field_name: dict(value) if isinstance(value, Mapping) else {}
        for field_name in HUMAN_MODEL_SNAPSHOT_FIELDS
        for value in [source.get(field_name, {})]
    }
