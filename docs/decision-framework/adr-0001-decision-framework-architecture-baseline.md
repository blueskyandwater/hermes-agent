# ADR-0001: Accept Decision Framework Architecture Baseline v1

## Status

Accepted as Baseline

## Review Date

2026-06-29

## Decision

Adopt the Story 3.1 Decision Framework interface as **Decision Framework Architecture Baseline v1**.

The frozen v1 interface is:

Input:

- Identity
- Energy
- Habit
- Growth
- Communication
- Coaching

Output:

- Perspective
- Decision Synthesis
- Next Step
- Review Point

Decision Style remains a Human Model Core candidate and is not included in v1 input.

## Context

Story 3.1 established an interface between Human Model and Decision Framework.

The architecture requires a clear dependency direction:

```text
Human Model
    ↓
Decision Framework
    ↓
Domain Models
```

Human Model describes the person. Decision Framework uses that context to support decision processes. Domain Models handle specialized domains such as Investment, Career, Health, Learning, Business, and Finance.

The framework must not decide for the user.

## Alternatives

### Alternative 1: Include Decision Style immediately

Rejected for now.

Decision Style is architecturally promising, but including it now would expand the interface before implementation proves the need.

### Alternative 2: Let Domain Models feed directly into Human Model

Rejected.

This would create reverse dependency and risk turning Human Model into a collection of domain profiles.

### Alternative 3: Expand outputs with recommendations and final decisions

Rejected.

This would increase decision takeover risk and violate the principle that the final decision belongs to the user.

### Alternative 4: Keep architecture unfrozen until implementation

Rejected.

Implementation without a baseline would likely blur Human Model, Decision Framework, and Domain Model responsibilities.

## Consequences

Positive:

- Future implementation has a stable contract.
- Human Model remains person-centered.
- Domain Models remain separated.
- Decision Style can be added later without breaking v1.
- User agency is protected by output limits.

Tradeoffs:

- Some domain-specific decision support must wait for Domain Model design.
- Decision Style benefits are deferred.
- Implementers must resist adding new outputs during early implementation.

## Follow-up

Future Decision Framework implementation should conform to this ADR unless a new ADR supersedes it.
