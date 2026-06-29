# Hermes Roadmap v1

## 1. Purpose

Hermes Roadmap v1 defines the order in which the Hermes Product Vision should become real.

It is not a task list. It is a Planning artifact that fixes the priority order, phase boundaries, and dependency relationships between Epics so that implementation work does not start before the required product, safety, and planning foundations exist.

The roadmap connects:

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

This document does not implement code, change runtime behavior, mutate memory, update the Human Model, expose gateway/API/CLI surfaces, change Kanban state, or open the Planning Gate.

---

## 2. Roadmap Principles

Hermes Roadmap v1 follows these principles.

### 2.1 Human Agency First

Hermes exists to strengthen the user's agency, not replace it. Roadmap order must prioritize systems that preserve final human decision ownership before systems that automate or externally expose behavior.

### 2.2 Safety before automation

Automation should be introduced only after safety boundaries are clear. Small, bounded, inspectable steps come before broad execution, dispatcher expansion, memory mutation, or external exposure.

### 2.3 Planning before implementation

Implementation work must be preceded by Planning artifacts that define purpose, scope, dependencies, risks, mode, success criteria, and stop conditions. Definition of Ready must be satisfied before a Story becomes executable.

### 2.4 Internal before external

Internal interfaces, runtime paths, and evidence boundaries should be stabilized before gateway/API/CLI exposure. External surfaces have larger blast radius and require schema, auth, redaction, and logging design first.

### 2.5 Read-only before mutation

Context providers and memory-backed systems should begin as read-only. Mutation paths require separate design, approval, provenance, rollback, and safety controls.

### 2.6 Quality before scale

Quality, reviewability, judge/rubric behavior, metrics, and bounded logging should exist before Hermes scales into broader automation or external use.

### 2.7 Explicit approval before high-risk expansion

High-risk areas require human approval before expansion. This includes gateway/API/CLI publication, memory read/write changes, Human Model mutation, prompt injection paths, decision-framework suppression behavior, auth/security/logging/redaction, and upstream operations.

---

## 3. Current Baseline

The current baseline is:

- Philosophy docs exist.
- Human Model foundations exist.
- Decision Framework core and internal runtime work has progressed significantly.
- The Internal Decision Support path is substantially advanced.
- `HumanModelSnapshotProvider` is implemented.
- Hermes Product Vision v1 exists.
- Hermes Planning System Note v1 exists.
- Definition of Ready v1 exists.
- Gateway/API/CLI publication is not yet opened as an external surface.
- Memory-backed automatic Human Model snapshot is not yet enabled.
- Domain Model is not yet implemented as a product/runtime layer.
- Decision Style is not yet implemented as a product/runtime layer.
- Quality Framework is not yet implemented as a bounded product/runtime layer.

This baseline means Hermes has enough internal foundation to continue Planning, but it should not jump directly to external exposure or mutation-heavy automation.

---

## 4. Roadmap Phases

### Phase 0: Philosophy and Planning Foundation

Purpose: establish the durable meaning, product direction, and planning controls before more implementation work is authorized.

Includes:

- Philosophy docs.
- Product Vision.
- Planning System.
- Definition of Ready.
- Roadmap.
- Planning Gate Policy.

Exit direction:

- The product north star is documented.
- Planning artifacts are connected.
- Implementation readiness can be judged per Story.
- Planning Gate behavior is defined separately from individual Story readiness.

### Phase 1: Decision Support Core

Purpose: build the internal Decision Support path while keeping it bounded, internal, and reviewable.

Includes:

- Decision Framework interface.
- Decision Framework runtime.
- Decision Framework adapter.
- Context formatter.
- Conversation-loop injection guard.
- `conversation_loop` injection path.
- `AIAgent` forwarder.
- Internal decision-support caller.
- `HumanModelSnapshotProvider`.

Exit direction:

- Hermes can assemble bounded decision-support context internally.
- The internal caller can use Decision Framework outputs without claiming final user decisions.
- Human Model snapshot access remains controlled and explainable.

### Phase 2: Memory-backed Context

Purpose: connect durable user context safely without creating uncontrolled memory mutation or hidden profile rewriting.

Includes:

- Memory-backed Human Model snapshot provider.
- Read-only memory boundaries.
- No mutation by default.
- Snapshot provenance.

Exit direction:

- Memory-backed context can be read with clear provenance.
- Mutation remains disabled unless separately approved.
- The system can explain where Human Model context came from.

### Phase 3: Domain and Decision Style

Purpose: add specialized domain context and soft decision-style hints without mixing them into the Human Model or overriding user agency.

Includes:

- Domain Model interface.
- Domain context integration.
- Decision Style interface.
- Decision Style context integration.
- Soft hints only.

Exit direction:

- Domain Model is separate from Human Model.
- Decision Style is a hint, not a policy or instruction to decide for the user.
- Domain and style context can support better answers without rewriting identity or final judgment.

### Phase 4: Quality Framework

Purpose: make Hermes outputs and processes reviewable before scale or external exposure.

Includes:

- Judge design.
- Rubric design.
- Metrics design.
- Deterministic evaluator first.
- Bounded logging.
- Inject suppress rules only with approval.

Exit direction:

- Quality checks are bounded and explainable.
- Metrics are recorded without uncontrolled surveillance or mutation.
- Any quality-judge behavior that suppresses context injection has explicit approval and clear rules.

### Phase 5: External Surface

Purpose: expose Hermes through gateway/API/CLI only after internal behavior, quality boundaries, and security design are ready.

Includes:

- External schema design.
- Gateway/API exposure.
- CLI exposure.
- Auth boundaries.
- Redaction boundaries.
- Logging boundaries.

Exit direction:

