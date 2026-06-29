# Story 3.21 - Human Model Snapshot Provider Design

## Goal

Design the boundary for a future snapshot provider that can safely supply Human
Model input to Decision Support before any memory-backed source is introduced.

This story is design-only. It does **not** implement memory access, runtime
wiring, gateway/API/CLI exposure, or Human Model updates.

## Background

After Story 3.19, a trusted internal caller may construct a prebuilt
`decision_support_context` and pass it into `AIAgent.run_conversation()`.

Before a future caller can use Human Model data safely, Hermes needs a clear
answer to three questions:

1. where the snapshot comes from,
2. what shape is allowed to cross into Decision Support,
3. which runtime surfaces must remain isolated from provider logic.

The current repository already exposes two important pure boundaries:

- `agent/human_model_snapshot.py` provides
  `normalize_human_model_snapshot(snapshot)` for the six allowed Human Model
  sections only.
- `agent/decision_framework_adapter.py` provides
  `build_decision_support_context(human_model_snapshot, turn_context=None)` and
  does not connect itself to memory, tools, conversation flow, gateway, or API
  surfaces.

Story 3.21 defines the missing provider boundary that can sit between future
source retrieval and Decision Support preparation.

## Conclusion

Introduce an internal, read-only `HumanModelSnapshotProvider` boundary.

Decision Support should receive only the normalized six-section snapshot:

- `identity`
- `energy`
- `habit`
- `growth`
- `communication`
- `coaching`

The provider must remain separate from:

- `AIAgent`
- `conversation_loop`
- gateway surfaces
- CLI surfaces
- public API surfaces

`conversation_loop` should not know the provider exists. `AIAgent` should not
create snapshots.

## Recommended Boundary

The intended ownership chain is:

```text
explicit source or future read-only source result
  ↓
HumanModelSnapshotProvider
  ↓
normalized six-section snapshot
  ↓
trusted internal Decision Support caller/preparer
  ↓
build_decision_support_context(...)
  ↓
AIAgent.run_conversation(...)
  ↓
conversation_loop injection sink
```

This keeps source retrieval, snapshot shaping, Decision Framework execution, and
runtime injection as separate responsibilities.

## Provider Responsibilities

A future `HumanModelSnapshotProvider` is responsible for the following only:

- read a snapshot from an explicit trusted source
- normalize the value into the six-section Human Model shape
- drop unknown top-level keys
- turn missing sections into empty dictionaries
- return a read-only adapter-facing snapshot
- avoid mutating the input mapping
- avoid mutating nested mapping inputs
- keep Decision Style and Domain Model data out of the snapshot

In practical terms, the provider should preserve compatibility with the current
`normalize_human_model_snapshot()` contract in `agent/human_model_snapshot.py`.

## Non-responsibilities

The provider must **not** do any of the following:

- memory write
- Human Model mutation
- docs/profile parsing
- gateway/API/CLI publication
- `conversation_loop` integration
- expansion of `AIAgent` responsibility
- Decision Framework execution
- recommendation generation
- final decision generation
- Decision Style implementation
- Domain Model implementation

## Input Design

Future inputs may eventually include:

- explicit snapshot mapping
- future memory read result
- source metadata

For v1, the preferred and safest source is:

- explicit snapshot mapping

A memory-backed provider should wait for a later story. Story 3.21 only defines
where that future source would plug in.

## Output Design

The provider output should always be compatible with the current Human Model
snapshot normalizer and adapter input expectations:

```python
{
    "identity": {...},
    "energy": {...},
    "habit": {...},
    "growth": {...},
    "communication": {...},
    "coaching": {...},
}
```

Output rules:

- only the six allowed sections may be present
- unknown keys are excluded
- missing sections become `{}`
- non-mapping section values become `{}`
- returned top-level mappings should be safe copies, not aliases to mutable
  caller state

## Safety Boundary

The provider boundary must preserve all of the following:

- provider is read-only
- memory and Human Model state are not mutated
- public API callers cannot invoke the provider directly
- external user input does not directly create a runtime snapshot
- Domain Model and Decision Style data are not mixed into the snapshot
- snapshot data is support context only, not delegated decision authority
- raw PII and raw memory should not be forwarded as-is

A provider is a shaping boundary, not a decision-maker.

## Relationship to Existing Runtime Surfaces

### `agent/human_model_snapshot.py`

This module already defines the canonical six allowed sections and a pure
normalizer. Story 3.21 should remain compatible with that boundary rather than
replace it.

### `agent/decision_framework_adapter.py`

The adapter expects a caller-provided `human_model_snapshot` and optional
`turn_context`. The provider should prepare the safe snapshot before the caller
hands it to `build_decision_support_context(...)`.

### `AIAgent.run_conversation()`

`AIAgent` may forward a prebuilt Decision Support payload, but it should not own
snapshot generation.

### `conversation_loop`

`conversation_loop` remains only the terminal injection sink. It should not
import, instantiate, or call a provider.

## Future Story

**Story 3.22:** Memory-backed Human Model Snapshot Provider Minimal
Implementation

Recommended scope:

- implement a read-only provider
- accept explicit snapshot input and normalize it safely
- if memory becomes involved, keep it mock/fake or constrained to a read-only
  boundary
- do not change gateway/API/CLI surfaces
- do not update Human Model state

## Test Plan for Future Implementation

When Story 3.22 is implemented, tests should verify:

- only the six allowed sections are returned
- unknown keys are dropped
- missing sections become `{}`
- input mappings are not mutated
- memory write does not occur
- Human Model mutation does not occur
- Decision Style and Domain Model content are excluded
- `conversation_loop`, `AIAgent`, gateway, and CLI do not directly depend on the
  provider
- provider output can be passed to `build_decision_support_context()`

## Non-goals

Story 3.21 does not include:

- code implementation
- memory connection
- runtime connection
- gateway/API/CLI exposure
- Human Model updates
- Decision Style integration
- Domain Model integration
- recommendation generation
- final decision generation

## Recommendation Summary

Choose the smallest safe boundary:

1. keep Human Model snapshot generation outside `AIAgent` and
   `conversation_loop`
2. keep the provider internal and read-only
3. allow only the normalized six-section snapshot to cross into Decision
   Support
4. defer memory-backed sourcing to Story 3.22 or later

That gives Hermes a clean future extension point without expanding runtime
authority or introducing side effects now.
