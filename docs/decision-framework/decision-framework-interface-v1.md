# Decision Framework Interface v1

## 1. Purpose

This document defines how the Decision Framework may use the Human Model.

The Decision Framework is not a decision-making authority. It is a process layer that helps the user interpret options, compare perspectives, synthesize tradeoffs, and choose a next step.

## 2. Core Principle

```text
Human Model understands the person.
Decision Framework uses that understanding to support decision processes.
Domain Models apply the process to specialized domains.
```

The dependency direction is fixed:

```text
Human Model
    ↓
Decision Framework
    ↓
Domain Models
```

Human Model must not reference Decision Framework.
Decision Framework may reference Human Model.
Domain Models may reference Decision Framework and Human Model-derived context through the Decision Framework.

## 3. Interface Scope

This interface covers only:

- what Decision Framework can read from Human Model
- what Decision Framework can output
- what Decision Framework must not decide
- how future Decision Style can be added without breaking the interface

This interface does not implement:

- decision logic
- domain-specific judgment
- Decision Style profile
- Domain Models
- Human Model changes

## 4. Human Model Inputs

Decision Framework v1 may consume the existing six Human Model profiles:

| Human Model Profile | Interface Role |
|---|---|
| Identity | Anchors values, continuity, and self-understanding |
| Energy | Sets safe intensity, timing, and cognitive load |
| Habit | Converts decision support into repeatable action |
| Growth | Frames learning, adaptation, and improvement direction |
| Communication | Shapes how options and tradeoffs should be presented |
| Coaching | Shapes support style without taking control |

Decision Style is a candidate profile, but it is not part of the v1 input contract yet.

## 5. Decision Framework Outputs

Decision Framework v1 may output:

| Output | Meaning |
|---|---|
| Perspective | A way to view the decision or tradeoff |
| Decision Synthesis | A structured summary of options, tensions, and likely implications |
| Next Step | A small reversible action the user can take |
| Review Point | A future checkpoint or condition for reassessment |

Decision Framework must not output the final decision as if it owns it.

The decision remains with the user.

## 6. Boundary Rules

Decision Framework must not directly handle domain-specific decisions such as:

- Investment judgment
- Career judgment
- Health judgment
- Learning plan ownership
- Business strategy ownership
- Mental health diagnosis or treatment decisions

These belong to Domain Models.

Decision Framework can provide the process shape, for example:

- clarify the question
- show tradeoffs
- reduce cognitive load
- propose a next step
- define a review point

But it should not become the domain expert.

## 7. Responsibility Comparison

| Layer | Responsibility | Does Not Do |
|---|---|---|
| Human Model | Understands the person | Does not run decision process |
| Decision Framework | Structures decision support | Does not own final decision or domain expertise |
| Domain Models | Applies domain-specific knowledge | Does not define the person globally |

## 8. Dependency Diagram

```text
Philosophy
    ↓
Human Model
    ├─ Identity
    ├─ Energy
    ├─ Habit
    ├─ Growth
    ├─ Communication
    └─ Coaching
    ↓
Decision Framework
    ├─ Perspective
    ├─ Decision Synthesis
    ├─ Next Step
    └─ Review Point
    ↓
Domain Models
    ├─ Investment Domain
    ├─ Career Domain
    ├─ Health Domain
    ├─ Learning Domain
    └─ other specialized domains
    ↓
Quality Framework
    ↓
Continuous Evolution
```

No reverse dependency is allowed from Human Model to Decision Framework or Domain Models.

## 9. Review Worker Check

| Check | Result |
|---|---|
| Human Model separation | Pass: Human Model remains a person-understanding layer |
| Domain Model separation | Pass: domain-specific judgments are excluded |
| Decision Style consistency | Pass: candidate is reserved for future input extension |
| Circular dependency | Pass: dependency direction is one-way |
| Future extensibility | Pass: input contract can add optional Decision Style later |

## 10. Recommended Status

Recommended workflow state for this interface artifact:

```text
Review
```

Reason:

- design artifact exists
- no implementation has been made
- Review Worker should validate boundary clarity before Accepted
