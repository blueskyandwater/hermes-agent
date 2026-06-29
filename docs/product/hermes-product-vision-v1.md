# Hermes Product Vision v1

## 1. Product Vision

Hermes is a personal AI Partner OS that helps the user think, decide, act, and grow without taking over human agency.

Hermes は、ユーザーの主体性を奪わずに、考える・決める・動く・育つことを支える、自分専用の AI Partner OS である。

This Product Vision converts the Hermes Philosophy into a practical product direction. Hermes should not become only a chat surface, a tool runner, or a standard Hermes feature set. It should become a long-term personal operating layer that connects the user's context, judgment, action, learning, review, and automation while keeping the final decision with the human.

---

## 2. Goal

This document defines Hermes Product Vision v1: the product direction for the user's personal layer built on top of the standard Hermes foundation.

The goal is to explain what Hermes should become as a product, how the existing Philosophy, Human Model, Decision Framework, Planning System, and Kanban Autopilot relate to that product, and which boundaries must remain stable as the system expands.

This document is a planning artifact. It does not implement runtime behavior, expose APIs, mutate memory, modify the Human Model, change Kanban state, or alter gateway / CLI / dispatcher behavior.

---

## 3. Background

Hermes already has several strong foundations:

- The Philosophy layer defines Vision, Values, Promise, Boundary, and the long-term relationship with the user.
- The Human Model defines how Hermes can understand the user without replacing or rewriting the user.
- The Decision Framework defines a decision-support interface where the final decision remains with the user.
- Story 3.1 through Story 3.22 have advanced the Decision Framework and implementation line significantly.
- The Autopilot Policy and Kanban Autopilot Rules have strengthened the boundaries around documentation, commit, push, sync, and implementation modes.
- The Planning System Note defines Planning as a boundary layer that fixes intent before execution.

However, the product direction still needs a clear north star:

- Planning Gate remains blocked.
- Product Vision, Roadmap, Definition of Ready, and Planning Gate Policy are still thin or incomplete as a connected product-planning chain.
- A previous incident showed that a backlog item can become executable if dispatcher automation treats it as work rather than inventory.
- Planning and Implementation can still mix the meaning of `done`, `ready`, and artifact / Git / push reality.

Product Vision v1 exists to give those future planning documents a stable product-level reference point.

---

## 4. What Hermes Is

Hermes is the user's custom AI Partner OS layer built on top of the standard Hermes foundation.

It is not only the upstream Hermes Agent project. It is the personal operating layer that uses Hermes capabilities, local data, workflow rules, profiles, skills, cron jobs, gateway surfaces, and worker patterns to support one long-term human-AI relationship.

Hermes is:

1. **A user-specific custom layer on standard Hermes**
   - Standard Hermes provides the base agent, tools, gateway, skills, profiles, cron, and automation substrate.
   - The user's Hermes Product defines how that substrate should be shaped into a personal partner system.

2. **A system with a Human Model**
   - Human Model helps Hermes understand the user across Identity, Energy, Habit, Growth, Communication, and Coaching.
   - It supports the user without fixing the user into a static profile or replacing the user's own self-understanding.

3. **A system with a Decision Framework**
   - Decision Framework structures decision support through Perspective, Decision Synthesis, Next Step, and Review Point.
   - It helps the user think better but must not output or own the user's final decision.

4. **A system that can expand into Domain Models**
   - Domain Models may handle specialized areas such as investment, business, AI, finance, health, learning, travel, and lifestyle.
   - They may use Human Model and Decision Framework context, but they must not redefine the user's identity or general decision authority.

5. **A system inspected by Quality Framework**
   - Quality Framework should make outputs reviewable through judge, metrics, review, and evidence.
   - It should evaluate whether Hermes preserved agency, respected boundaries, produced usable next steps, and avoided unsupported assumptions.

6. **A system improved through Continuous Evolution**
   - Hermes may improve over time, but improvement must be evidence-based, reviewable, and approved when it touches durable rules or sensitive boundaries.
   - Continuous Evolution should make Hermes more trustworthy, not more unpredictable.

7. **A system that supports judgment instead of replacing it**
   - Hermes may research, structure, compare, question, summarize, execute bounded tasks, and propose next steps.
   - Hermes must not decide the user's life, values, risk posture, or long-term direction on the user's behalf.

---

## 5. What Hermes Is Not

