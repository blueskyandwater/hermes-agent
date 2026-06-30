# Story 3.23 - Domain Model Interface Design

## Background

Story 3.7 and Story 3.8 fixed the Human Model input boundary as a six-section,
read-only snapshot shape.

Story 3.19 fixed the internal Decision Support caller boundary so that trusted
internal code may prepare decision-support context without exposing new public
inputs.

The current roadmap then places a new phase after memory-backed Human Model
context: add domain-specific context and Decision Style carefully, without
mixing either of them into the Human Model and without expanding external
surfaces too early.

Current confirmed baseline:

- `HumanModelSnapshotProvider` is implemented as a read-only boundary in
  `agent/human_model_snapshot.py`.
- The provider normalizes only the six allowed Human Model sections.
- Unknown, Decision Style, and domain-specific keys are excluded from the Human
  Model snapshot boundary.
- Decision Support remains an internal path.
- Gateway/API/CLI exposure is still deferred until schema, auth, redaction, and
  logging design exist.
- Memory mutation is still deferred until after read-only provider boundaries are
  settled.

This creates the next design question:

> If Hermes eventually needs domain-specific context for better decision support,
> where should that context live, and what interface can carry it without
> polluting the Human Model?

Story 3.23 answers that question as a design-only artifact.

## Goals

- Define a separate Domain Model interface boundary for specialized context.
- Keep Domain Model data clearly separate from Human Model data.
- Preserve the current Human Model snapshot contract unchanged.
- Define a read-only provider-shaped path for future domain context retrieval.
- Describe a minimal, inspectable data shape that trusted internal callers can
  use later.
- State the safety and redaction rules that must be settled before any external
  exposure.
- Keep Decision Style out of policy logic and treat it only as a future soft hint
  layer.

## Non-goals

Story 3.23 does not include:

- code implementation
- runtime wiring
- gateway/API/CLI exposure
- schema publication for public callers
- memory mutation
- Human Model mutation
- Decision Style implementation
- Domain Model recommendation logic
- final decision generation
- automatic domain inference from conversation text
- docs/profile parsing implementation
- `conversation_loop`, `run_agent.py`, or `prompt_builder.py` changes

## Why a separate Domain Model is needed

Human Model and Domain Model answer different questions.

- Human Model describes the user across durable support dimensions such as
  identity, energy, habit, growth, communication, and coaching.
- Domain Model describes the current structured context of a specific operating
  area such as investment, health, career, business, or travel.

If Domain Model data is mixed into Human Model:

- the Human Model stops being a stable user-understanding boundary
- domain facts start to look like user identity facts
- redaction and provenance become harder to explain
- per-domain freshness and trust rules become ambiguous
- future mutation boundaries become harder to enforce

The safer design is:

```text
Human Model = who the user is / how Hermes should support the user
Domain Model = structured context about a specific problem space
Decision Style = soft hint about preferred decision-making posture
```

These should remain separate inputs even if a future internal caller combines
summaries from them into a single temporary decision-support payload.

## Domain Model and Human Model boundary

### Human Model remains

The Human Model boundary remains exactly the current six sections:

```text
identity
energy
habit
growth
communication
coaching
```

Rules that remain unchanged:

- Human Model snapshot accepts only those six top-level sections.
- Domain-specific keys must not be inserted into the Human Model snapshot.
- Decision Style must not be inserted into the Human Model snapshot.
- Human Model remains durable-support-oriented, not domain-case-oriented.

### Domain Model should contain

A Domain Model should contain structured, read-only, domain-scoped context such
as:

- the domain name
- a normalized domain context payload
- provenance / source summary
- freshness metadata
- trust / confidence metadata
- optional bounded domain constraints

### Domain Model must not contain

A Domain Model must not:

- redefine Human Model identity or values
- replace the user's final decision authority
- act as a hidden policy engine
- silently write memory
- mutate source records
- expose raw sensitive records by default
- expand into public gateway/API/CLI inputs before safety design exists

## Proposed interface

The recommended future boundary is an internal, read-only provider interface
parallel to the Human Model snapshot provider.

Illustrative shape:

```python
class DomainModelProvider:
    def build_domain_context(
        self,
        domain_name: str,
        explicit_context: Mapping[str, Any] | None = None,
    ) -> Mapping[str, Any]:
        ...
```

Design intent:

- `domain_name` makes the target domain explicit.
- `explicit_context` is the safest first source, mirroring the earlier Human
  Model design direction.
- Future read-only sources may exist behind the provider, but they should remain
  internal and explicit.
- The provider returns normalized domain context for internal callers.
- The provider does not know about gateway/API/CLI exposure.
- The provider does not mutate memory or domain records.

Recommended ownership chain:

```text
explicit domain context or future read-only source
  ↓
DomainModelProvider
  ↓
normalized domain context
  ↓
trusted internal Decision Support caller/preparer
  ↓
temporary decision-support payload
  ↓
AIAgent.run_conversation(...)
  ↓
conversation_loop injection sink
```

This keeps:

- source retrieval
- normalization
- redaction/provenance shaping
- decision-support preparation
- runtime injection

as separate responsibilities.

## Read-only provider assumptions

