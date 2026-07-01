# Foundation Docs Index v1 Draft

Status: Draft  
Scope: Foundation support document  
Target: Hermes Agent product / governance documentation  
Mode: Documentation only  
Authorization: This index does not authorize implementation, mutation, dispatch, push, CI rerun, or governance change.

---

## 1. Purpose

Foundation Docs Index v1 is the entry point for the Hermes Foundation document set.

Its role is simple:

- show what documents exist
- explain what each document is for
- suggest what order to read them in
- show when each document should be consulted
- reduce confusion before implementation or mutation work

This index is a navigation artifact, not an approval artifact.

Core principle:

> Foundation docs guide; they do not authorize execution.

Supporting principles:

- Index is navigation, not permission
- Backlog is inventory, not authorization
- Readiness review is review, not authorization
- High-risk operations require current explicit approval
- Current user instruction wins
- Push remains weekly / push-only unless explicitly changed

This document is meant to prevent a recurring mistake:

> reading a Foundation document and treating it as if it approved action.

The index exists to make the document set easier to use without turning the document set into an automation trigger.

---

## 2. Document Inventory

The current Foundation-related documents covered by this index are:

1. `docs/product/hermes-foundation-v1.md`
2. `docs/product/foundation-pillar-map-v1.md`
3. `docs/product/planning-gate-policy-v1.md`
4. `docs/product/high-risk-operation-taxonomy-v1.md`
5. `docs/product/implementation-readiness-review-v1.md`
6. `docs/product/memory-system-v1.md`
7. `docs/product/human-model-v1.md`
8. `docs/product/decision-support-v1.md`
9. `docs/product/domain-model-v1.md`
10. `docs/product/decision-profile-v1.md`
11. `docs/product/worker-architecture-v1.md`
12. `docs/product/quality-framework-v1.md`
13. `docs/product/continuous-evolution-v1.md`
14. `docs/product/improvement-backlog-v1.md`
15. `docs/product/weekly-quality-report-v1.md`

Short inventory summary:

| Document | Primary role | What it is not |
| --- | --- | --- |
| `hermes-foundation-v1.md` | Foundation overview and governing principles | implementation approval |
| `foundation-pillar-map-v1.md` | map of responsibilities and dependencies across docs | execution trigger |
| `planning-gate-policy-v1.md` | pre-action gate and permission boundary | implementation spec |
| `high-risk-operation-taxonomy-v1.md` | shared risk classification vocabulary | approval token |
| `implementation-readiness-review-v1.md` | pre-implementation review checklist | go-order |
| `memory-system-v1.md` | durable context policy | authorization source |
| `human-model-v1.md` | user-understanding support framework | definition of the user |
| `decision-support-v1.md` | decision support structure | decision authority |
| `domain-model-v1.md` | domain evidence and domain reasoning boundaries | command source |
| `decision-profile-v1.md` | stable preference and judgment guide | hard policy |
| `worker-architecture-v1.md` | role boundaries for workers / dispatcher / human | dispatch permission |
| `quality-framework-v1.md` | behavior evaluation framework | user evaluation or permission system |
| `continuous-evolution-v1.md` | reviewed refinement flow | autonomous mutation engine |
| `improvement-backlog-v1.md` | improvement inventory | implementation queue with implied approval |
| `weekly-quality-report-v1.md` | periodic quality visibility report | governance authority |

---

## 3. Quick Start Reading Order

If someone is new to the Foundation docs, use this reading order first.

### Minimal orientation path

1. `docs/product/hermes-foundation-v1.md`
2. `docs/product/foundation-pillar-map-v1.md`
3. `docs/product/foundation-docs-index-v1.md`

Purpose of this path:

- understand the overall intent
- understand the document set shape
- understand where to go next

### Pre-implementation path

1. `docs/product/hermes-foundation-v1.md`
2. `docs/product/foundation-pillar-map-v1.md`
3. `docs/product/planning-gate-policy-v1.md`
4. `docs/product/high-risk-operation-taxonomy-v1.md`
5. `docs/product/implementation-readiness-review-v1.md`
6. `docs/product/worker-architecture-v1.md`

