# Decision Style Position Proposal

## 1. Purpose

This proposal evaluates Decision Style as a formal Human Model Core Layer profile candidate.

This is design only.
It does not create a new profile implementation.

## 2. Proposed Position

```text
Human Model
└── Core Layer
    ├── Identity
    └── Decision Style  [candidate]
```

Decision Style belongs in Core Layer because it describes a durable cross-domain aspect of the person:

- how the user judges
- how the user gathers information
- how the user handles uncertainty
- how the user delegates to AI
- what the user tends to value when deciding

## 3. Relationship to Identity

Identity answers:

> What should Hermes respect about who the user is and is becoming?

Decision Style answers:

> How does the user tend to make judgments under uncertainty?

They are related but not the same.

Identity should not contain detailed decision mechanics.
Decision Style should not redefine the user's values or long-term identity.

## 4. Relationship to Decision Framework

Decision Style is not the Decision Framework.

Decision Style describes the user's natural decision tendencies.
Decision Framework defines a reusable process for making decisions.

Recommended dependency:

```text
Human Model.Decision Style
↓
Decision Framework
```

Decision Framework may use Decision Style to adapt its process.
Decision Style should not prescribe the process by itself.

## 5. In Scope

Decision Style may describe:

- judgment tendencies
- information collection style
- risk posture
- reversibility sensitivity
- reflective vs intuitive preference
- need for comparison or external perspective
- preferred use of AI as researcher, reviewer, challenger, executor, or companion
- decision values such as ownership, long-term compounding, simplicity, safety, speed, or optionality
- signals that the user is overthinking or under-checking

## 6. Out of Scope

Decision Style must not handle:

- investment decisions
- career decisions
- health decisions
- medical advice
- financial recommendations
- domain-specific scoring
- final choice ownership
- Kanban workflow decisions
- quality scoring

These belong elsewhere:

| Topic | Belongs To |
|---|---|
| Investment judgment | Investment Domain + Decision Framework |
| Career choice | Career Domain + Decision Framework |
| Health decision | Health Domain + Decision Framework |
| Learning path | Learning Domain + Decision Framework |
| Output scoring | Quality Framework |
| Process evolution | Continuous Evolution |

## 7. Responsibility Boundary

Decision Style should stay at the level of user tendency.

Good examples:

- The user tends to prefer practical tradeoffs over abstract completeness.
- The user values long-term ownership and continuity.
- The user often wants AI to reduce cognitive load and preserve momentum.
- The user benefits from separating facts, assumptions, and next actions.

Bad examples:

- The user should buy a specific stock.
- The user should choose a specific career path.
- The user should follow a specific health program.
- Hermes should decide for the user.

## 8. Responsibility Conflict Check

### With Identity

No conflict if:

- Identity remains values and direction.
- Decision Style remains judgment tendency and delegation style.

### With Communication

No conflict if:

- Communication controls how Hermes says things.
- Decision Style describes what kind of decision support the user tends to need.

### With Coaching

No conflict if:

- Coaching decides support stance.
- Decision Style informs how to support judgment without taking ownership.

### With Decision Framework

Potential conflict exists.

Mitigation:

- Decision Style must not define formal decision steps.
- Decision Framework owns decision process.
- Decision Style provides adaptation context.

## 9. Recommendation

Decision Style should be accepted as a **Human Model Core Layer candidate**.

It should not be implemented during this review.
It should be scheduled only after the Human Model v0.3 architecture is accepted and Epic 3 Decision Framework boundaries are clear.
