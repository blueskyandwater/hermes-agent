# Story 3.24 - Decision Style Interface Design

## Background

Story 3.21 fixed the Human Model boundary around a six-section snapshot shape.
Story 3.22 clarified that `HumanModelSnapshotProvider` is implemented as a
read-only boundary, while fully defined memory-backed source integration is not
yet enabled.
Story 3.23 then introduced a separate Domain Model interface boundary so
specialized context can be added without polluting the Human Model.

The next design question is narrower:

> If Hermes later uses Decision Style, what interface should carry it so that it
> stays a soft hint instead of turning into hidden policy, hard rules, or final
> decision logic?

Current confirmed baseline:

- Human Model remains a read-only six-section support snapshot.
- Domain Model remains a separate domain-scoped context boundary.
- Gateway/API/CLI publication is not yet opened as an external surface.
- Memory mutation is still deferred.
- Decision Style is not yet implemented as a product/runtime layer.
- Product Vision already defines Decision Style as a soft adaptation hint.

This story is design-only. It defines the interface shell and safety rules for a
future Decision Style boundary without opening runtime exposure, mutation, or
policy behavior.

## Goals

- Define a separate Decision Style interface boundary.
- Keep Decision Style distinct from Human Model and Domain Model.
- Fix the meaning of Decision Style as a soft hint only.
- Describe a minimal internal provider-shaped interface for future read-only
  retrieval.
- Provide a schema sketch that trusted internal callers may eventually consume.
- Preserve user agency and prevent Decision Style from becoming hidden policy.
- Document logging, redaction, and reviewability constraints before any runtime
  expansion.

## Non-goals

Story 3.24 does not include:

- code implementation
- runtime wiring
- gateway/API/CLI exposure
- memory mutation
- Human Model mutation
- Domain Model mutation
- decision policy enforcement
- hard-rule evaluation
- final decision generation
- automatic conversation-time inference
- recommendation logic
- prompt-builder or conversation-loop integration
- public schema publication

## Relationship to Human Model

Human Model and Decision Style answer different questions.

- Human Model describes who the user is and how Hermes should support the user
  across durable support dimensions.
- Decision Style describes how the user may prefer decisions to be framed,
  paced, compared, or stress-tested.

The Human Model boundary must remain the same six sections only:

```text
identity
energy
habit
growth
communication
coaching
```

Rules:

- Decision Style must not be inserted into the Human Model snapshot.
- Decision Style must not redefine identity, values, or durable personal facts.
- Human Model remains the support-context boundary, not a decision-posture
  container.

## Relationship to Domain Model

Domain Model and Decision Style also answer different questions.

- Domain Model provides structured domain-specific context such as constraints,
  risks, terminology, and evidence standards.
- Decision Style provides soft guidance about how to approach judgment within or
  around that context.

Examples:

- Domain Model: investment horizon, tax constraints, risk categories,
  rebalancing cadence.
- Decision Style: prefers downside-first framing, prefers reversible next steps,
  prefers short comparison before recommendation.

Rules:

- Decision Style must not be stored inside Domain Model.
- Domain Model must not become a carrier for generic decision posture.
- Domain facts and decision posture should remain independently inspectable.

## Decision Style as soft hint

Decision Style must be interpreted narrowly.

Safe meaning:

> Decision Style is a soft adaptation hint that may influence framing,
> ordering, emphasis, depth, or comparison style.

Unsafe meanings:

- hidden policy engine
- mandatory rule set
- hard constraint solver
- automatic delegation of final choice to Hermes
- substitute for Human Model values
- substitute for Domain Model facts

Soft-hint examples:

- cautious vs exploratory tone of tradeoff framing
- fast provisional answer vs deliberate review emphasis
- downside-first vs upside-first comparison order
- preference for reversible next steps before strong commitment
- preference for explicit uncertainty and evidence gaps

Even when used, Decision Style should only shape presentation and emphasis. It
must not claim authority over the user's final decision.

## Proposed interface

The recommended future boundary is an internal, read-only provider interface
parallel to the Human Model snapshot provider and the future Domain Model
provider.

Illustrative shape:

```python
class DecisionStyleProvider:
    def build_decision_style(
        self,
        explicit_style: Mapping[str, Any] | None = None,
    ) -> Mapping[str, Any]:
        ...
```

Possible later extension if source selection is needed:

```python
class DecisionStyleProvider:
    def build_decision_style(
        self,
        explicit_style: Mapping[str, Any] | None = None,
        source_label: str | None = None,
    ) -> Mapping[str, Any]:
        ...
```

Design intent:

- `explicit_style` is the safest first source.
- Future read-only sources may exist behind the provider, but they should remain
  internal and explicit.
- The provider returns normalized Decision Style hints for trusted internal
  callers only.
- The provider does not know about gateway/API/CLI surfaces.
- The provider does not mutate memory, profile state, or domain records.
- The provider does not execute policy logic.

Recommended ownership chain:

```text
explicit style input or future read-only source
  ↓
DecisionStyleProvider
  ↓
normalized decision-style hints
  ↓
trusted internal Decision Support caller/preparer
  ↓
temporary decision-support payload
  ↓
AIAgent.run_conversation(...)
  ↓
conversation_loop injection sink
```

