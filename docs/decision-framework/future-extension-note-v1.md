# Decision Framework Future Extension Note v1

## 1. Purpose

This document explains how Decision Style can be added later without breaking Decision Framework Interface v1.

## 2. Current Position

Decision Style is a Human Model Core Layer candidate.

It is not implemented and is not part of the v1 required input contract.

## 3. Future Addition Strategy

Decision Style should be added as optional input first:

```text
DecisionFrameworkInputV2 = DecisionFrameworkInputV1 + optional DecisionStyle
```

This preserves compatibility with v1.

## 4. Candidate Fields

Possible future fields:

| Field | Meaning |
|---|---|
| information_collection_style | How the user gathers information before deciding |
| risk_orientation | How the user tends to handle uncertainty and downside |
| deliberation_style | Fast/slow, intuitive/analytical tendency |
| delegation_style | How much the user wants AI to draft, compare, or execute |
| decision_values | What the user tends to prioritize during choices |

## 5. Non-Goals

Decision Style must not become:

- investment decision logic
- career decision logic
- health decision logic
- a domain-specific recommendation engine
- a replacement for user agency

## 6. Compatibility Check

Adding Decision Style later should not require changing the current outputs:

- Perspective
- Decision Synthesis
- Next Step
- Review Point

It should only improve how those outputs are shaped.

## 7. Migration Path

Recommended path:

1. Keep Decision Style as candidate during Interface v1 review
2. Use Interface v1 with existing six Human Model profiles
3. Validate whether Decision Framework needs Decision Style explicitly
4. If needed, create Decision Style Profile as a separate approved story
5. Add it as optional input in Interface v2

## 8. Review Result

Decision Style can be added without breaking the interface if it remains optional and descriptive.