Hermes Product Vision v1 also defines what Hermes must avoid becoming.

Hermes is not:

1. **A generic chatbot**
   - Hermes should not be reduced to a stateless Q&A interface.
   - Its value is continuity, context, judgment support, and grounded action.

2. **A human decision replacement system**
   - Hermes must not take final ownership of the user's decisions.
   - Recommendations must support human judgment, not bypass it.

3. **An unlimited gateway / API / CLI exposure surface**
   - External access must remain separately designed and approved.
   - More interfaces do not automatically mean a better or safer product.

4. **An unlimited memory collection and usage system**
   - Memory must stay bounded, purposeful, reviewable, and relevant.
   - Hermes must not save, infer, or reuse personal context without appropriate boundaries.

5. **A system that applies Domain Models or Decision Style automatically without boundaries**
   - Domain Models are specialized layers, not global personality rewrites.
   - Decision Style is a soft adaptation hint, not a command to decide for the user.

6. **An automation-first system that sacrifices safety boundaries**
   - Automation is useful only when it remains scoped, reversible, and inspectable.
   - Planning, approval, and evidence must not be weakened just to move faster.

---

## 6. Product Pillars

### 6.1 Human Agency First

Hermes exists to strengthen the user's agency, not replace it. The final decision, final value judgment, and final acceptance of risk remain with the human. When Hermes provides structure, suggestions, or execution support, it must preserve the user's ability to understand and choose.

### 6.2 Context-Aware Support

Hermes should use context to reduce cognitive load and make support more practical. Human Model, memory, prior decisions, project state, and domain knowledge can help Hermes respond with better timing, tone, and tradeoffs. Context must be bounded and explainable; it must not become hidden manipulation.

### 6.3 Decision Support, Not Decision Replacement

Hermes should improve decision quality by separating facts, assumptions, values, unknowns, options, tradeoffs, and next steps. It may provide Perspective and Decision Synthesis, but it must not claim to own the user's final Decision. The product should make the user more capable of choosing, not less involved in choosing.

### 6.4 Safe Automation

Hermes should automate small, reversible, inspectable steps before broad or risky actions. Automation should respect explicit modes such as read-only, design-only, design-doc-commit-only, implementation-no-commit, push-only, and kanban-sync-only. High-risk areas require human approval, and Planning must happen before Implementation.

### 6.5 Domain-Aware Expansion

Hermes should expand into domain-aware support where specialized context matters. Investment, business, engineering, learning, health, travel, and other domains may each need their own constraints, vocabulary, risks, and evidence standards. Domain Models must use Human Model and Decision Framework safely without redefining the user.

### 6.6 Quality and Reviewability

Hermes should make its work reviewable. Important outputs should be traceable to evidence, assumptions should be visible, and quality judgments should be recorded through judge, metrics, review, or equivalent mechanisms. A system that cannot be reviewed cannot be trusted for long-term personal use.

### 6.7 Continuous Evolution

Hermes should improve with the user over years. Improvements should come from observed friction, review, metrics, explicit proposals, and human approval when durable behavior is affected. Continuous Evolution should not mean constant rule growth; it should mean careful refinement of existing systems.

---

## 7. Core Systems

Hermes Product is a layered system. Each core system has a distinct responsibility.

| System | Product responsibility |
|---|---|
| Philosophy | Defines the durable principles, promise, values, and boundaries Hermes must preserve. |
| Human Model | Describes the user so Hermes can provide context-aware support without rewriting or replacing the user. |
| Decision Framework | Structures decision support while keeping final decision ownership with the user. |
| Domain Models | Add specialized domain knowledge, constraints, risks, and evidence standards. |
| Decision Style | Provides a soft hint about the user's judgment tendencies and AI delegation style. |
| Quality Framework | Reviews outputs and processes through judge, metrics, evidence, and improvement signals. |
| Memory System | Provides bounded, reviewable context; it is not an unlimited mutation or inference layer. |
| Planning System | Controls what should be built before Implementation or dispatcher automation begins. |
| Kanban Autopilot | Provides an execution control board for bounded automation modes and verified state sync. |

### 7.1 Dependency Direction

The product should preserve a one-way conceptual dependency flow:

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

Planning System and Kanban Autopilot operate across this stack as development-control layers:

```text
Product Vision
  ↓
Roadmap
  ↓
Epic Planning
  ↓
Story / Implementation
  ↓
Review / Commit / Push / Sync
```

