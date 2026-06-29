# Human Model v0.3 Architecture Review

## 1. Purpose

This document reviews the Human Model architecture after Human Model v0.2 integration.

The goal of v0.3 is not to add many new profiles.
The goal is to clarify responsibility boundaries:

- Human Model understands the person.
- Decision Framework helps the person decide.
- Domain Models apply Human Model and Decision Framework to specialized areas.
- Quality Framework evaluates process and output quality.
- Continuous Evolution governs controlled improvement over time.

## 2. Proposed v0.3 Architecture

```text
Human Model
├── Core Layer
│   ├── Identity
│   └── Decision Style  [proposal only]
├── Behavior Layer
│   ├── Energy
│   ├── Habit
│   └── Growth
└── Interaction Layer
    ├── Communication
    └── Coaching
```

## 3. Layer Responsibilities

### 3.1 Core Layer

Core Layer describes durable, cross-domain traits of the person.

It should answer:

- Who is this person becoming?
- What values and long-term direction should Hermes respect?
- How does this person tend to judge, gather information, delegate, and handle risk?

Core Layer should not answer:

- Which investment should be chosen?
- Which career path should be selected?
- Which health action should be taken?
- Which learning curriculum should be followed?

Those are Domain Model or Decision Framework responsibilities.

### 3.2 Behavior Layer

Behavior Layer describes how the person moves through life in practice.

It should answer:

- What energy state supports or limits action?
- What repeating patterns help progress?
- What growth direction gives meaning to change?

Behavior Layer translates Core Layer into sustainable action patterns.

### 3.3 Interaction Layer

Interaction Layer describes how Hermes should engage with the person.

It should answer:

- How should Hermes communicate?
- When should Hermes coach, support, challenge, or step back?
- How can Hermes help without taking ownership away from the user?

Interaction Layer does not decide domain outcomes.
It shapes the way support is delivered.

## 4. Review of Existing Six Profiles

### 4.1 Identity

Recommended layer: **Core Layer**

Role:

- Anchors the Human Model.
- Captures durable values, direction, agency, ownership, and long-term relationship with Hermes.
- Provides the stable reference point for other profiles.

Review result:

- No major contradiction found.
- Identity is correctly positioned as the foundation.
- It should remain domain-neutral.

Risk:

- If Identity starts to include domain-specific goals, it may absorb Career, Business, Investment, or Lifestyle responsibilities.

Boundary rule:

- Identity may describe values behind domain choices.
- Identity should not define domain strategies.

### 4.2 Energy

Recommended layer: **Behavior Layer**

Role:

- Describes energy sources, drainers, low-energy signals, and recovery style.
- Helps Hermes adapt intensity, timing, and task size.

Review result:

- Energy fits Behavior Layer naturally.
- It is not a Health Domain model.
- It should remain an operational readiness profile, not medical interpretation.

Risk:

- Energy can drift into Health Domain if it starts describing diagnoses, treatment, symptoms as clinical data, or training prescriptions.

Boundary rule:

- Energy may guide pacing.
- Health Domain handles medical, physical, and clinical interpretation.

### 4.3 Habit

Recommended layer: **Behavior Layer**

Role:

- Describes recurring behavioral patterns.
- Converts identity and energy into repeatable small actions.
- Helps Hermes suggest friction-reducing next steps.

Review result:

- Habit fits Behavior Layer naturally.
- The current profile already separates routines from Health, Learning, and Decision Profile responsibilities.

Risk:

- Habit can drift into Learning Domain, Health Domain, or Decision Framework if it starts prescribing curricula, treatments, or formal decision rules.

Boundary rule:

- Habit describes recurring patterns and leverage points.
- Domain Models define domain-specific routines when needed.

### 4.4 Growth

Recommended layer: **Behavior Layer**

Role:

- Describes growth orientation, future self, strengths to amplify, and patterns to leave behind.
- Gives meaning to development without becoming a curriculum, career plan, or goal-management system.

Review result:

- Growth fits Behavior Layer if kept as direction and meaning.
- It should not become Learning, Career, or Goal Management.

Risk:

- Growth is the most likely profile to absorb domain concepts because growth often appears through career, learning, health, business, and investment.

Boundary rule:

- Growth may describe the user's broad development direction.
- Domain Models handle specialized growth paths.

### 4.5 Communication

Recommended layer: **Interaction Layer**

Role:

- Describes how Hermes should express information.
- Covers density, tone, feedback style, trust signals, and mode-specific communication.

Review result:

- Communication fits Interaction Layer naturally.
- It is distinct from Coaching because it governs message shape, not developmental stance.

Risk:

- Communication can drift into Coaching if it starts deciding when to challenge, mentor, or guide.

Boundary rule:

- Communication defines delivery style.
- Coaching defines support stance.

### 4.6 Coaching

Recommended layer: **Interaction Layer**

Role:

- Defines how Hermes supports user growth without controlling the user.
- Covers coaching triggers, boundaries, modes, and failure patterns.

Review result:

- Coaching fits Interaction Layer naturally.
- It should not become Decision Framework or Domain Advisor.

Risk:

- Coaching can drift into making life decisions for the user or becoming a domain-specific advisor.

Boundary rule:

- Coaching helps the user think and act.
- Decision Framework structures decisions.
- Domain Models provide domain-specific context.

## 5. Decision Style Addition Review

Decision Style can be added as a **Core Layer profile candidate** without responsibility conflict if its scope is tightly limited.

Decision Style should handle:

- judgment tendencies
- information gathering style
- risk posture
- reflective vs intuitive preference
- AI delegation style
- decision values and tradeoff preferences

Decision Style should not handle:

- investment decisions
- career decisions
- health decisions
- domain-specific recommendations
- final choice ownership

Review result:

- Decision Style is architecturally natural as the second Core Layer element beside Identity.
- Identity explains why choices should respect durable values.
- Decision Style explains how the person tends to choose.
- Decision Framework can later use Decision Style, but Decision Style should not become the framework itself.

## 6. Domain Separation Review

Removing these from Human Model is architecturally safe:

- Investment
- Career
- Health
- Learning

Reason:

- Human Model should describe the person across domains.
- These areas are specialized contexts where the person's traits are applied.
- Keeping them outside Human Model prevents profile explosion and domain leakage.

Recommended relationship:

```text
Human Model -> Domain Models
Domain Models -/-> Human Model
```

Domain Models may reference Human Model.
Human Model should not reference individual Domain Models as dependencies.

## 7. Overall Architecture Judgment

Recommended Human Model v0.3 direction:

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

Judgment:

- Existing six profiles are mostly consistent.
- Energy / Habit / Growth are natural Behavior Layer members.
- Communication / Coaching are natural Interaction Layer members.
- Decision Style is a good Core Layer candidate.
- Domain Models should be separated from Human Model.

## 8. Improvement Proposals

1. **Add Decision Style as a design candidate, not an implementation task yet**
   - Keep it in Core Layer proposal status until Epic 3 clarifies Decision Framework boundaries.

2. **Introduce a Domain Boundary Rule**
   - Any profile that starts making Investment / Career / Health / Learning decisions should be moved to a Domain Model.

3. **Use v0.3 as an architecture review artifact before rewriting v0.2**
   - Do not modify Human Model v0.2 until the review is accepted.
