# Decision Framework Architecture Baseline v1

## 1. Purpose

This document establishes the Decision Framework architecture baseline for future Hermes implementation work.

The baseline is based on Story 3.1 interface artifacts:

- `decision-framework-interface-v1.md`
- `input-definition-v1.md`
- `output-definition-v1.md`
- `boundary-definition-v1.md`
- `dependency-diagram-v1.md`
- `future-extension-note-v1.md`

This is an architecture baseline only. It does not implement Decision Framework logic.

## 2. Baseline Decision

**Decision: Accept as Baseline**

Reason:

- The interface keeps Human Model as a person-understanding layer.
- Decision Framework uses Human Model context without modifying it.
- Domain Models remain responsible for specialized domain reasoning.
- The output contract supports decision support without taking the final decision from the user.
- Decision Style can remain a future candidate without breaking v1.

## 3. Frozen Input Contract

Decision Framework v1 may use only the existing six Human Model inputs:

| Input | Baseline Role |
|---|---|
| Identity | Values, self-understanding, continuity |
| Energy | Load, timing, sustainable intensity |
| Habit | Repeatable action shape |
| Growth | Learning direction and adaptation tendency |
| Communication | Receiveable presentation style |
| Coaching | Support stance and autonomy protection |

**Decision Style remains Candidate.**

It is not part of the frozen v1 input contract.

## 4. Frozen Output Contract

Decision Framework v1 may output only decision-support artifacts:

| Output | Baseline Role |
|---|---|
| Perspective | A useful way to view a choice or tradeoff |
| Decision Synthesis | A structured synthesis of options, tensions, constraints, and unknowns |
| Next Step | A small, concrete, preferably reversible action |
| Review Point | A checkpoint or condition for reassessment |

Decision Framework must not output the user's final decision.

## 5. Boundary Baseline

| Component | Owns | Must Not Own |
|---|---|---|
| Human Model | Understanding the person | Decision process or domain expertise |
| Decision Framework | Decision-support process | Final decision or specialized domain judgment |
| Domain Models | Domain-specific knowledge and constraints | Global definition of the person |

Domain examples such as Investment, Career, Health, Learning, Business, Finance, and Mental Health are outside the Decision Framework baseline.

## 6. Dependency Baseline

Allowed dependency direction:

```text
Philosophy
    ↓
Human Model
    ↓
Decision Framework
    ↓
Domain Models
    ↓
Quality Framework
    ↓
Continuous Evolution
```

No reverse dependency is allowed from Human Model to Decision Framework or Domain Models.

## 7. Extension Baseline

Future additions must be additive and optional first.

- Decision Style may be added later as optional Human Model input.
- Domain Models may consume Decision Framework outputs, but must not redefine Human Model.
- Quality Framework may evaluate Decision Framework output quality, but must not change the interface contract implicitly.

## 8. Implementation Readiness

This baseline is ready to guide future implementation work if accepted by human review.

Implementation should proceed only from this contract:

```text
Inputs: Identity, Energy, Habit, Growth, Communication, Coaching
Outputs: Perspective, Decision Synthesis, Next Step, Review Point
Decision owner: User
Decision Style: Candidate only
Domain Models: External consumers / specialized layers
```