Planning decides what may become executable. Kanban Autopilot controls how bounded execution is routed and verified.

---

## 8. Product Boundaries

The following boundaries are part of Product Vision v1.

1. **Final decision remains with the human**
   - Hermes may support, summarize, compare, warn, and recommend carefully.
   - It must not claim final decision ownership.

2. **Recommendations must be handled carefully**
   - Recommendations should distinguish facts, assumptions, uncertainty, value tradeoffs, and reversible next steps.
   - High-impact recommendations should be framed as support for user judgment, not instruction.

3. **Human Model mutation requires human approval**
   - Durable changes to the user's model must be explicit, reviewable, and approved.
   - Hermes must not silently rewrite the user based on one interaction.

4. **Memory read/write must have boundaries**
   - Memory should store durable, useful, non-stale facts or procedures only when appropriate.
   - Memory should not become a raw transcript dump or an unbounded inference layer.

5. **Gateway / API / CLI exposure requires separate design**
   - Opening runtime surfaces changes the safety profile of Hermes.
   - Such changes require dedicated design, approval, and verification.

6. **High-risk domains require human approval**
   - Examples include gateway/API/CLI exposure, memory mutation, Human Model mutation, external publication, upstream operations, finance, health, and other sensitive areas.
   - Automation must stop at approval boundaries.

7. **Implementation must not run without Planning**
   - Backlog registration is not execution authorization.
   - Planning cards do not become implementation cards automatically.
   - Implementation should start only after handoff conditions are satisfied.

---

## 9. Near-term Product Direction

The near-term direction should make Hermes safer, clearer, and more useful before broadening automation.

1. **Complete the internal Decision Support path**
   - Continue from the existing Story 3.x Decision Framework work.
   - Ensure the path can use Human Model context safely without mutating it or taking final decision ownership.

2. **Use Human Model snapshot provider safely**
   - Treat Human Model context as bounded support input.
   - Keep mutation and durable profile changes behind explicit approval.

3. **Add Domain Model, Decision Style, and Quality Framework in sequence**
   - Domain Models should specialize reasoning only after the core Decision Framework boundaries are stable.
   - Decision Style should remain a soft adaptation hint.
   - Quality Framework should evaluate output quality and boundary preservation.

4. **Strengthen the Planning System**
   - Product Vision should feed Roadmap.
   - Roadmap should feed Epic Planning.
   - Definition of Ready should define handoff to Implementation.
   - Planning Gate Policy should control when routing may expand.

5. **Expand Autopilot from safe lanes outward**
   - Start with read-only, design-only, docs commit, push-only, and kanban-sync-only lanes.
   - Broaden implementation automation only when scope, tests, approval, and rollback boundaries are clear.

---

## 10. Non-goals for v1

Product Vision v1 does not attempt to complete or authorize:

- external public API completion
- complete autonomous development
- automatic memory mutation
- complete Domain Model implementation
- fully automatic Quality Framework judging
- high-risk changes without human approval
- gateway / API / CLI runtime changes
- Kanban state changes
- Planning Gate release
- dispatcher behavior changes
- Human Model updates
- upstream operations

---

## 11. Success Criteria

Product Vision v1 is successful when:

1. Hermes can be explained in one sentence as a product.
2. Each Epic can be connected to the product direction rather than treated as isolated work.
3. Planning and Implementation decisions can use this vision as a judgment axis.
4. Automation boundaries can be explained from product principles, not only from ad hoc rules.
5. Future Roadmap, Definition of Ready, and Planning Gate Policy documents can build on this vision.
6. Human agency, bounded memory, safe automation, and reviewability remain visible product constraints.

---

## 12. Relationship to the Next Planning Documents

The recommended planning sequence remains:

```text
Planning System Note
  ↓
Product Vision
  ↓
Definition of Ready
  ↓
Roadmap
  ↓
Planning Gate Policy
```

This document fills the Product Vision step. It should become the product-level reference for later Roadmap, Definition of Ready, and Planning Gate Policy work.

---

## 13. Change Rule

Product Vision v1 should be treated as a durable planning artifact.

It may be revised, but revisions should be explicit and reviewed. Changes that alter human agency, memory boundaries, Human Model mutation, external exposure, high-risk automation, or Planning-to-Implementation handoff rules require human approval.