Purpose of this path:

- understand what Foundation is protecting
- understand what may block action
- understand risk categories
- understand what “ready” means
- understand who is allowed to do what

### Context and user-understanding path

1. `docs/product/memory-system-v1.md`
2. `docs/product/human-model-v1.md`
3. `docs/product/decision-profile-v1.md`
4. `docs/product/decision-support-v1.md`
5. `docs/product/domain-model-v1.md`

Purpose of this path:

- understand durable context boundaries
- understand user-support boundaries
- understand soft guidance vs authority
- understand evidence vs instruction

### Quality and evolution path

1. `docs/product/quality-framework-v1.md`
2. `docs/product/weekly-quality-report-v1.md`
3. `docs/product/improvement-backlog-v1.md`
4. `docs/product/continuous-evolution-v1.md`

Purpose of this path:

- understand evaluation first
- understand reporting second
- understand inventory third
- understand reviewed refinement last

Recommended rule:

> Evaluation before backlog, backlog before evolution, and none of them authorize action by themselves.

---

## 4. Docs by Purpose

### 4.1 Foundation orientation

Read these to understand the whole system shape.

- `docs/product/hermes-foundation-v1.md`
- `docs/product/foundation-pillar-map-v1.md`
- `docs/product/foundation-docs-index-v1.md`

These answer:

- what the Foundation is trying to protect
- how the docs relate to each other
- where to look next

### 4.2 Gating and risk control

Read these before acting.

- `docs/product/planning-gate-policy-v1.md`
- `docs/product/high-risk-operation-taxonomy-v1.md`
- `docs/product/implementation-readiness-review-v1.md`

These answer:

- is action even discussable right now
- what type of risk this action has
- what still needs review before implementation

### 4.3 Context and human support

Read these when the task touches long-lived context or user understanding.

- `docs/product/memory-system-v1.md`
- `docs/product/human-model-v1.md`
- `docs/product/decision-profile-v1.md`
- `docs/product/decision-support-v1.md`
- `docs/product/domain-model-v1.md`

These answer:

- what context can be kept
- what must not be overclaimed
- how to support decisions without replacing the user
- what evidence belongs to domain reasoning

### 4.4 Execution boundaries

Read these before delegation, dispatch, or mode-sensitive execution.

- `docs/product/worker-architecture-v1.md`
- `docs/product/planning-gate-policy-v1.md`
- `docs/product/high-risk-operation-taxonomy-v1.md`

These answer:

- who may act
- who may not approve
- what requires current explicit approval

### 4.5 Quality and evolution

Read these when reviewing behavior or discussing change proposals.

- `docs/product/quality-framework-v1.md`
- `docs/product/weekly-quality-report-v1.md`
- `docs/product/improvement-backlog-v1.md`
- `docs/product/continuous-evolution-v1.md`

These answer:

- how behavior is evaluated
- how issues are made visible
- where candidates are stored
- how reviewed refinement may happen later

---

## 5. Docs by Operation Type

Use the following mapping when a task starts from an operation rather than from a design question.

| Operation type | Read first | Read next | Why |
| --- | --- | --- | --- |
| implementation planning | `hermes-foundation-v1.md` | `planning-gate-policy-v1.md`, `implementation-readiness-review-v1.md` | clarify boundaries before work |
| runtime code change | `planning-gate-policy-v1.md` | `high-risk-operation-taxonomy-v1.md`, `worker-architecture-v1.md` | determine approval and blast radius |
| docs-only creation | `hermes-foundation-v1.md` | `implementation-readiness-review-v1.md` | keep scope narrow and non-authorizing |
| memory mutation | `memory-system-v1.md` | `human-model-v1.md`, `planning-gate-policy-v1.md`, `high-risk-operation-taxonomy-v1.md` | context is not permission |
| human model mutation | `human-model-v1.md` | `memory-system-v1.md`, `planning-gate-policy-v1.md`, `high-risk-operation-taxonomy-v1.md` | user support must stay bounded |
| decision profile mutation | `decision-profile-v1.md` | `decision-support-v1.md`, `planning-gate-policy-v1.md`, `high-risk-operation-taxonomy-v1.md` | soft guide must not become hard policy by accident |
| worker dispatch | `worker-architecture-v1.md` | `planning-gate-policy-v1.md`, `high-risk-operation-taxonomy-v1.md` | dispatch is not self-authorized |
| git push / PR / rerun | `high-risk-operation-taxonomy-v1.md` | `planning-gate-policy-v1.md`, `implementation-readiness-review-v1.md` | publication and side effects require current approval |
| quality review | `quality-framework-v1.md` | `weekly-quality-report-v1.md`, `improvement-backlog-v1.md` | separate evaluation from action |
| evolution proposal | `continuous-evolution-v1.md` | `quality-framework-v1.md`, `improvement-backlog-v1.md`, `weekly-quality-report-v1.md` | reviewed refinement only |
| high-risk operation | `high-risk-operation-taxonomy-v1.md` | `planning-gate-policy-v1.md`, `implementation-readiness-review-v1.md` | classify first, act later |

