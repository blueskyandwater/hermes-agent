# Story 3.8 - Human Model Snapshot Provider Design

## Story Goal

Design the responsibility boundary and future API shape for a provider layer that may eventually generate the `human_model_snapshot` passed to the Decision Framework Adapter.

Story 3.8 does **not** implement the provider. It is a design-only story that preserves the Story 3.7 decision:

> Recommend explicit snapshot only for now.

## Recommendation

**Recommend provider interface design only.**

Reasons:

- It does not conflict with Story 3.7's explicit-snapshot-only approach.
- It has no runtime side effects because no provider is implemented yet.
- It creates a future abstraction point for docs, profile, or memory sources.
- It avoids making the adapter depend on a provider.
- It prevents Human Model mutation, Decision Style data, and Domain Model data from being mixed into the Decision Framework input boundary.

## Provider Responsibilities

A future `HumanModelSnapshotProvider` should be a read-only snapshot boundary. It should prepare adapter-facing Human Model input, not change the Human Model and not make decisions for the user.

Provider responsibilities:

- Accept an explicit snapshot.
- Abstract future docs, profile, or memory sources.
- Return a six-field Human Model snapshot.
- Normalize missing fields to `{}`.
- Exclude unknown keys.
- Exclude `decision_style`.
- Exclude domain-specific keys.
- Avoid mutating the input mapping.

The returned snapshot should contain only these top-level fields:

```python
{
    "identity": Mapping[str, Any],
    "energy": Mapping[str, Any],
    "habit": Mapping[str, Any],
    "growth": Mapping[str, Any],
    "communication": Mapping[str, Any],
    "coaching": Mapping[str, Any],
}
```

A future provider should not do the following:

- memory write
- Human Model mutation
- docs parsing implementation
- LLM-based extraction
- Domain Model judgment
- Decision Style implementation
- `conversation_loop` integration
- final decision generation
- recommendation generation

## Provider Options Compared

| Option | Description | Safety | Small implementation | Low side effects | Future extensibility | Memory dependency risk | Human Model mutation risk | Testability | Adapter responsibility separation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | Do not create a provider yet | High | Highest | Highest | Medium | Low | Low | High | Medium |
| B | Create only an explicit snapshot normalizer | High | High | High | Medium | Low | Low | High | Medium-High |
| C | Design only a `HumanModelSnapshotProvider` interface | High | High | High | High | Low | Low | High | High |
| D | Keep a docs-backed provider as a future candidate | Medium | Low | Medium | Medium | Low | Medium | Low-Medium | High |
| E | Keep a memory-backed provider as a future candidate | Low-Medium | Low | Low | High | High | High | Medium | High |

### A. Do not create a provider yet

This is safe and consistent with Story 3.7. It keeps the adapter pure and avoids runtime coupling. The weakness is that the future boundary for docs, profile, and memory sources remains ambiguous.

### B. Create only an explicit snapshot normalizer

This would be small and testable, but it can overlap with the adapter's current normalization responsibility. If introduced too early, it may create two nearby layers that both know the six Human Model fields without a clear reason to separate them.

### C. Design only a `HumanModelSnapshotProvider` interface

This is the recommended Story 3.8 outcome. It establishes a future boundary without introducing runtime behavior, memory reads, docs parsing, or adapter coupling.

### D. Keep a docs-backed provider as a future candidate

The docs-backed path may be useful later for offline seed generation because `docs/human-model/` already contains the six Human Model profile areas. It should not be implemented now because Markdown parsing would make documentation changes affect runtime behavior.

### E. Keep a memory-backed provider as a future candidate

A memory-backed provider may eventually be the natural production source, but it should wait until Human Model Store semantics are designed. It has higher stale-data, trust, schema-versioning, and accidental-mutation risks.

## Final Option Decision

**Choose C: design only a `HumanModelSnapshotProvider` interface.**

This preserves the current explicit-snapshot adapter boundary while documenting where future source selection can live.

## Future API Shape

A future provider may use an API like this:

```python
class HumanModelSnapshotProvider:
    def build_snapshot(
        self,
        explicit_snapshot: Mapping[str, Any] | None = None,
        turn_context: Mapping[str, Any] | None = None,
    ) -> Mapping[str, Any]:
        ...
```

`explicit_snapshot` should remain the first and safest source. `turn_context` is reserved for future runtime context and should not require conversation-loop integration in Story 3.8.

The return value should always contain exactly six top-level fields:

```python
{
    "identity": {},
    "energy": {},
    "habit": {},
    "growth": {},
    "communication": {},
    "coaching": {},
}
```

A future implementation may choose to preserve mapping values from `explicit_snapshot`, but the top-level shape should stay fixed to those six fields.

## Adapter Relationship

The intended relationship is:

```text
Caller / future runtime layer
  ↓
HumanModelSnapshotProvider
  ↓
human_model_snapshot
  ↓
Decision Framework Adapter
  ↓
DecisionFrameworkInput
```

**Adapter should not directly know about the provider.**

Reasons:

- It preserves the adapter's pure boundary.
- It keeps memory, docs, and runtime dependencies out of the adapter.
- Provider source strategy can change without changing the adapter API.
- Provider tests and adapter tests can remain separate.

Future calling code should build the snapshot first, then pass it into the adapter:

```python
snapshot = human_model_snapshot_provider.build_snapshot(
    explicit_snapshot=explicit_snapshot,
    turn_context=turn_context,
)

context = build_decision_support_context(
    human_model_snapshot=snapshot,
    turn_context=turn_context,
)
```

This example is illustrative only. Story 3.8 does not implement it.

## Non-goals

Story 3.8 does not include:

- code implementation
- memory read/write
- docs parsing
- Human Model mutation
- Decision Style implementation
- Domain Model implementation
- `conversation_loop` integration
- `run_agent.py` integration
- `prompt_builder.py` integration
- gateway/API integration
- final decision generation
- recommendation generation

## Blocking Issues

None.

## Non-blocking Issues

- Story 3.8 intentionally leaves the provider unimplemented.
- Docs-backed and memory-backed sources need separate future stories before runtime use.
- Memory-backed provider design should wait for Human Model Store semantics.

## Next Human Approval Point

Approve whether the next story should remain design-only or introduce a minimal explicit snapshot normalizer.

If implementation is approved later, the safest next implementation candidate is a small, read-only normalizer that preserves the adapter boundary and does not connect to runtime, memory, docs parsing, Decision Style, or Domain Models.