A future `DomainModelProvider` should be read-only first.

Recommended v1 provider responsibilities:

- accept explicit bounded domain context
- optionally read from a future trusted read-only source
- normalize the context into a stable interface shape
- attach provenance/freshness/trust metadata
- drop unknown top-level structural fields outside the interface contract
- avoid mutating caller input
- avoid mutating source data
- remain independent from runtime transport surfaces

Recommended non-responsibilities:

- memory write
- source mutation
- automatic domain selection
- recommendation generation
- policy enforcement
- final decision generation
- gateway/API/CLI publication
- auth decisions
- logging policy decisions

## Data shape / schema sketch

A future internal Domain Model payload may use a shape like this:

```python
{
    "domain_name": "investment",
    "schema_version": "domain-model.v1",
    "context": {
        "objectives": ["capital preservation", "long-term growth"],
        "constraints": ["no leverage", "taxable account"],
        "current_state": {
            "cash_ratio": "bounded-summary-only",
            "review_horizon": "quarterly",
        },
    },
    "provenance": {
        "source_kind": "explicit" | "read_only_memory" | "read_only_store",
        "source_label": "user-provided" | "investment-profile" | "other-safe-label",
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
        "contains_sensitive_fields": True,
        "safe_summary_only": True,
    },
}
```

Interpretation notes:

- `domain_name` should be explicit and single-domain for v1.
- `schema_version` should version the Domain Model independently from Human
  Model and Decision Framework schemas.
- `context` is opaque to the general runtime but structured for the relevant
  domain.
- `provenance`, `freshness`, and `trust` are first-class because domain context
  can age or drift faster than Human Model context.
- `redaction` indicates whether the payload is already safe for downstream
  internal use.

### Example domains

Likely future domains include:

- `investment`
- `health`
- `career`
- `business`
- `finance`
- `travel`

Story 3.23 does not lock the internal schema of each domain. It fixes only the
interface shell around them.

## Relationship to Decision Style

Decision Style should not be stored inside Human Model and should not be treated
as a policy engine.

For Story 3.23, the important rule is:

- Domain Model and Decision Style are different things.

Suggested separation:

- Domain Model = structured facts / constraints / context for a domain
- Decision Style = soft hint about how the user prefers to approach decisions

Examples of Decision Style soft hints:

- cautious vs exploratory
- fast provisional answer vs deliberate deep review
- preference for downside protection vs upside seeking

These hints may influence phrasing or emphasis later, but they must not become:

- mandatory decision policy
- hidden override of user agency
- substitute for domain facts

## Safety and redaction considerations

Before any runtime expansion or external exposure, Domain Model design must keep
these constraints.

### 1. Read-only first

Domain context should begin as read-only.

No automatic memory mutation, no source rewriting, and no hidden persistence
should occur as part of domain-context retrieval.

### 2. Safe summary before raw records

The provider boundary should prefer bounded summaries over raw source payloads.

Examples:

- summarized constraints instead of full account records
- summarized health context instead of raw medical history
- summarized business context instead of unrestricted internal notes

### 3. Provenance must remain visible

A trusted internal caller should be able to explain where domain context came
from:

- explicit user input
- read-only memory result
- read-only store snapshot
- another approved internal source

### 4. Freshness matters more than in Human Model

Many domain facts change faster than Human Model support traits. The interface
should therefore track freshness and stale-state explicitly.

### 5. External exposure is deferred

Gateway/API/CLI exposure should remain blocked until all of the following exist:

- schema design
- redaction design
- auth design
- logging design
- approval for the public surface

### 6. Domain Model must not silently decide for the user

Even if domain context is rich, the final decision remains the user's. Domain
Model is support context, not delegated authority.

## Open questions

1. Should v1 allow only a single `domain_name` per payload, or support a future
   multi-domain wrapper later?
2. Should provenance remain a simple summary structure, or eventually include
   record-level references?
3. How should read-only memory-backed domain sources declare stale or conflicting
   facts?
4. What is the smallest safe redaction contract before any internal caller can
   combine Domain Model output with decision-support context?
5. Should Domain Model normalization allow domain-specific validators per
   `domain_name`, or stay generic at the interface layer?
6. What story should define the Decision Style interface so it can remain a soft
   hint rather than drifting into policy?

## Next steps

Recommended next sequence:

1. Confirm Story 3.20 / 3.22 reality is still aligned enough to build on.
2. Design a read-only memory-backed Human Model safety note if additional
   provenance constraints are still needed.
3. Define a minimal Domain Model provider design review checklist.
4. Define the Decision Style interface separately as a soft-hint boundary.
5. Only after schema/redaction/auth/logging design, consider whether any
   gateway/API/CLI exposure is acceptable.
6. Keep memory mutation for a later dedicated story after read-only provider
   boundaries are proven.

## Recommendation summary

Choose the smallest safe boundary:

- keep Domain Model separate from Human Model
- define a read-only internal provider interface first
- require provenance, freshness, trust, and redaction metadata in the interface
- defer runtime/public exposure
- keep Decision Style as a separate soft-hint concern

This preserves Human Model clarity while creating a future extension point for
specialized domain context inside the Decision Framework.
