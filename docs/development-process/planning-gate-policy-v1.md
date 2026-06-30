# Planning Gate Policy v1

## 1. Purpose

Planning Gate is the boundary that protects whether Planning artifacts are good enough to hand off toward Implementation.

It is not implementation approval by itself. It is a control layer that decides whether work may move from Planning into implementation-ready routing, card creation, or dispatcher execution.

The policy exists to prevent:

- Implementation from starting before product intent, scope, risks, and verification are clear.
- Dispatcher automation from treating unplanned backlog inventory as executable work.
- Planning cards from becoming implementation cards by accident.
- Kanban `done`, Git state, artifact existence, commit state, and push state from being mixed together.
- High-risk areas from expanding without explicit human approval.

This document is a Planning artifact. It does not open the Planning Gate, change Kanban state, modify dispatcher behavior, create implementation cards, change runtime behavior, expose gateway/API/CLI surfaces, mutate memory, or update the Human Model.

---

## 2. Gate Levels

Planning Gate has four levels. A higher level may be used only when its conditions are satisfied and no close / stop condition is active.

### Level 0: fully blocked

Meaning:

- The Planning Gate is closed.
- Work may be recorded as inventory, but not executed.
- Dispatcher execution is forbidden.

Allowed:

- Backlog registration only.
- Read-only review of existing docs, cards, logs, or Git state when explicitly requested.
- Human discussion about intent, priority, and risks.

Forbidden:

- Implementation cards.
- Worker auto-run.
- Dispatcher promotion.
- Runtime changes.
- Git commits unless a separate docs-only mode is explicitly authorized.
- Kanban `ready`, `running`, or `done` transitions caused by automation.

### Level 1: planning active

Meaning:

- Planning work may proceed, but only as planning.
- Planning cards remain read-only / design-only unless a narrow docs-only commit mode is explicitly requested.
- Implementation card creation is still forbidden.

Allowed:

- Product, roadmap, policy, design-note, and handoff draft work.
- Read-only repository, document, and Git inspection.
- Design-only docs proposals.
- Local docs-only commits when the task mode explicitly allows them, such as `design-doc-commit-only`.

Forbidden:

- Implementation card creation.
- Runtime connection.
- Dispatcher auto-run.
- Gateway/API/CLI exposure.
- Memory writes.
- Human Model mutation.
- Treating a Planning artifact as implementation completion.

### Level 2: handoff enabled

Meaning:

- Planning can create bounded implementation handoffs when the required planning artifacts exist.
- Implementation cards may be created as separate cards after readiness is proven.
- Auto-run remains limited.

Required baseline:

- Product Vision exists.
- Roadmap exists.
- Definition of Ready exists.
- Implementation handoff template or equivalent handoff fields exist.
- Planning and Implementation cards are separated.

Allowed:

- Creating an Implementation card from a Planning result that satisfies Definition of Ready.
- Identifying mode, target files / surfaces, success criteria, risks, verification, and stop conditions.
- Preparing dispatcher-safe instructions without starting dispatcher execution automatically.

Forbidden:

- Auto-running implementation by default.
- Mixing Planning card `done` with Implementation card `done`.
- High-risk implementation without explicit human approval.
- External surface, memory, or Human Model expansion without separate approval.

### Level 3: implementation routing enabled

Meaning:

- Worker execution may be allowed for bounded, ready implementation work.
- Routing is allowed only under explicit mode, risk, and evidence constraints.

Required baseline:

- Mode is specified.
- High-risk approval conditions are defined.
- Done evidence rules are defined.
- Artifact / commit / push / Kanban state relationships are explicit.
- Worker execution is limited to the approved scope.

Allowed:

- Limited worker execution for cards that satisfy Definition of Ready.
- Mode-specific routing such as `implementation-no-commit`, `implementation-review-commit`, `push-only`, or `kanban-sync-only`.
- Verification and evidence collection required by the Story.

Forbidden:

- Worker execution for `[Backlog]` inventory.
- Running mode-unspecified cards.
- Auto-expanding into high-risk surfaces.
- Marking work complete without artifact, Git, test, review, and push evidence as applicable.
- Planning Gate changes without human approval.

---

## 3. Open Conditions

The Planning Gate may advance to a higher level only when the relevant conditions below are true.

General open conditions:

- Product Vision exists.
- Roadmap exists.
- Definition of Ready exists.
- High-risk approval conditions are documented.
- Autopilot mode and prefix rules exist.
- The relationship between `done`, artifact existence, commit state, and push state is defined.
- Implementation handoff conditions exist.
- Planning cards and Implementation cards are separated.

Level-specific open conditions:

| Target level | Required conditions |
|---|---|
| Level 1 | A planning task is explicitly requested and scoped as read-only, design-only, or docs-only. |
| Level 2 | Product Vision, Roadmap, Definition of Ready, and handoff fields are available, and the Planning result can be evaluated for readiness. |
| Level 3 | A separate Implementation card or equivalent task has passed Definition of Ready, has an explicit mode, has verification steps, and has risk approval when needed. |

