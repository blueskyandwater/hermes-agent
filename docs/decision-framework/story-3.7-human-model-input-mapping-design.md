# Story 3.7 - Human Model Input Mapping Design

## Story Goal

Define the structure, source strategy, and missing-value behavior for the `human_model_snapshot` passed to the Decision Framework Adapter.

Story 3.6 already introduced the minimal adapter API:

```python
build_decision_support_context(
    human_model_snapshot: Mapping[str, Any] | None,
    turn_context: Mapping[str, Any] | None = None,
) -> str
```

Story 3.7 decides where `human_model_snapshot` should come from and what shape it should have before it reaches that adapter boundary.

## Recommendation

**Recommend explicit snapshot only for now.**

The adapter should continue to accept an explicitly supplied snapshot and should not fetch, infer, or mutate Human Model data by itself.

Reasons:

- It preserves the adapter's pure, side-effect-free boundary.
- It defers memory, docs, and runtime integration until those layers have explicit contracts.
- It avoids Human Model mutation.
- It prevents Decision Style and Domain Model data from being mixed into the v1 Decision Framework input.
- It makes the boundary easy to lock down with unit tests.
- It leaves room to add a future `HumanModelSnapshotProvider` without changing the adapter API.

## Recommended Snapshot Structure

The snapshot should be a shallow mapping with exactly the six Human Model fields accepted by `DecisionFrameworkInput`:

```python
human_model_snapshot = {
    "identity": Mapping[str, Any],
    "energy": Mapping[str, Any],
    "habit": Mapping[str, Any],
    "growth": Mapping[str, Any],
    "communication": Mapping[str, Any],
    "coaching": Mapping[str, Any],
}
```

Rules:

- Top-level keys are limited to the six fields above.
- Each accepted value is treated as `Mapping[str, Any]`.
- Missing fields normalize to `{}`.
- Unknown keys are ignored.
- `decision_style` is ignored.
- Domain-specific keys are ignored.
- The input mapping must not be mutated.

The Decision Framework should not define the internal schema of each Human Model profile in this story. Each field remains an opaque mapping from the adapter's perspective.

## Source Options Compared

| Option | Description | Safety | Small implementation | Low side effects | Future extensibility | Memory dependency risk | Human Model change risk | Testability |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | Read from `docs/human-model/*.md` | Medium | Low-Medium | Medium | Medium | Low | Medium | Low |
| B | Read from memory / profile store | Low-Medium | Low | Low | High | High | High | Medium |
| C | Build from explicitly provided conversation context | Medium | Medium | Medium | Medium | Medium | Medium | Medium |
| D | Use only the explicit snapshot argument for now | High | High | High | Medium | Low | Low | High |
| E | Build a future Human Model Store | Medium | Low | Medium | High | Medium | Medium | Medium-High |

### A. Read from `docs/human-model/*.md`

This is useful as a possible future offline seed-generation path because the Human Model docs already describe the six profile areas. It is not recommended for Story 3.7 because Markdown parsing would turn documentation into runtime input and make docs changes affect adapter behavior.

### B. Read from memory / profile store

This may become natural for production behavior later, but it should wait until Human Model Store semantics are designed. Direct memory/profile reads introduce stale-data, trust, schema, and accidental-write concerns too early.

### C. Build from explicit conversation context

This may be useful after conversation-loop integration exists, especially when the user explicitly provides temporary context for a decision. It is not recommended in Story 3.7 because conversation extraction and runtime wiring are out of scope.

### D. Use only the explicit snapshot argument for now

This is the recommended Story 3.7 direction. It matches the Story 3.6 adapter API, keeps the adapter pure, avoids external reads, and is easy to test.

### E. Build a future Human Model Store

A dedicated store is a strong future direction because it could unify docs, memory, profile data, and explicit context behind a versioned read-only snapshot boundary. It is too large for Story 3.7 and should remain a future design topic.

## Missing and Extra Data Behavior

The adapter-facing snapshot normalization should follow these rules:

| Input case | Behavior |
| --- | --- |
| `snapshot is None` | Produce all six fields as `{}`. |
| `snapshot == {}` | Produce all six fields as `{}`. |
| Only some of the six fields are present | Use the provided fields and fill missing fields with `{}`. |
| Unknown top-level key is present | Ignore it. |
| `decision_style` is present | Ignore it. |
| Domain-specific key is present | Ignore it. |
| Input mapping is provided | Do not mutate it. |

Domain-specific keys include, but are not limited to:

- `investment`
- `health`
- `career`
- `business`
- `finance`
- `travel`

Example normalization:

```python
input_snapshot = {
    "identity": {"values": ["agency", "ownership"]},
    "energy": {"current_capacity": "low"},
    "decision_style": {"risk": "low"},
    "investment": {"portfolio": "out-of-scope"},
    "temporary_mood": "tired",
}

normalized_snapshot = {
    "identity": {"values": ["agency", "ownership"]},
    "energy": {"current_capacity": "low"},
    "habit": {},
    "growth": {},
    "communication": {},
    "coaching": {},
}
```

## Future Shape

A future story may introduce a dedicated provider that constructs explicit snapshots before calling the adapter:

```python
class HumanModelSnapshotProvider:
    def build_snapshot(
        self,
        source_context: Mapping[str, Any] | None = None,
    ) -> Mapping[str, Any]:
        ...
```

Story 3.7 does **not** implement this provider. It only reserves the shape so later runtime integration can be added without changing the adapter API.

## Non-goals

Story 3.7 does not include:

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

## Final Decision

For Story 3.7, the Decision Framework Adapter should continue to receive an explicit, caller-supplied `human_model_snapshot`.

The accepted top-level shape is the six-field Human Model mapping:

```text
identity
energy
habit
growth
communication
coaching
```

All missing or invalid profile fields become `{}`. Unknown, Decision Style, and domain-specific keys are ignored. The input mapping is never mutated.

This keeps Story 3.7 as a documentation and boundary-design step only, while preserving a clean path toward a future `HumanModelSnapshotProvider`.