---

## 6. Docs to Read Before Implementation

Before implementation, the recommended minimum set is:

1. `docs/product/hermes-foundation-v1.md`
2. `docs/product/foundation-pillar-map-v1.md`
3. `docs/product/planning-gate-policy-v1.md`
4. `docs/product/high-risk-operation-taxonomy-v1.md`
5. `docs/product/implementation-readiness-review-v1.md`
6. `docs/product/worker-architecture-v1.md`

Why this set matters:

- Foundation explains intent
- Pillar Map explains relationships
- Planning Gate explains permission boundaries
- Risk Taxonomy explains blast radius
- Readiness Review explains practical review checks
- Worker Architecture explains role boundaries

Implementation should not begin from backlog presence alone.
Implementation should not begin from “it seems obvious” alone.
Implementation should not begin because a document exists.

Working rule:

> Roadmap and documentation can justify discussion order. They do not justify execution order by themselves.

---

## 7. Docs to Read Before Memory / Human Model / Decision Profile Mutation

Before mutating user-adjacent durable context, read:

1. `docs/product/memory-system-v1.md`
2. `docs/product/human-model-v1.md`
3. `docs/product/decision-profile-v1.md`
4. `docs/product/decision-support-v1.md`
5. `docs/product/domain-model-v1.md`
6. `docs/product/planning-gate-policy-v1.md`
7. `docs/product/high-risk-operation-taxonomy-v1.md`

Why this set matters:

- Memory can drift into false authority if not bounded
- Human Model can drift into identity overclaim if not bounded
- Decision Profile can drift into policy if not bounded
- Decision Support can drift into substitution if not bounded
- Domain Model can drift into command language if evidence/instruction is mixed
- Planning Gate and Risk Taxonomy remind that mutation still needs current approval

Reminder:

> Memory is context, not authorization.

Reminder:

> Human Model supports the user, not defines the user.

Reminder:

> Decision Profile is soft guide, not policy.

---

## 8. Docs to Read Before Worker Dispatch

Before dispatching a worker or relying on worker routing logic, read:

1. `docs/product/worker-architecture-v1.md`
2. `docs/product/planning-gate-policy-v1.md`
3. `docs/product/high-risk-operation-taxonomy-v1.md`
4. `docs/product/implementation-readiness-review-v1.md`

Why this set matters:

- Worker Architecture defines role boundaries
- Planning Gate prevents premature execution
- Risk Taxonomy shows when dispatch becomes high-risk
- Readiness Review helps surface unresolved blockers

Hard boundary reminders:

- worker cannot self-escalate into authority
- dispatcher cannot approve on behalf of the user
- mode does not erase approval requirements
- backlog presence does not authorize dispatch

---

## 9. Docs to Read Before Git / Push / PR / CI Rerun

Before git publication or CI-side effect operations, read:

1. `docs/product/high-risk-operation-taxonomy-v1.md`
2. `docs/product/planning-gate-policy-v1.md`
3. `docs/product/implementation-readiness-review-v1.md`
4. `docs/product/worker-architecture-v1.md`

Why this set matters:

- Git / push / PR / rerun operations can create external or durable consequences
- They often cross from local draft space into shared or visible space
- They can be mistaken as “routine” when they are actually approval-sensitive

