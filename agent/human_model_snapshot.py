"""Utilities for normalizing explicit Human Model snapshots.

This module is intentionally pure and source-agnostic. It accepts an explicit
caller-provided snapshot, or a read-only source boundary, and returns the six
Decision Framework Human Model sections that are safe to pass onward. It does
not write memory, parse profile/docs, mutate Human Model state, or connect to
runtime surfaces.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Mapping

__all__ = [
    "HUMAN_MODEL_SNAPSHOT_FIELDS",
    "HumanModelSnapshotProvider",
    "normalize_human_model_snapshot",
]

SnapshotSource = Mapping[str, Any] | Callable[[], Mapping[str, Any] | None] | None

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


class HumanModelSnapshotProvider:
    """Read-only boundary for building normalized Human Model snapshots.

    The provider intentionally stops at source selection plus normalization. It
    does not connect to memory stores, write memory, mutate Human Model state,
    parse docs/profiles, call Decision Framework code, or expose a gateway/API/
    CLI surface.
    """

    def __init__(self, snapshot_source: SnapshotSource = None) -> None:
        self._snapshot_source = snapshot_source

    def build_snapshot(
        self,
        explicit_snapshot: Mapping[str, Any] | None = None,
    ) -> Mapping[str, Mapping[str, Any]]:
        """Return the normalized six-section Human Model snapshot.

        Explicit snapshots take precedence over the configured source. When no
        explicit snapshot is supplied, a mapping source is read as-is and a
        callable source is invoked without arguments. All returned data is
        normalized via :func:`normalize_human_model_snapshot`, which copies the
        allowed mapping sections and drops unknown, Decision Style, and Domain
        Model keys.
        """

        if explicit_snapshot is not None:
            return normalize_human_model_snapshot(explicit_snapshot)

        source_snapshot = self._read_source_snapshot()
        return normalize_human_model_snapshot(source_snapshot)

    def _read_source_snapshot(self) -> Mapping[str, Any] | None:
        source = self._snapshot_source
        if source is None:
            return None
        if isinstance(source, Mapping):
            return source
        if callable(source):
            return source()
        return None
