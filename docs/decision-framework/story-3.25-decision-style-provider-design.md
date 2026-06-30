# Story 3.25 - Decision Style Provider Design

## Background

Story 3.21 fixed the Human Model boundary around a normalized six-section support snapshot.
Story 3.22 clarified the current implementation status: `HumanModelSnapshotProvider` exists as a read-only provider boundary, while fully defined memory-backed Human Model sourcing remains deferred.
Story 3.23 introduced a separate Domain Model interface boundary so domain-specific context can remain distinct from the Human Model.
Story 3.24 then defined the Decision Style interface boundary and fixed its meaning: Decision Style is a soft hint only, not policy, not hard rule enforcement, and not final decision logic.

The next design question is narrower and more operational:

> If Hermes later wants to retrieve Decision Style context internally, what provider contract should supply that context while preserving user agency, preventing hidden policy behavior, and keeping Decision Style separate from Human Model and Domain Model?

Current confirmed baseline:

- Human Model remains a read-only six-section support snapshot.
- Domain Model remains a separate domain-scoped context boundary.
- Decision Style remains a separate soft-hint boundary.
- Decision Style is not yet implemented as a product/runtime layer.
- Memory mutation is still deferred.
- Gateway/API/CLI publication is not yet opened as an external surface.
- No approved design yet exists for automatic conversation-time inference or public retrieval.

This story is design-only. It defines the provider boundary for future internal, read-only Decision Style retrieval. It does not implement runtime wiring, storage integration, mutation, policy behavior, or public exposure.

## Goals

- Define an internal, read-only `DecisionStyleProvider` contract.
- Preserve the Story 3.24 meaning of Decision Style as a soft hint only.
- Keep Decision Style separate from Human Model and Domain Model.
- Define what trusted internal callers may request from a provider.
- Define a minimal, inspectable output shape for provider results.
- Make override precedence clear when explicit turn instructions conflict with stored or default style hints.
- Establish provenance, freshness, and trust expectations before any future integration work.
- Establish logging and redaction constraints before any runtime expansion.

## Non-goals

This story does **not** do any of the following:

- implement a Decision Style storage system
- implement memory-backed sourcing
- implement Gateway/API/CLI exposure
- implement provider wiring into conversation runtime
- implement automatic conversation-time inference
- implement policy enforcement
- implement hard-rule evaluation
- implement final decision generation
- implement recommendation authority transfer
- mutate Human Model, Domain Model, or Decision Style state
- define public schema guarantees for external callers
- define dispatcher, worker, or Kanban behavior

## Relationship to Story 3.24

Story 3.24 answered **what Decision Style is** and **what it must never become**.
This story answers a narrower question: **if a trusted internal caller later retrieves Decision Style, what provider-shaped boundary should carry it safely?**

The dependency direction is therefore:

```text
Story 3.24 Decision Style Interface Design
  ↓
Story 3.25 Decision Style Provider Design
  ↓
future internal read-only retrieval work (if approved)
```

Story 3.25 must inherit the Story 3.24 constraints unchanged:

- Decision Style is advisory only.
- Decision Style may influence framing, ordering, emphasis, pacing, uncertainty expression, or comparison style.
- Decision Style must not decide for the user.
- Decision Style must not become hidden policy.
- Decision Style must not be merged into Human Model or Domain Model.

## Provider responsibilities

A future `DecisionStyleProvider` may be responsible for only the following:

1. Read Decision Style data from an explicitly trusted, read-only source boundary.
2. Normalize that data into a stable internal Decision Style result shape.
3. Drop unknown or unsafe fields that would incorrectly expand Decision Style into policy or authority.
4. Return provenance, freshness, and trust metadata alongside the normalized value.
5. Return an inspectable empty/default result when no trusted style data exists.
6. Make no claim that the returned hint is mandatory, current, or globally correct unless metadata explicitly supports that claim.
7. Preserve reviewability so a trusted internal caller can explain what hint was present and why it was considered advisory only.

## Non-responsibilities

A future `DecisionStyleProvider` must **not** be responsible for any of the following:

- deciding what the user should do
- deciding whether Hermes should obey or suppress explicit user instructions
- generating final recommendations
- evaluating hard constraints or compliance rules
- mutating stored style state
- mutating Human Model or Domain Model state
- inferring new durable style traits automatically from one conversation
- rewriting user identity, values, or priorities
- acting as a hidden ranking engine for all decisions
- publishing Decision Style externally through gateway/API/CLI
- resolving domain facts or domain evidence

## Input sources / explicit-input-first

The provider should follow an **explicit-input-first** rule.

Preferred source order:

1. Explicit trusted input supplied directly by an internal caller for the current bounded task.
2. A future approved read-only persisted source with provenance metadata.
3. No style hint at all.

Interpretation rules:

- If an explicit style input is provided for the current task, it should take precedence over any future stored default.
- If no explicit style input exists, a future stored value may be returned only if the source is trusted, reviewable, and clearly marked as advisory.
- If trust, freshness, or provenance is weak, the provider should prefer returning no style hint rather than overstating certainty.
- Absence of style data is acceptable and must not be treated as an error.

This keeps the safe baseline aligned with read-only-first design and avoids accidental authority transfer from stale or inferred context.

## Output shape / normalization contract

A minimal internal provider result may look like this:

```python
{
    "decision_style": {
        "framing_preferences": {
            "brevity": "prefer-concise",
            "comparison_style": "options-side-by-side",
            "uncertainty_style": "state-confidence-and-tradeoffs",
            "action_posture": "prefer-small-reversible-steps",
        },
        "interaction_preferences": {
            "challenge_level": "gentle-push",
            "pace": "steady",
            "depth_default": "practical-first",
        },
        "decision_support_preferences": {
            "option_count_default": 3,
            "highlight_tradeoffs": true,
            "separate_fact_and_opinion": true,
        },
    },
    "metadata": {
        "source": "explicit-input",
        "source_id": null,
        "captured_at": null,
        "freshness": "current-turn",
        "trust_level": "high",
        "advisory_only": true,
        "schema_version": "v1",
    },
}
```

