# Hermes Planning System Note v1

## 1. Goal

This note defines the role, artifacts, gate model, and Kanban automation boundaries of the Hermes Planning System.

The purpose is to prevent Implementation work or dispatcher automation from moving forward before Planning has clarified what should be built, why it should be built, and under what conditions it may be handed off.

Planning is therefore not just an idea memo. It is a boundary layer that fixes intent before execution and keeps automation from treating unplanned backlog items as executable work.

---

## 2. Background

Hermes development has advanced significantly through Story 3.1 to Story 3.22.

During that sequence:

- The implementation line became stronger.
- Autopilot Policy and Kanban Autopilot Rules became clearer.
- Documentation, review, commit, and sync modes were separated more safely.
- Worker and dispatcher automation became more useful for bounded execution.

However, the planning side is still incomplete:

- Planning Gate remains blocked.
- Product Vision, Roadmap, Definition of Ready, and Planning Gate Policy documents are still thin or not yet established as a connected system.
- A previous incident showed that a card registered as backlog can be picked up by dispatcher automation if it becomes executable.
- Planning and Implementation can easily mix the meaning of `done`, `ready`, and actual artifact reality.

This note strengthens Planning as the control layer before Implementation.

---

## 3. Planning System Role

Planning is an automation control layer, not merely a proposal area.

It defines what may become executable and what must remain only an idea, backlog item, or design candidate.

### 3.1 Responsibilities

The Planning System is responsible for:

1. **Deciding what to build**
   - Convert raw ideas, backlog entries, and improvement candidates into structured product work.

2. **Fixing why it should be built**
   - Connect work to Philosophy, Product Vision, Epic Purpose, and user value.

3. **Clarifying dependencies between Epics**
   - Identify which Epics, Stories, or process documents must exist before other work can safely proceed.

4. **Defining handoff conditions for Implementation**
   - Specify when a Story is ready to become implementation work.

5. **Creating boundaries against Autopilot drift**
   - Prevent dispatcher, workers, or status automation from executing work that is still only planning-level.

### 3.2 What Planning Protects

Planning protects Hermes development from:

- implementation with unclear purpose
- priority inversion
- starting work before dependencies are understood
- mismatch between `done` status and actual artifact / commit / push reality
- accidental auto-execution of Planning cards

---

## 4. Planning Artifacts

Planning should be represented by a small set of durable process documents.

### 4.1 Core Documents

The core Planning documents are:

- **Hermes Planning System Note v1**
- **Hermes Product Vision v1**
- **Definition of Ready v1**
- **Roadmap v1**
- **Planning Gate Policy v1**

### 4.2 Supporting Documents

Supporting documents may include:

- **Product Backlog Structure v1**
- **Epic Prioritization Policy v1**
- **Planning-to-Implementation Handoff v1**

### 4.3 Artifact Responsibilities

| Artifact | Responsibility |
|---|---|
| Hermes Planning System Note | Overall design of the planning layer |
| Hermes Product Vision | Product meaning and north star |
| Definition of Ready | Handoff judgment from Planning to Implementation |
| Roadmap | Priority order and sequencing |
| Planning Gate Policy | Gate open / close rules |
| Product Backlog Structure | How backlog items are classified and shaped |
| Epic Prioritization Policy | How Epics are compared and ordered |
| Planning-to-Implementation Handoff | What must be passed to an implementation card |

---

## 5. Relationship Between Philosophy, Vision, Roadmap, Epic, and Story

Planning should preserve a clear hierarchy from long-term meaning to concrete work.

```text
Philosophy
  ↓
Product Vision
  ↓
Roadmap
  ↓
Epic Planning
  ↓
Story / Implementation
```

### 5.1 Philosophy

Philosophy defines the reason Hermes exists and the durable principles that should not be casually rewritten.

It answers:

- Why does Hermes exist?
- What kind of relationship should Hermes preserve with the user?
- What values should remain stable even when implementation details change?

### 5.2 Product Vision

Product Vision converts Philosophy into a product north star.

It answers:

- What is Hermes becoming as a product or personal AI operating layer?
- What product direction should Epics support?
- What should Hermes avoid becoming?

### 5.3 Roadmap

Roadmap defines the order in which the Product Vision becomes real.

It answers:

- Which Epics come first?
- Which dependencies must be resolved before later work?
- What should be deferred even if it is interesting?

### 5.4 Epic Planning

Epic Planning breaks roadmap areas into pre-implementation design.

It answers:

- What is the Epic purpose?
- What are the Story candidates?
- What scope, non-goals, dependencies, risks, and review criteria apply?

### 5.5 Story / Implementation

Story / Implementation is the executable work unit.

It should start only after Epic Planning has clarified enough context to support a safe handoff.

---

## 6. Planning Gate

Planning Gate controls when work may move from backlog or planning into implementation routing.

The gate should be gradual rather than a single open / closed switch.

### 6.1 Level 0: Fully Blocked

Purpose: prevent unplanned execution.

Allowed:

- Register backlog items.
- Preserve ideas for later planning.

Prohibited:

- Dispatcher execution.
- Worker execution.
- Implementation card creation from unplanned items.
- Planning Gate release.

### 6.2 Level 1: Planning Active

