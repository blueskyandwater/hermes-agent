# Hermes Human Model v0.2

## 1. Purpose

Hermes Human Model v0.2 integrates the six completed Epic 2 Human Model foundation stories into one coherent model.

This document does **not** add new profiles.
It does **not** expand Human Model scope beyond Epic 2.
It closes the conceptual integration work for the existing six foundations only:

- Identity
- Energy
- Habit
- Growth
- Communication
- Coaching

The purpose of v0.2 is to give Hermes a stable, reviewable Human Model baseline before later work proceeds into Decision Framework or other future epics.

---

## 2. Scope

### Included

Human Model v0.2 includes only these six profile artifacts:

| Story | Profile | Artifact |
|---|---|---|
| Story 2.1 | Identity Profile | `docs/human-model/identity-profile-v1.md` |
| Story 2.2 | Energy Profile | `docs/human-model/energy-profile-v1.md` |
| Story 2.3 | Habit Profile | `docs/human-model/habit-profile-v1.md` |
| Story 2.4 | Growth Profile | `docs/human-model/growth-profile-v1.md` |
| Story 2.5 | Communication Profile | `docs/human-model/communication-profile-v1.md` |
| Story 2.6 | Coaching Profile | `docs/human-model/coaching-profile-v1.md` |

### Excluded

Human Model v0.2 does not create or define any additional profiles.
It does not implement runtime behavior, memory updates, research tasks, routing logic, Constitution rules, Kanban workflow changes, or Git operations.

---

## 3. Integrated Model

Human Model v0.2 treats the six profiles as one layered support model:

```text
Identity
  ↓
Energy
  ↓
Habit
  ↓
Growth
  ↓
Communication
  ↓
Coaching
```

This order is not a rigid execution pipeline.
It is a conceptual dependency map for how Hermes should understand the user over time.

- **Identity** anchors the user's durable self, values, agency, mission, and long-term direction.
- **Energy** describes the conditions under which the user can express capability without unnecessary pressure.
- **Habit** describes recurring behavior patterns that carry identity and energy into repeated action.
- **Growth** describes the user's future-facing direction and the kind of person the user wants to become.
- **Communication** describes how Hermes should speak so the user's thinking becomes clearer and easier to act on.
- **Coaching** describes how Hermes should support reflection, momentum, perspective, and small concrete movement while preserving user agency.

---

## 4. Profile Responsibilities

### 4.1 Identity Profile

Identity Profile is the root of the Human Model.

It defines durable foundations such as:

- human agency
- ownership and locality
- long-term compounding
- practical building
- mission and purpose
- values that should not be overwritten by Hermes

Identity is the answer to:

> Who is the user, and what must Hermes respect over the long term?

All later profiles should remain compatible with Identity.

### 4.2 Energy Profile

Energy Profile defines how Hermes should understand the user's capacity patterns.

It covers:

- energy sources
- energy drainers
- flow conditions
- recovery patterns
- low-energy signals
- supportive response by energy state

Energy is the answer to:

> When and how can the user best express capability without being forced or overloaded?

Energy Profile must not become a health diagnosis, medical model, shame mechanism, or aggressive optimization system.

### 4.3 Habit Profile

Habit Profile defines the user's durable behavior patterns.

It covers:

- keystone habits
- growth-supporting habits
- recovery habits
- decision-supporting habits
- anti-habits
- coaching leverage points

Habit is the answer to:

> Which repeated actions and patterns help the user's identity and growth become real in daily life?

Habit Profile must not become a todo list, streak tracker, compliance system, or character judgment.

### 4.4 Growth Profile

Growth Profile defines the user's long-term direction of becoming.

It covers:

- future self direction
- qualities to strengthen
- strengths to amplify
- habits to build over years
- patterns to leave behind
- coaching growth strategy

Growth is the answer to:

> What kind of person does the user want to become, and what direction feels increasingly true over time?

Growth Profile must not become a goal management system, curriculum, career plan, or performance scorecard.

### 4.5 Communication Profile

Communication Profile defines the dialogue patterns that make Hermes useful and trustworthy.

It covers:

- communication style
- feedback style
- perspective presentation
- decision-support communication
- information density
- trust signals
- coaching-related communication style

Communication is the answer to:

> How should Hermes speak so the user's thinking becomes clearer, decisions become easier, and momentum is preserved?

Communication Profile must not become a global personality setting, UI setting, fixed writing template, or Coaching Profile replacement.

### 4.6 Coaching Profile

Coaching Profile defines Hermes's long-term support stance.

It covers:

- coaching philosophy
- conceptual coaching modes
- coaching triggers
- coaching boundaries
- coaching style
- success conditions
- failure modes
- integration of the other Human Model layers into supportive interaction

Coaching is the answer to:

> How should Hermes accompany the user's growth without taking over the user's life, judgment, or agency?

Coaching Profile must not become therapy, automatic mode-switching logic, a productivity command system, or a control mechanism.

---

## 5. Integration Rules

### Rule 1: Identity anchors all profiles

No Human Model layer should override the user's agency, values, ownership, or long-term self-direction.

### Rule 2: Energy gates intensity

Hermes should adjust challenge level, density, and next-step size based on energy context when it is known or reasonably inferred.

### Rule 3: Habit converts direction into repeated action

Hermes should prefer small repeatable behavior patterns over abstract advice when the user needs momentum.

### Rule 4: Growth gives meaning to improvement

Hermes should support growth as user-owned becoming, not as external performance pressure.

### Rule 5: Communication determines receiveability

Even correct advice is low-value if it is too dense, mistimed, cold, vague, or difficult to act on.

### Rule 6: Coaching integrates without controlling

Coaching should use Identity, Energy, Habit, Growth, and Communication as context, while leaving final judgment and life direction with the user.

---

## 6. Workflow State Summary

Based on Hermes Development Workflow v1 and Definition of Done v1:

| Story | Artifact | Review Evidence | Judge | Metrics | Recommended State |
|---|---|---|---|---|---|
| Story 2.1 Identity | Present | Review Worker PASS recorded | Missing / not found | Missing / not found | Accepted candidate |
| Story 2.2 Energy | Present | Review Worker PASS recorded | Missing / not found | Missing / not found | Accepted candidate |
| Story 2.3 Habit | Present | Review Worker PASS recorded | Missing / not found | Missing / not found | Accepted candidate |
| Story 2.4 Growth | Present | Missing / not found | Missing / not found | Missing / not found | Review continues |
| Story 2.5 Communication | Present | Missing / not found | Missing / not found | Missing / not found | Review continues |
| Story 2.6 Coaching | Present | Missing / not found | Missing / not found | Missing / not found | Review continues |

This document integrates all six artifacts conceptually, but it does not change Kanban state.

---

## 7. Epic 2 Integration Result

Epic 2 has enough artifact coverage to form a coherent Human Model baseline.

However, Epic 2 should not be marked Done solely because this integration document exists.
Under Definition of Done v1, Epic completion still depends on:

- review evidence for the remaining unreviewed stories
- acceptance of the integrated model
- close note review
- Kanban state update by an explicit later action

Recommended Epic 2 state after this artifact:

> **Accepted candidate**, pending remaining review evidence and explicit Kanban closure.

---

## 8. Next Epic Handoff

Human Model v0.2 provides a stable foundation for later Decision Framework work.

The next epic should treat Human Model as context, not as something to expand by default.
Future Decision Framework work should answer:

> Given this user's Identity, Energy, Habit, Growth, Communication, and Coaching context, how should Hermes support decisions without replacing the user's judgment?

No additional Human Model profile should be added unless a future backlog item explicitly adopts it through the improvement lifecycle.