Normalization rules:

- Unknown top-level keys should be dropped.
- Unknown nested keys may be dropped or preserved only in a clearly non-authoritative extension area if a future story explicitly allows that.
- Values that imply authority transfer should be rejected or normalized away.
- The result must preserve `advisory_only: true` or an equivalent internal invariant.
- The provider should be allowed to return an empty result shape, for example:

```python
{
    "decision_style": {},
    "metadata": {
        "source": "none",
        "source_id": null,
        "captured_at": null,
        "freshness": "unknown",
        "trust_level": "none",
        "advisory_only": true,
        "schema_version": "v1",
    },
}
```

## Read-only provider assumptions

This design assumes the following:

- The provider is internal-only.
- The provider is read-only.
- The provider does not write to memory, files, or user profile state.
- The provider does not open gateway/API/CLI surfaces.
- The provider does not independently trigger decision-support flows.
- The provider is consumed only by trusted internal callers that already understand Decision Style is advisory.
- The provider boundary may exist before any concrete persisted backend exists.

This matches the same safe pattern already clarified in Story 3.22: provider boundary design may exist before a full source integration is approved or implemented.

## Override precedence vs explicit turn instruction

Decision Style must not override direct user instructions given in the current turn.

Recommended precedence:

1. Explicit current-turn user instruction
2. Explicit trusted task-scoped style input
3. Future approved stored Decision Style hint
4. No style hint

Examples:

- If the user says "give me the long version," a stored brevity preference must not suppress that request.
- If the user says "just decide for me," the provider still does not grant policy authority; the assistant behavior remains bounded by broader system rules and user-agency constraints.
- If the stored style suggests concise framing but the current task needs careful safety explanation, the runtime may choose the safer response while still treating the style as advisory.

The provider itself should not perform this full policy resolution. It should only return normalized style data plus metadata that helps a caller apply the precedence rules safely.

## Provenance / freshness / trust

Decision Style is especially vulnerable to overgeneralization if provenance is missing.

A future provider should therefore attach metadata that answers at least:

- **Where did this hint come from?**
  - explicit task input
  - future approved stored source
  - unknown / none
- **How fresh is it?**
  - current-turn
  - recent
  - stale
  - unknown
- **How trustworthy is it?**
  - high
  - medium
  - low
  - none
- **Was it human-approved or merely observed?**
  - explicitly user-confirmed
  - inferred but unconfirmed
  - unknown

Safe interpretation rules:

- Unconfirmed or low-trust hints should be easy to ignore.
- Stale hints should not silently shape high-impact decisions.
- Inferred style should never be presented as durable truth without separate approval.
- A future implementation should prefer omission over false confidence.

## Safety considerations

Decision Style is high-risk because it can become manipulative if its boundary is vague.

Required safety rules:

- Decision Style must remain advisory only.
- Decision Style must not become a hidden control layer.
- Decision Style must not replace explicit user instructions.
- Decision Style must not replace Human Model, Domain Model, or domain evidence.
- Decision Style must not be used to justify high-impact action without normal approval boundaries.
- Decision Style must not be silently inferred and then treated as durable truth.
- Decision Style must remain independently inspectable from Human Model and Domain Model.
- If the system is uncertain whether a style hint is valid, it should prefer a neutral response posture.

High-risk future expansions that require separate design and approval:

- automatic inference from conversations
- write-back or mutation flows
- external schema exposure
- coupling Decision Style to execution authority
- coupling Decision Style to automated recommendation ranking
- coupling Decision Style to domain-specific decision engines

## Redaction / logging considerations

If Decision Style is ever retrieved at runtime, logs should minimize unnecessary personal detail.

Recommended logging posture:

- Log only that a Decision Style hint was present, absent, or ignored when possible.
- Avoid logging raw personal preference text if a normalized label is sufficient.
- Treat provenance, trust, and freshness metadata as more important than verbose content.
- Redact free-text notes unless a future approved design explicitly requires them.
- Keep Decision Style logs reviewable and bounded.
- Do not expose raw provider payloads to external gateway/API/CLI consumers by default.

Minimal safe log example:

```text
DecisionStyleProvider used: source=explicit-input freshness=current-turn trust=high advisory_only=true
```

Less safe example that should be avoided by default:

```text
Full decision-style payload with free-text behavioral notes and historical interpretation
```

## Open questions

- Should Decision Style use a strictly enumerated schema from the start, or allow a small extension map for future experimentation?
- Should provenance distinguish user-confirmed preferences from assistant-observed but unconfirmed patterns?
- How should future callers represent partial conflict between current-turn instruction and stored style hint?
- Should a future provider expose confidence at the field level, or only at the payload level?
- What is the minimum metadata required before a stored Decision Style hint may be considered usable at all?
- How should future reviews detect drift where Decision Style slowly absorbs policy or recommendation authority?
- If Domain Models later want domain-specific style overlays, how should those remain subordinate to general Decision Style without mixing boundaries?

## Next steps

1. Keep this document as a design-only baseline.
2. Do **not** implement runtime wiring, storage, or mutation from this story alone.
3. If future work is approved, create a separate story for Decision Style source definition and provenance rules.
4. If future work is approved, create a separate story for runtime caller behavior and explicit precedence handling.
5. If future work is approved, create a separate story for logging/redaction review before any external exposure.
6. Reconfirm that Human Model, Domain Model, and Decision Style remain independently inspectable boundaries before any implementation begins.