Open does not mean unrestricted execution. Even when Level 3 is available, each Story must still satisfy Definition of Ready and must obey its mode-specific permissions.

---

## 4. Close / Stop Conditions

If any condition below is observed, the Planning Gate must close or the current progression must stop until the mismatch is reviewed.

Close / stop conditions:

- A `[Backlog]` card becomes `ready` or `running`.
- A Planning card begins implementation work.
- A mode-unspecified card is executed.
- A high-risk area is touched without explicit human approval.
- `done` state and actual evidence do not match.
- Git status is unknown.
- Push target is unknown.
- External schema work appears without approval.
- Gateway/API/CLI exposure appears without approval.
- Memory read/write expansion appears without approval.
- Human Model mutation appears without approval.
- Runtime changes appear in a design-only or docs-only mode.
- Dispatcher behavior changes without explicit approval.
- `git add .`, broad staging, upstream push, or PR creation appears in a scope that forbids it.

Required response when a stop condition appears:

1. Stop the current action.
2. Preserve the current worktree and artifact state unless rollback was explicitly authorized.
3. Report the exact observed mismatch.
4. Separate confirmed facts from assumptions.
5. Ask for or wait for human approval before reopening the gate or continuing.

---

## 5. Kanban Rules

Planning Gate Policy uses the following Kanban rules.

### 5.1 Prefix and lane rules

- `[Backlog]` is never auto-run.
- `[Backlog]` means inventory, not executable work.
- `[Planning]` is read-only / design-only by default.
- `[Planning]` may produce docs, design notes, handoff drafts, or readiness analysis.
- `[Planning]` must not perform implementation work.
- `[Implementation]` is created only after Definition of Ready is satisfied.
- `[Implementation]` must be a separate card or separately authorized implementation task.
- `[High-Risk]` requires explicit human approval before execution.

### 5.2 Done and sync rules

- Planning done and Implementation done are different states.
- Planning done means the planning artifact or handoff exists.
- Implementation done requires the implementation artifact, verification, Git state, commit / push state, and review evidence required by the Story.
- Kanban `done` alone is not proof that work is complete.
- Done synchronization is `kanban-sync-only`.
- `kanban-sync-only` records already-verified artifact / Git / push reality; it must not create implementation scope.
- Done sync must not be used to retroactively justify unverified implementation.

### 5.3 Gate mutation rules

- Planning Gate changes require human approval.
- Dispatcher rules must not auto-open the Planning Gate.
- Worker success must not auto-open the Planning Gate.
- A Roadmap or DoR document existing does not automatically authorize implementation routing.

---

## 6. Relationship to DoR and Roadmap

Planning Gate Policy, Roadmap, and Definition of Ready have different responsibilities.

| Artifact | Responsibility |
|---|---|
| Roadmap | Defines priority order, phase sequence, and Epic dependency direction. |
| Definition of Ready | Judges whether a specific Story or Implementation card is ready to start. |
| Planning Gate Policy | Controls whether the overall system may move from planning into handoff, card creation, or bounded execution. |

Rules:

- Roadmap decides what should come next.
- Definition of Ready decides whether a Story is ready.
- Planning Gate decides whether the system is allowed to move work across the Planning / Implementation boundary.
- Even if the Gate is open, each Story must still satisfy Definition of Ready.
- Even if a Story satisfies Definition of Ready, high-risk actions still require explicit human approval.
- Even if implementation is complete, Kanban sync must follow evidence rather than create evidence.

The intended flow is:

```text
Product Vision
  ↓
Roadmap
  ↓
Planning Gate Policy
  ↓
Planning artifact / handoff
  ↓
Definition of Ready check
  ↓
Implementation card or bounded execution mode
  ↓
Evidence-backed completion and optional kanban-sync-only
```

---

## 7. Non-goals

Planning Gate Policy v1 does not do any of the following:

- It does not actually open or unblock the Planning Gate.
- It does not change Kanban dispatcher implementation.
- It does not create Implementation cards.
- It does not change gateway/API/CLI exposure.
- It does not enable memory writes.
- It does not permit Human Model mutation.
- It does not change runtime behavior.
- It does not change `run_agent.py`, `prompt_builder.py`, `conversation_loop.py`, dispatcher code, or worker routing.
- It does not define a full external schema.
- It does not approve high-risk work.

---

## 8. Near-term Use

Near-term work should use this policy as a gate check before expanding automation.

Recommended next planning candidates:

1. Story 3.23 Domain Model Interface Design docs.
2. Story 3.25 Decision Style Interface Design docs.
3. Story 3.27 Quality Framework / Judge / Metrics Design docs.
4. Dispatcher `[Backlog]` never auto-run guard design.
5. Roadmap-based Backlog cleanup.

Before any of those become implementation work, the handoff should state:

- Which Roadmap phase it belongs to.
- Which Gate level is required.
- Whether the work is planning-only, implementation, push-only, or kanban-sync-only.
- Whether high-risk approval is required.
- Which artifacts, files, tests, commits, pushes, or Kanban sync steps are allowed.
- Which stop conditions apply.