- External inputs and outputs have stable schemas.
- Sensitive data handling is designed before exposure.
- Auth, redaction, and logging behavior is explicit and testable.

### Phase 6: E2E Acceptance and Continuous Evolution

Purpose: prove the product flow end-to-end and create a sustainable improvement loop.

Includes:

- E2E tests.
- Epic close notes.
- Review dashboard.
- Improvement backlog.
- Continuous evolution loop.

Exit direction:

- Major product paths have acceptance evidence.
- Epic closure is backed by artifact, commit, push, test, and review reality.
- Improvements feed a backlog without automatically becoming permanent rules or runtime changes.

---

## 5. Priority Order

Recommended near-to-mid-term order:

1. **Planning Gate Policy v1**
   - Define when the Planning Gate is closed, when it can open, and what automation must not do while it is closed.

2. **Complete Story 3.20 / 3.22 sync if needed**
   - Reconcile any remaining artifact, commit, push, or Kanban reality mismatch before building on top of those Stories.

3. **Memory-backed Human Model snapshot safety**
   - Design and verify read-only memory-backed snapshots, provenance, and no-mutation defaults.

4. **Domain Model interface**
   - Define the specialized-domain context boundary separately from Human Model.

5. **Decision Style interface**
   - Define soft decision-style hints without making them policy or final decision logic.

6. **Quality Framework design**
   - Define judge, rubric, metrics, deterministic evaluator boundaries, bounded logging, and approval rules.

7. **External schema design**
   - Design gateway/API/CLI schemas before publishing external surfaces.

8. **Gateway/API exposure**
   - Open external gateway/API paths only after schema, auth, redaction, logging, and quality boundaries exist.

9. **CLI exposure**
   - Expose CLI behavior only after command contract, safety boundaries, and output handling are defined.

10. **E2E acceptance**
    - Prove the full flow from product intent to implementation output and review evidence.

11. **Epic close / architecture review**
    - Close Epics only when artifact, Git, push, tests, review, and known gaps are aligned.

Already-completed items in this list may be treated as baseline evidence, but later Stories must still satisfy Definition of Ready before implementation.

---

## 6. Dependency Rules

The following dependency rules govern roadmap execution:

1. **External Surface comes after Quality Framework design**
   - Gateway/API/CLI exposure must not move ahead of quality, schema, auth, redaction, and logging design.

2. **Memory mutation comes after read-only provider safety**
   - Memory-backed context must first work as read-only with provenance. Mutation requires separate design and explicit approval.

3. **Domain Model must not be mixed into Human Model**
   - Domain Model may use Human Model context, but it must not redefine identity, values, or general user profile structure.

4. **Decision Style is a soft hint, not policy**
   - Decision Style may adapt framing or support style, but it must not decide, enforce, or override user judgment.

5. **Gateway/API/CLI publication requires schema, redaction, auth, and logging design first**
   - External interfaces need clear contracts and safety boundaries before exposure.

6. **Quality judge inject-suppress behavior requires human approval**
   - A judge or quality layer must not silently suppress context injection unless the behavior has been explicitly approved and documented.

7. **Implementation requires Definition of Ready**
   - Implementation cards and Stories must satisfy Definition of Ready before being marked ready or handed to workers.

8. **Planning Gate and Story readiness are separate controls**
   - Planning Gate may block broad implementation even when a single Story appears ready. Story readiness does not automatically open the Gate.

9. **Kanban state is not artifact reality**
   - `done`, `ready`, or `running` status cannot replace proof from docs, diffs, commits, pushes, tests, and review evidence.

---

## 7. Near-term Next Steps

Near-term Planning and Story candidates:

1. **Planning Gate Policy v1**
   - Define closed/open conditions, dispatcher behavior while closed, and required evidence for gate changes.

2. **Story 3.23 Domain Model Interface Design docs**
   - Define domain context boundaries and separation from Human Model.

3. **Story 3.25 Decision Style Interface Design docs**
   - Define decision-style hints, allowed usage, and non-policy constraints.

4. **Story 3.27 Quality Framework / Judge / Metrics Design docs**
   - Define deterministic evaluation, judge/rubric contracts, bounded metrics, and approval requirements for suppress behavior.

5. **Dispatcher `[Backlog]` never auto-run guard design**
   - Define how dispatcher should prevent inventory cards from becoming executable without explicit transition.

6. **Roadmap-based Backlog cleanup**
   - Reclassify or defer backlog items according to roadmap phase and dependencies.

These are candidates, not automatic authorizations. Each one still needs an explicit mode, Definition of Ready check, target files, allowed actions, forbidden actions, and success criteria before implementation.

---

## 8. Relationship to Planning Gate

Roadmap v1 is a Planning artifact. It helps decide which Epics and Stories should come next, but it does not open the Planning Gate by itself.

Planning Gate Policy v1 should define:

- when the Gate is closed;
- what work is allowed while closed;
- who or what can propose opening it;
- what evidence is required before Implementation cards become ready;
- how dispatcher automation must behave while the Gate is closed.

Until the Planning Gate is open for a given workstream, Implementation cards should not be marked ready only because they appear on this roadmap.

After the Gate opens, Definition of Ready remains the Story-level check before a worker can implement.

---

## 9. Non-goals

Roadmap v1 does not:

- Fully freeze the implementation order forever.
- Open gateway/API/CLI surfaces.
- Enable memory writes.
- Allow Human Model mutation.
- Implement Domain Model.
- Implement Decision Style.
- Implement Quality Framework.
- Change dispatcher behavior.
- Create or update Kanban cards.
- Open or close the Planning Gate.
- Authorize high-risk work without explicit human approval.

Roadmap v1 is a sequencing and dependency artifact. It guides Planning; it is not runtime implementation.