This keeps source retrieval, normalization, safety shaping, and runtime
injection separate.

## Data shape / schema sketch

A future internal Decision Style payload may use a shape like this:

```python
{
    "schema_version": "decision-style.v1",
    "style": {
        "pace": "fast_provisional" | "deliberate_review" | "balanced",
        "tradeoff_frame": "downside_first" | "balanced" | "upside_first",
        "uncertainty_style": "explicit" | "minimal" | "balanced",
        "action_preference": "reversible_first" | "commit_when_ready" | "balanced",
        "delegation_posture": "advisor_only" | "strong_recommendation_ok" | "balanced",
    },
    "provenance": {
        "source_kind": "explicit" | "read_only_memory" | "read_only_store",
        "source_label": "user-provided" | "decision-profile" | "other-safe-label",
    },
    "freshness": {
        "captured_at": "ISO-8601 or null",
        "staleness": "unknown" | "fresh" | "stale",
    },
    "trust": {
        "level": "low" | "medium" | "high",
        "reason": "short human-readable justification",
    },
    "redaction": {
        "contains_sensitive_fields": False,
        "safe_summary_only": True,
    },
}
```

Interpretation notes:

- `schema_version` should be independent from Human Model and Domain Model.
- `style` should contain bounded enumerated hints rather than open-ended policy
  text when possible.
- `provenance`, `freshness`, and `trust` matter because decision posture may be
  contextual, inferred imperfectly, or become stale.
- `delegation_posture` must remain advisory about answer style, not authority
  transfer.

## Read-only provider assumptions

A future `DecisionStyleProvider` should be read-only first.

Recommended v1 responsibilities:

- accept explicit bounded Decision Style input
- optionally read from a future trusted read-only source
- normalize the payload into a stable internal interface shape
- attach provenance/freshness/trust metadata
- drop unknown top-level structural fields outside the interface contract
- avoid mutating caller input
- avoid mutating source data
- remain independent from runtime transport surfaces

Recommended non-responsibilities:

- memory write
- source mutation
- policy enforcement
- hard-rule evaluation
- automatic final decision logic
- recommendation generation by itself
- gateway/API/CLI publication
- auth decisions
- logging policy decisions

## Safety considerations

Before any runtime expansion, Decision Style design must preserve these
constraints.

### 1. User agency stays primary

Decision Style may shape support, but it must never claim final decision
ownership or silently override the user's explicit request.

### 2. No hidden policy behavior

Decision Style must not quietly become a rule engine that blocks, forces, or
ranks actions without an explicit higher-level design and approval.

### 3. Keep boundaries inspectable

A reviewer should be able to tell whether a given effect came from:

- Human Model context
- Domain Model context
- Decision Style hint
- explicit live user instruction

### 4. Avoid over-generalization

A single interaction should not crystallize into durable Decision Style without
separate approval and source design.

### 5. Read-only first

Decision Style should be consumed as support context before any design considers
mutation, persistence, or external configuration.

## Redaction / logging considerations

Even if Decision Style is usually less sensitive than raw personal records, it
still needs bounded handling.

Recommended rules:

- log normalized summaries, not raw speculative source text
- keep provenance visible in internal inspection paths
- avoid storing conversational guesswork as durable style by default
- redact or summarize sensitive psychological or personal framing labels
- distinguish explicit user-provided style from system-derived or profile-derived
  style
- avoid logs that imply policy authority where only a hint was present

If runtime exposure is ever proposed later, logging and redaction should be
reviewed separately from the interface itself.

## Open questions

1. Should v1 Decision Style support only bounded enums, or also limited
   free-text notes with stricter redaction?
2. Should Decision Style freshness be global, or can it vary per domain/context?
3. How should explicit in-turn user instructions override stored soft hints?
4. Should delegation posture live inside Decision Style, or stay outside as a
   separate execution preference boundary?
5. What minimum provenance is required before a read-only memory-backed style
   source can be considered trustworthy?

## Impact on adjacent stories

### Impact on Story 3.23

Story 3.23 remains valid.

- Domain Model continues to carry structured domain context.
- Decision Style remains separate from Domain Model.
- Story 3.23 does not need Decision Style implementation to stay correct.

### Impact on Story 3.25

A future provider implementation story should inherit these assumptions:

- Decision Style provider is read-only first.
- Decision Style is a soft hint only.
- No policy engine or hard-rule semantics are introduced implicitly.
- Gateway/API/CLI exposure and mutation remain out of scope unless separately
  designed and approved.

## Next steps

1. Keep Human Model, Domain Model, and Decision Style as three separate internal
   boundaries.
2. If a later story implements `DecisionStyleProvider`, start with explicit
   input and normalization only.
3. Define override precedence between explicit turn instructions and stored soft
   hints before runtime wiring.
4. Revisit provenance, freshness, trust, and redaction before allowing any
   memory-backed or profile-backed read-only source.
5. Keep Gateway/API/CLI exposure and any mutation story separate from this
   interface design.

## Summary

Story 3.24 should fix the contract as:

- Human Model = durable six-section support snapshot
- Domain Model = domain-scoped structured context
- Decision Style = soft hint about decision posture

These are separate boundaries. Decision Style may help Hermes support the user
better, but it must not become policy, hard rule, or final decision logic.
