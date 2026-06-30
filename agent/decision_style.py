"""Read-only Decision Style normalization and provider boundary.

This module is intentionally pure and source-agnostic. It accepts an explicit
caller-provided Decision Style payload, or a read-only source boundary, and
returns a normalized advisory-only shape that is safe to pass onward. It does
not write memory, mutate Human Model or Domain Model state, open gateway/API/
CLI surfaces, or connect to dispatcher/runtime flows.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Mapping

__all__ = [
    "DECISION_STYLE_SCHEMA_VERSION",
    "DECISION_STYLE_TOP_LEVEL_FIELDS",
    "DecisionStyleProvider",
    "normalize_decision_style",
]

StyleSource = Mapping[str, Any] | Callable[[], Mapping[str, Any] | None] | None

DECISION_STYLE_SCHEMA_VERSION = "decision-style.v1"
DECISION_STYLE_TOP_LEVEL_FIELDS = (
    "schema_version",
    "style_hints",
    "provenance",
    "freshness",
    "trust",
    "redaction",
)

STYLE_HINT_FIELDS = (
    "framing_preferences",
    "interaction_preferences",
    "decision_support_preferences",
)

_STYLE_HINT_SUBFIELDS: dict[str, tuple[str, ...]] = {
    "framing_preferences": (
        "brevity",
        "comparison_style",
        "uncertainty_style",
        "action_posture",
    ),
    "interaction_preferences": (
        "challenge_level",
        "pace",
        "depth_default",
    ),
    "decision_support_preferences": (
        "option_count_default",
        "highlight_tradeoffs",
        "separate_fact_and_opinion",
    ),
}

_PROVENANCE_FIELDS = (
    "source_kind",
    "source_label",
    "source_id",
    "user_confirmed",
)

_FRESHNESS_FIELDS = (
    "captured_at",
    "staleness",
)

_TRUST_FIELDS = (
    "level",
    "reason",
)

_REDACTION_FIELDS = (
    "contains_sensitive_fields",
    "safe_summary_only",
)

_DEFAULT_PAYLOAD = {
    "schema_version": DECISION_STYLE_SCHEMA_VERSION,
    "style_hints": {
        "framing_preferences": {},
        "interaction_preferences": {},
        "decision_support_preferences": {},
    },
    "provenance": {
        "source_kind": "none",
        "source_label": None,
        "source_id": None,
        "user_confirmed": False,
    },
    "freshness": {
        "captured_at": None,
        "staleness": "unknown",
    },
    "trust": {
        "level": "none",
        "reason": "",
    },
    "redaction": {
        "contains_sensitive_fields": False,
        "safe_summary_only": True,
    },
}



def normalize_decision_style(
    style: Mapping[str, Any] | None,
    *,
    default_source_kind: str = "none",
    default_source_label: str | None = None,
) -> Mapping[str, Any]:
    """Normalize a Decision Style payload to the minimal advisory-only schema.

    Unknown keys are dropped at every level by construction. Human Model,
    Domain Model, policy, hard-rule, final-decision, and instruction-override
    keys are never part of the returned shape because only the approved
    Decision Style contract is copied. The input mapping and nested mappings are
    not mutated.
    """

    source = style if isinstance(style, Mapping) else {}

    normalized = {
        "schema_version": DECISION_STYLE_SCHEMA_VERSION,
        "style_hints": _normalize_style_hints(source.get("style_hints")),
        "provenance": _normalize_metadata_section(
            source.get("provenance"),
            _PROVENANCE_FIELDS,
            defaults={
                "source_kind": default_source_kind,
                "source_label": default_source_label,
                "source_id": None,
                "user_confirmed": False,
            },
        ),
        "freshness": _normalize_metadata_section(
            source.get("freshness"),
            _FRESHNESS_FIELDS,
            defaults={
                "captured_at": None,
                "staleness": "unknown",
            },
        ),
        "trust": _normalize_metadata_section(
            source.get("trust"),
            _TRUST_FIELDS,
            defaults={
                "level": "none",
                "reason": "",
            },
        ),
        "redaction": _normalize_metadata_section(
            source.get("redaction"),
            _REDACTION_FIELDS,
            defaults={
                "contains_sensitive_fields": False,
                "safe_summary_only": True,
            },
        ),
    }

    if "style_hints" not in source and not _has_meaningful_value(normalized["style_hints"]):
        normalized["style_hints"] = {}

    return normalized


class DecisionStyleProvider:
    """Read-only boundary for building normalized Decision Style payloads.

    The provider intentionally stops at source selection plus normalization. It
    does not connect to memory stores, write profile state, mutate Human Model
    or Domain Model data, call runtime/dispatcher hooks, or expose a gateway/
    API/CLI surface.
    """

    def __init__(self, style_source: StyleSource = None) -> None:
        self._style_source = style_source

    def build_decision_style(
        self,
        explicit_style: Mapping[str, Any] | None = None,
    ) -> Mapping[str, Any]:
        """Return the normalized advisory-only Decision Style payload.

        Explicit task-scoped style takes precedence over the configured source.
        When no explicit style is supplied, a mapping source is read as-is and a
        callable source is invoked without arguments. All returned data is
        normalized via :func:`normalize_decision_style`, which copies only the
        approved Decision Style schema and drops Human Model, Domain Model,
        policy, hard-rule, final-decision, and instruction-override keys.
        """

        if explicit_style is not None:
            return normalize_decision_style(
                explicit_style,
                default_source_kind="explicit",
                default_source_label="explicit-input",
            )

        source_style = self._read_source_style()
        return normalize_decision_style(
            source_style,
            default_source_kind="read_only_source" if source_style is not None else "none",
            default_source_label="configured-source" if source_style is not None else None,
        )

    def _read_source_style(self) -> Mapping[str, Any] | None:
        source = self._style_source
        if source is None:
            return None
        if isinstance(source, Mapping):
            return source
        if callable(source):
            return source()
        return None



def _normalize_style_hints(value: object) -> dict[str, dict[str, Any]]:
    source = value if isinstance(value, Mapping) else {}
    normalized: dict[str, dict[str, Any]] = {}
    for field_name in STYLE_HINT_FIELDS:
        field_value = source.get(field_name, {})
        if not isinstance(field_value, Mapping):
            normalized[field_name] = {}
            continue
        normalized[field_name] = {
            key: field_value[key]
            for key in _STYLE_HINT_SUBFIELDS[field_name]
            if key in field_value and _is_decision_style_scalar(field_value[key])
        }
    return normalized



def _is_decision_style_scalar(value: object) -> bool:
    return value is None or isinstance(value, (str, int, float, bool))



def _normalize_metadata_section(
    value: object,
    fields: tuple[str, ...],
    *,
    defaults: Mapping[str, Any],
) -> dict[str, Any]:
    source = value if isinstance(value, Mapping) else {}
    normalized = dict(defaults)
    for field in fields:
        if field in source and _is_decision_style_scalar(source[field]):
            normalized[field] = source[field]
    return normalized



def _has_meaningful_value(value: object) -> bool:
    if isinstance(value, Mapping):
        if not value:
            return False
        return any(_has_meaningful_value(item) for item in value.values())
    if isinstance(value, (list, tuple, set)):
        return any(_has_meaningful_value(item) for item in value)
    return value not in (None, "", False)
