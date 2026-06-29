# Decision Framework Extension Policy v1

## 1. Purpose

This policy defines how Decision Framework Architecture Baseline v1 may be extended without breaking the interface.

## 2. Core Rule

All extensions must be additive, optional, and reviewed before becoming required.

## 3. Decision Style Extension

Decision Style may be added later only as an optional Human Model input.

Allowed future shape:

```text
DecisionFrameworkInputV2
= DecisionFrameworkInputV1
+ optional DecisionStyle
```

Decision Style must remain descriptive:

- judgment tendency
- information collection style
- risk orientation
- deliberation style
- AI delegation style
- values emphasized during decisions

Decision Style must not become:

- investment advice
- career advice
- health advice
- domain judgment
- final decision authority

## 4. Domain Models Extension

Domain Models may use Decision Framework outputs to structure specialized reasoning.

Allowed:

```text
Decision Framework output
    ↓
Domain Model interpretation
    ↓
Domain-specific next evidence / constraints / review point
```

Not allowed:

```text
Domain Model
    ↓
redefines Human Model
```

## 5. Quality Framework Extension

Quality Framework may evaluate:

- whether the output preserved user agency
- whether the boundary was respected
- whether the next step was concrete
- whether review points were clear

Quality Framework must not silently change the Decision Framework input or output contract.

## 6. Output Extension Rule

Do not add new output types unless all are true:

1. The need cannot be expressed as Perspective, Decision Synthesis, Next Step, or Review Point.
2. The new output does not decide for the user.
3. The new output does not duplicate Domain Model responsibility.
4. A review note or ADR documents the change.

## 7. Compatibility Promise

Existing v1 consumers should continue to work if future optional inputs are absent.

The v1 contract remains valid until explicitly superseded by a reviewed v2 baseline.
