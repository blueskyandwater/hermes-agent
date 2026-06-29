# Decision Framework Input Definition v1

## 1. Purpose

This document defines the Human Model information that Decision Framework v1 may receive.

## 2. Input Contract

Decision Framework v1 accepts Human Model-derived context from the existing six profiles only.

| Input | Required? | Purpose | Boundary |
|---|---:|---|---|
| Identity | Yes | Values, continuity, self-understanding | Does not decide the action |
| Energy | Yes | Cognitive load, timing, safe intensity | Does not diagnose health |
| Habit | Yes | Repeatable action pattern | Does not create a full productivity system |
| Growth | Yes | Learning direction and adaptation | Does not become Learning/Career Domain |
| Communication | Yes | Presentation style and receiveability | Does not manipulate the user |
| Coaching | Yes | Support stance and autonomy protection | Does not replace user agency |

## 3. Decision Style Candidate

Decision Style is intentionally excluded from the v1 input contract.

Future optional input:

```text
DecisionStyle?: {
  information_collection_style,
  risk_orientation,
  deliberation_style,
  delegation_style,
  decision_values
}
```

The interface should be designed so this can be added later as optional context.

## 4. Excluded Inputs

The following are not Human Model inputs for Decision Framework v1:

- Investment positions
- Career goals as domain strategy
- Health metrics as medical interpretation
- Learning curriculum ownership
- Business operating decisions

Those belong to Domain Models.

## 5. Input Use Rules

Decision Framework may use inputs to:

- adapt explanation length
- choose a lower-friction next step
- surface value conflicts
- avoid overloading the user
- preserve user agency

Decision Framework must not use inputs to:

- make the final decision
- override explicit user intent
- infer domain expertise from personality traits
- convert Human Model into a domain profile