User-specific operational note that should be respected alongside these docs:

- Push remains weekly / push-only unless explicitly changed

Operational interpretation:

- a file being ready does not mean push-approved
- a local verification pass does not mean PR-approved
- “ahead 1” does not mean “push now”
- CI rerun remains an explicit action, not a default cleanup step

---

## 10. Docs to Read Before Quality / Evolution Changes

Before changing quality criteria, evolution flow, or improvement handling, read:

1. `docs/product/quality-framework-v1.md`
2. `docs/product/weekly-quality-report-v1.md`
3. `docs/product/improvement-backlog-v1.md`
4. `docs/product/continuous-evolution-v1.md`
5. `docs/product/planning-gate-policy-v1.md`
6. `docs/product/high-risk-operation-taxonomy-v1.md`

Why this set matters:

- Quality Framework defines evaluation logic
- Weekly Report shows visibility, not authority
- Improvement Backlog stores candidates, not approval
- Continuous Evolution defines reviewed refinement, not autonomous mutation
- Gate and Taxonomy prevent silent governance change

Critical reminder:

> Quality finding is evidence, not permission.

Critical reminder:

> Improvement candidate is not authorization.

---

## 11. Docs to Read Before High-risk Operations

Before any high-risk or possibly high-risk operation, the minimum read set is:

1. `docs/product/high-risk-operation-taxonomy-v1.md`
2. `docs/product/planning-gate-policy-v1.md`
3. `docs/product/implementation-readiness-review-v1.md`
4. `docs/product/worker-architecture-v1.md`

If the operation touches a specialized area, add the area-specific doc:

- memory -> `memory-system-v1.md`
- human model -> `human-model-v1.md`
- decision profile -> `decision-profile-v1.md`
- quality -> `quality-framework-v1.md`
- evolution -> `continuous-evolution-v1.md`
- backlog -> `improvement-backlog-v1.md`

Simple rule:

> classify first, confirm scope second, verify approval third, act last.

---

## 12. Responsibility Summary Table

| Document | Main responsibility | Typical question it answers | Not allowed inference |
| --- | --- | --- | --- |
| `hermes-foundation-v1.md` | define the Foundation baseline | what is the overall operating philosophy | “therefore implement now” |
| `foundation-pillar-map-v1.md` | connect documents by role | how do the docs fit together | “this map approves action” |
| `foundation-docs-index-v1.md` | navigation entry point | what should I read first | “the index selected this, so execute it” |
| `planning-gate-policy-v1.md` | gate preconditions | is this even allowed to proceed to action discussion | “gate awareness = approval” |
| `high-risk-operation-taxonomy-v1.md` | risk vocabulary | how risky is this operation | “risk known = risk approved” |
| `implementation-readiness-review-v1.md` | readiness checklist | what is still unresolved before implementation | “ready = do it now” |
| `memory-system-v1.md` | durable memory boundary | what can be retained and mutated | “memory says so, so it is allowed” |
| `human-model-v1.md` | user-support framing | how should the user be supported | “model defines the user” |
| `decision-support-v1.md` | decision support structure | how to improve user decisions without replacing them | “decision support can decide” |
| `domain-model-v1.md` | domain evidence boundary | what evidence belongs in domain reasoning | “domain evidence is a command” |
| `decision-profile-v1.md` | stable preference guide | what soft decision tendencies matter | “profile is binding policy” |
| `worker-architecture-v1.md` | role boundary map | who may do what | “architecture implies permission” |
| `quality-framework-v1.md` | behavior evaluation | how Hermes behavior is judged | “quality score authorizes mutation” |
| `continuous-evolution-v1.md` | reviewed refinement flow | how change proposals move safely | “evolution means autonomous change” |
| `improvement-backlog-v1.md` | candidate inventory | what ideas are stored for later | “listed item should now be implemented” |
| `weekly-quality-report-v1.md` | periodic visibility | what quality trends are being observed | “report output is authorization” |

---

## 13. Dependency Summary

The Foundation docs are related, but they are not interchangeable.

### Core dependency shape

