"""Read-only Domain Model normalization and provider boundary.

This module is intentionally pure and source-agnostic. It accepts an explicit
caller-provided domain context payload, or a read-only source boundary, and
returns a normalized evidence-only Domain Model shape. It does not write memory,
mutate Human Model or Decision Profile state, open gateway/API/CLI surfaces, or
connect to dispatcher/runtime flows.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any

__all__ = [
    "DOMAIN_MODEL_SCHEMA_VERSION",
    "DOMAIN_MODEL_TOP_LEVEL_FIELDS",
    "DomainModelProvider",
    "normalize_domain_context",
]

DomainSource = Mapping[str, Any] | Callable[[], Mapping[str, Any] | None] | None

DOMAIN_MODEL_SCHEMA_VERSION = "domain-model.v1"
DOMAIN_MODEL_TOP_LEVEL_FIELDS = (
    "domain_name",
    "schema_version",
    "context",
    "provenance",
    "freshness",
    "trust",
    "redaction",
)

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

_HUMAN_MODEL_FIELDS = frozenset(
    {
        "identity",
        "energy",
        "habit",
        "growth",
        "communication",
        "coaching",
    }
)

_DECISION_STYLE_FIELDS = frozenset(
    {
        "style_hints",
        "framing_preferences",
        "interaction_preferences",
        "decision_support_preferences",
        "decision_style",
    }
)

_POLICY_LIKE_FIELDS = frozenset(
    {
        "policy",
        "hard_rule",
        "hard_rules",
        "final_decision",
        "instruction_override",
        "recommendation",
    }
)

_FORBIDDEN_CONTEXT_KEYS = _HUMAN_MODEL_FIELDS | _DECISION_STYLE_FIELDS | _POLICY_LIKE_FIELDS


def normalize_domain_context(
    domain_name: str,
    domain: Mapping[str, Any] | None,
    *,
    default_source_kind: str = "none",
    default_source_label: str | None = None,
) -> Mapping[str, Any]:
    """Normalize a Domain Model payload to the minimal evidence-only schema.

    ``domain_name`` is always caller-provided and preserved as the single v1
    domain identifier. Unknown top-level keys are dropped by construction.
    Human Model, Decision Style, policy, hard-rule, final-decision,
    instruction-override, and recommendation-like keys are never part of the
    returned shape. Input mappings and nested mappings are not mutated.
    """

    explicit_domain_name = _normalize_domain_name(domain_name)
    source = domain if isinstance(domain, Mapping) else {}

    return {
        "domain_name": explicit_domain_name,
        "schema_version": DOMAIN_MODEL_SCHEMA_VERSION,
        "context": _normalize_context(source.get("context")),
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


class DomainModelProvider:
    """Read-only boundary for building normalized Domain Model payloads.

    The provider intentionally stops at source selection plus normalization. It
    does not connect to memory stores, write profile state, mutate Human Model
    or Decision Profile data, call runtime/dispatcher hooks, or expose a
    gateway/API/CLI surface. Domain Model output is evidence context, not
    orders, policy, recommendations, or final-decision authority.
    """

    def __init__(self, domain_source: DomainSource = None) -> None:
        self._domain_source = domain_source

    def build_domain_context(
        self,
        domain_name: str,
        explicit_context: Mapping[str, Any] | None = None,
    ) -> Mapping[str, Any]:
        """Return the normalized evidence-only Domain Model payload.

        Explicit task-scoped context takes precedence over the configured
        source. When no explicit context is supplied, a mapping source is read
        as-is and a callable source is invoked without arguments. All returned
        data is normalized via :func:`normalize_domain_context`, which copies
        only the approved Domain Model schema and excludes Human Model,
        Decision Style, policy, hard-rule, final-decision,
        instruction-override, and recommendation-like keys.
        """

        if explicit_context is not None:
            return normalize_domain_context(
                domain_name,
                explicit_context,
                default_source_kind="explicit",
                default_source_label="explicit-input",
            )

        source_domain = self._read_source_domain()
        return normalize_domain_context(
            domain_name,
            source_domain,
            default_source_kind="read_only_source" if source_domain is not None else "none",
            default_source_label="configured-source" if source_domain is not None else None,
        )

    def _read_source_domain(self) -> Mapping[str, Any] | None:
        source = self._domain_source
        if source is None:
            return None
        if isinstance(source, Mapping):
            return source
        if callable(source):
            return source()
        return None


def _normalize_domain_name(domain_name: str) -> str:
    if not isinstance(domain_name, str) or not domain_name.strip():
        raise ValueError("domain_name must be a non-empty string")
    return domain_name


def _normalize_context(value: object) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        return {}

    normalized: dict[str, Any] = {}
    for key, item in value.items():
        if not isinstance(key, str) or key in _FORBIDDEN_CONTEXT_KEYS:
            continue
        copied = _copy_context_value(item)
        if copied is not _DROP:
            normalized[key] = copied
    return normalized


class _DropSentinel:
    pass


_DROP = _DropSentinel()


def _copy_context_value(value: object) -> Any:
    if _is_domain_scalar(value):
        return value

    if isinstance(value, Mapping):
        normalized: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str) or key in _FORBIDDEN_CONTEXT_KEYS:
                continue
            copied = _copy_context_value(item)
            if copied is not _DROP:
                normalized[key] = copied
        if not normalized and value:
            return _DROP
        return normalized

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        normalized_list = []
        for item in value:
            copied = _copy_context_value(item)
            if copied is not _DROP:
                normalized_list.append(copied)
        return normalized_list

    return _DROP


def _is_domain_scalar(value: object) -> bool:
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
        if field in source and _is_domain_scalar(source[field]):
            normalized[field] = source[field]
    return normalized
