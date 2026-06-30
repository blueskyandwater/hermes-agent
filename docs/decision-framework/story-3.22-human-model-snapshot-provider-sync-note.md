# Story 3.22 - Human Model Snapshot Provider Sync Note

## Purpose

This note aligns the Story 3.22 label with the current repository reality so that
later work does not over-assume what is already implemented.

The key clarification is:

- `HumanModelSnapshotProvider` **is implemented**.
- A full **memory-backed source integration is not implemented yet**.
- The safest current interpretation is therefore:
  - **read-only provider boundary implemented**
  - **memory-backed sourcing still deferred**

## Current status

The repository currently has a working `HumanModelSnapshotProvider` in
`agent/human_model_snapshot.py`.

That provider can:

- accept an explicit snapshot mapping
- optionally read from a configured read-only source boundary
- normalize the result to the six allowed Human Model sections
- exclude unknown, Decision Style, and domain-specific keys
- avoid mutating caller input

At the same time, the repository does **not** currently prove a full productized
memory-backed Human Model source integration.

## What is implemented

Confirmed implemented today:

- `normalize_human_model_snapshot(snapshot)` exists as a pure normalizer.
- `HumanModelSnapshotProvider` exists as a read-only provider boundary.
- The provider can read:
  - an explicit snapshot
  - a mapping source
  - a zero-argument callable source
- The provider output is always normalized to these six sections only:
  - `identity`
  - `energy`
  - `habit`
  - `growth`
  - `communication`
  - `coaching`
- Tests confirm:
  - unknown keys are dropped
  - Decision Style is excluded
  - domain-specific keys are excluded
  - input mappings are not mutated
  - the provider does not call memory write or runtime hook methods

## What is not implemented yet

Not confirmed implemented today:

- a dedicated memory-backed Human Model store integration with defined provenance
- schema/version handling for stored Human Model snapshots
- trust/freshness metadata for memory-derived snapshots
- runtime wiring that automatically retrieves Human Model context from durable memory
- gateway/API/CLI exposure for invoking or configuring the provider
- Human Model mutation/update behavior
- docs/profile parsing as a production source

So while the provider can read from a generic read-only source boundary, the repo
should **not** currently claim that a full memory-backed Human Model snapshot
system is already shipped.

## Correct interpretation of "memory-backed"

The Story 3.22 label is slightly ahead of the implementation if read literally.

Safe interpretation:

> Story 3.22 established the minimal read-only provider implementation needed for
> future memory-backed sourcing, but it did not complete or open full
> memory-backed source integration.

Unsafe interpretation:

> Hermes already has a production-ready memory-backed Human Model snapshot
> pipeline.

That stronger claim is not yet supported by the current code or docs baseline.

## Why this wording matters

If later stories assume "memory-backed" is already complete, they may
incorrectly build on top of missing guarantees such as:

- provenance
- freshness
- trust semantics
- safe memory read boundaries
- external exposure rules
- mutation controls

This note keeps the extension path honest:

```text
implemented now:
read-only provider boundary + normalization contract

implemented later:
real memory-backed source integration and its safety rules
```

## Impact on Story 3.23

Story 3.23 remains valid as written.

Why:

- Story 3.23 depends on the existence of a read-only provider-shaped boundary.
- That boundary does exist today.
- Story 3.23 does not require a completed memory-backed Human Model source.
- Story 3.23 only needs the Human Model boundary to remain stable and separate
  from future Domain Model work.

So this sync note is a wording correction, not a blocker for Story 3.23.

## Impact on Story 3.24

Story 3.24 should use this note as a baseline assumption:

- Human Model snapshot boundary exists.
- Domain Model must remain separate from that boundary.
- Story 3.24 must not assume that durable memory sourcing for Human Model is
  already fully designed or opened.

If Story 3.24 adds Decision Style interface work, it should continue treating
Human Model, Domain Model, and Decision Style as separate layers.

## Recommended baseline statement

For future planning and design notes, the safest baseline wording is:

> `HumanModelSnapshotProvider` is implemented as a read-only normalization and
> source-boundary layer. Automatic or fully defined memory-backed Human Model
> source integration is not yet enabled.

## Next steps

1. Keep Story 3.23 and later docs aligned with this narrower baseline.
2. Treat provenance, freshness, trust, and source-shaping as required design
   inputs before calling the provider truly memory-backed in a product sense.
3. If a later story implements durable memory sourcing, document the exact source
   contract explicitly rather than relying on the Story 3.22 title alone.
4. Preserve the current no-mutation, no-runtime-exposure boundary unless a
   separate approved story opens those surfaces.

## Summary

The current repo status is best described as:

- `HumanModelSnapshotProvider` implemented: **yes**
- read-only provider boundary implemented: **yes**
- full memory-backed source integration implemented: **not yet**

This note exists to keep later stories precise without rolling back the valid
progress already made.