Purpose: allow planning work while still preventing implementation.

Allowed:

- Planning cards may perform read-only or design-only work.
- Docs proposals may be drafted when explicitly requested.
- Current state may be inspected.
- Boundaries, dependencies, and recommendations may be written.

Prohibited:

- Code implementation.
- Runtime behavior changes.
- Dispatcher execution of Planning cards as implementation.
- Kanban `done` sync for implementation completion.

### 6.3 Level 2: Handoff Enabled

Purpose: allow properly planned work to become implementation candidates.

Required conditions:

- Definition of Ready exists.
- Roadmap priority order exists.
- Product Vision and Epic Purpose are aligned.
- Handoff template exists.

Allowed:

- Create an Implementation card after Planning handoff.
- Attach scope, non-goals, dependencies, mode, and verification expectations to the implementation work.

Prohibited:

- Directly treating a Planning card as implementation work.
- Creating implementation work without the handoff fields.

### 6.4 Level 3: Implementation Routing Enabled

Purpose: allow bounded worker execution after planning controls are in place.

Required conditions:

- Mode is explicitly specified.
- High-risk approval conditions are defined.
- Done evidence rules exist.
- Worker execution is limited to approved scope.

Allowed:

- Limited worker execution for approved Implementation cards.
- Verification according to the card mode.
- Later Kanban sync only after artifact / Git / push reality is verified.

Prohibited:

- Broad implementation from planning-level cards.
- Implicit push.
- PR creation without explicit authorization.
- Kanban state changes that are not backed by evidence.

---

## 7. Kanban Relationship

Kanban is the work queue. Planning defines when items in that queue may become executable.

The following rules are required:

1. **`[Backlog]` is never auto-run.**
   - Backlog means inventory, not execution authorization.

2. **`[Planning]` is limited to read-only / design-only work.**
   - Planning cards may clarify direction and boundaries.
   - They must not become implementation tasks by status movement alone.

3. **Planning cards must not implement.**
   - Implementation requires a separate Implementation card after handoff.

4. **Implementation cards are created separately after Planning handoff.**
   - A Planning card can produce the context for implementation.
   - It should not itself become the implementation container.

5. **`done` must match artifact / commit / push reality.**
   - Kanban state alone does not prove a document exists.
   - Kanban state alone does not prove tests passed.
   - Kanban state alone does not prove a commit or push happened.

6. **Kanban `done` sync is a separate `kanban-sync-only` step.**
   - Sync should happen only after the stated evidence is verified.
   - Sync should target only the explicitly named card.

---

## 8. Meaning of Done and Ready

Planning and Implementation use related but different state meanings.

### 8.1 Planning Done

Planning is done when:

- design direction is clear
- boundaries are documented
- ready conditions are defined
- dependencies are understood
- the next artifact or implementation handoff is known

Planning done does **not** mean implementation is complete.

### 8.2 Implementation Ready

Implementation is ready when:

- handoff conditions are satisfied
- scope and non-goals are explicit
- target files or target surfaces are known
- mode is specified
- verification expectations are defined
- required approvals are clear

Implementation ready does **not** mean implementation has started.

### 8.3 Implementation Done

Implementation is done when:

- implementation or documentation work is complete
- relevant checks or tests have been run or their blockers are reported
- required commits exist when the mode includes commit
- required push exists only when the mode includes push
- Kanban sync is completed only after evidence exists

Implementation done must be grounded in artifact, test, commit, push, and Kanban reality as applicable.

---

## 9. Recommended Planning Strengthening Order

The recommended sequence is:

```text
E → A → D → C → B
```

Meaning:

1. **Planning System overall note**
2. **Product Vision v1**
3. **Definition of Ready v1**
4. **Roadmap v1**
5. **Planning Gate Policy v1**

Reason:

- The Planning System note fixes the whole map first.
- Product Vision then defines the product north star.
- Definition of Ready defines handoff quality.
- Roadmap defines priority order.
- Planning Gate Policy defines when the gate may open or remain closed.

This order is safer than opening the gate first because it prevents automation from moving ahead before meaning, handoff, and sequencing are defined.

---

## 10. Non-goals

This note does not do any of the following:

- code implementation
- dispatcher changes
- Kanban state changes
- Planning Gate release
- Product Vision creation
- Roadmap creation
- Definition of Ready creation
- gateway changes
- API changes
- CLI changes
- memory updates
- Human Model updates
- Research work

---

## 11. Prohibited Actions for This Scope

For this Planning System documentation scope, the following actions are prohibited unless a later task explicitly authorizes them:

- code implementation
- editing files outside the explicitly requested documentation target
- `git push`
- PR creation
- Kanban changes
- card creation
- Planning Gate changes
- dispatcher changes
- gateway/API/CLI changes
- memory changes
- Human Model changes
- Research
- upstream operations

---

## 12. Summary

Hermes Planning System exists to keep the product direction, execution boundaries, and automation rules aligned.

Its core job is to ensure that Hermes does not start building merely because a card exists or because automation can run.

Planning must first answer:

- What are we building?
- Why are we building it?
- What depends on what?
- What must be true before Implementation starts?
- What must automation never do without explicit approval?

Only after those answers are stable should Implementation cards become executable.