- `hermes-foundation-v1.md` is the orientation baseline
- `foundation-pillar-map-v1.md` explains role and dependency relationships
- `foundation-docs-index-v1.md` explains access path and reference timing

### Gate and risk layer

- `planning-gate-policy-v1.md` depends on Foundation principles
- `high-risk-operation-taxonomy-v1.md` depends on shared boundary concepts
- `implementation-readiness-review-v1.md` depends on both gate and risk language

### Context layer

- `memory-system-v1.md`, `human-model-v1.md`, `decision-profile-v1.md`, `decision-support-v1.md`, and `domain-model-v1.md` all depend on the Foundation distinction between support and authority

### Worker and execution layer

- `worker-architecture-v1.md` depends on gate and risk thinking
- dispatch logic should be interpreted through worker boundaries, not through backlog presence or report output

### Quality and evolution layer

- `quality-framework-v1.md` defines evaluation language
- `weekly-quality-report-v1.md` depends on quality language but does not extend authority
- `improvement-backlog-v1.md` depends on quality findings and reviewed candidate capture
- `continuous-evolution-v1.md` depends on evaluation, reviewability, and explicit adoption

Dependency rule:

> Later documents usually depend on earlier concepts, but dependency is not permission.

---

## 14. Non-authorization Rule

Every document in this index must be read under the same rule:

> Foundation documents can guide, clarify, warn, classify, and organize. They do not authorize execution by themselves.

This means:

- a roadmap is not approval
- an index is not approval
- a readiness review is not approval
- a backlog entry is not approval
- a weekly report is not approval
- a quality finding is not approval
- a risk classification is not approval
- a worker role definition is not approval
- memory is not approval
- past preference is not approval

Actual permission must still come from the current instruction and, where relevant, explicit approval for high-risk actions.

Strong reminder:

> Current user instruction wins.

---

## 15. Dangerous Misunderstandings

This section lists common errors the index is designed to prevent.

### 15.1 “The backlog item exists, so implementation is allowed”

Wrong.

Backlog is inventory, not authorization.

### 15.2 “The readiness review says ready, so push is allowed”

Wrong.

Ready does not mean push-approved.

### 15.3 “The quality report flagged a problem, so autonomous repair is allowed”

Wrong.

Weekly Quality Report observes and reports; it does not govern.

### 15.4 “The risk taxonomy says medium, so no explicit approval is needed”

Wrong.

Risk labels help classify; they do not override current instructions or mode boundaries.

### 15.5 “The worker architecture mentions a worker, so the worker may self-start”

Wrong.

Worker Architecture defines boundaries. It does not create dispatch permission.

### 15.6 “Memory says the user usually prefers X, so do it now”

Wrong.

Past preference is context, not current approval.

### 15.7 “The Foundation docs all point toward the same direction, so execution is obvious”

Wrong.

Shared direction still does not equal authorization.

### 15.8 “This is docs-only, so any related doc edits are fine”

Wrong.

Docs-only scope is still path-bounded and request-bounded.

### 15.9 “Push is routine maintenance, so no extra caution is needed”

Wrong.

Push has publication impact and follows current operational policy.

### 15.10 “Index selected the reading order, so all prerequisites are satisfied”

Wrong.

The index helps navigation. It does not confirm completion, comprehension, or approval.

---

## 16. Recommended Next Review Step

After this index exists, the most useful next review step is:

- verify cross-links and naming consistency across the Foundation document set

A practical follow-up artifact would be:

- `docs/product/foundation-crosslink-audit-v1.md` (optional future review doc; not yet created)

Suggested scope for that review:

- confirm every referenced Foundation doc path is correct
- confirm each doc states clearly what it is not
- confirm non-authorization language is consistent
- confirm overlapping terms like approval, readiness, backlog, report, mutation, and dispatch are used consistently
- confirm no document silently implies autonomous governance

That follow-up should remain documentation-only unless explicit broader approval is given.

---

## Closing note

Foundation Docs Index v1 should make the Foundation document set easier to navigate, but it should never become a substitute for approval discipline.

If this index works correctly, it reduces confusion without increasing automation.

That is the intended result.
