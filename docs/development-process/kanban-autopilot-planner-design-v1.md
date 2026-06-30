# Kanban Autopilot Planner Design v1

## 1. Purpose

Kanban Autopilot Planner is not an execution mechanism.

It is a pre-execution planner that inspects the `hermes-product` board and Planning documents in read-only mode before dispatcher or worker automation decides what to run next.

Its purpose is to judge and report:

- which cards may be safe next-step candidates;
- which cards must not run;
- which cards are blocked by Planning, readiness, risk, Git, or evidence gaps;
- which boundaries require human approval before any mutation or execution.

Planner output is a recommendation and safety report only. It does not authorize implementation, Git mutation, Kanban mutation, dispatcher execution, push, Planning Gate changes, or High-Risk approval.

This design fixes the read-only Planner specification before any CLI planner or dispatcher gate is implemented.

## 2. Responsibilities

The Planner is responsible for the following read-only activities.

1. **Read Kanban in read-only mode**
   - Inspect the `hermes-product` board.
   - Read card id, title, status, body, assignee, prefix, and mode when available.
   - Treat Kanban state as workflow evidence, not proof that artifacts, commits, pushes, or tests exist.

2. **Read Planning documents**
   - Use the Planning System Note, Product Vision, Definition of Ready, Roadmap, Planning Gate Policy, Development Autopilot Policy, Kanban Autopilot Rules, and Manual Prompt as evidence sources.
   - Do not treat document existence as permission to execute.

3. **Read Git state**
   - Inspect `git status`.
   - Inspect `origin/main..HEAD`.
   - Detect whether the worktree is dirty.
   - Use Git state only to classify candidate lanes; do not mutate Git.

4. **Classify each relevant card as Ready or Not Ready**
   - Check mode presence.
   - Check prefix / lane.
   - Check Planning Gate assumptions.
   - Check high-risk status.
   - Check whether artifact, commit, push, or review evidence is missing.

5. **Classify card lane**
   - Backlog
   - Planning
   - Implementation
   - Review
   - Push
   - Sync
   - High-Risk
   - unknown / no-prefix

6. **Return at most three next-step candidates**
   - Rank only candidates that are supported by the available evidence.
   - Return fewer than three candidates when fewer are safe.
   - Return `N/A` when there is no safe candidate.

7. **Return a must-not-run list**
   - Identify cards, categories, or conditions that must not be executed automatically.
   - Include reason and required human decision when useful.

8. **Ask for human approval at boundaries**
   - Human approval is required before Git mutation, Kanban mutation, dispatcher execution, push, Planning Gate mutation, High-Risk work, runtime exposure, or any unclear scope expansion.

## 3. Non-responsibilities

The Planner must not perform any of the following actions:

- Kanban state changes
- assignee changes
- card creation
- card deletion
- Git operations
- file editing
- implementation
- commit
- push
- Planning Gate changes
- dispatcher execution
- High-Risk automatic approval
- prefix automatic completion
- mode automatic completion

The Planner may report that one of these actions is needed, but it must not perform the action itself.

## 4. Classification

The Planner uses the following classification values.

| Classification | Meaning |
| --- | --- |
| `ready-for-design` | Safe candidate for read-only or design-only planning work. |
| `ready-for-design-doc` | Safe candidate for explicitly scoped documentation work, usually under `design-doc-commit-only`. |
| `ready-for-implementation-no-commit` | Candidate for bounded implementation without staging or commit, only when Definition of Ready and gate assumptions allow it. |
| `ready-for-review-commit` | Candidate for review / commit lane when a scoped dirty worktree or reviewed diff exists, but content inspection is still required before staging. |
| `ready-for-push` | Candidate for push-only when `origin/main..HEAD > 0`, the branch and target are known, and human approval authorizes push. |
| `ready-for-kanban-sync` | Candidate for syncing one explicitly identified card after artifact, Git, commit, push, or other evidence is already verified. |
| `not-ready` | Missing mode, scope, handoff, evidence, verification, or other readiness requirement. |
| `blocked-by-gate` | Implementation or routing is blocked because Planning Gate assumptions do not allow execution. |
| `high-risk-needs-human` | High-risk area requires explicit human approval before any modifying action. |
| `backlog-never-run` | Backlog inventory; must never be automatic execution. |
| `not-ready-for-close` | Kanban `done` or close state is not backed by required artifact, commit, push, test, review, or sync evidence. |

Classification is advisory. It identifies the safest lane and the next approval boundary; it does not execute the lane.

## 5. Judgment Rules

The Planner applies these rules when classifying cards and ranking candidates.

1. **`[Backlog]` is `backlog-never-run`.**
   - Backlog means inventory, not execution authorization.
   - If a backlog card becomes `ready` or `running`, automation must stop and report.

2. **`[Planning]` is limited to `ready-for-design`.**
   - Planning cards may support read-only investigation or design-only work.
   - They must not be treated as implementation cards by status movement alone.

3. **`[High-Risk]` is `high-risk-needs-human`.**
   - High-risk work always requires explicit human approval before mutation, exposure, or implementation.

4. **Cards without a prefix are not automatic execution targets.**
   - No-prefix cards are treated conservatively as Level 0.
   - They may be reported, but must not be routed automatically.

5. **Implementation cards without a mode are `not-ready`.**
   - A card must not be routed to implementation from title, status, or assignee alone.
   - Mode must match allowed actions.

6. **If the Planning Gate is closed, implementation is `blocked-by-gate`.**
   - Roadmap, Product Vision, or Definition of Ready existence does not automatically open the gate.
   - Gate state and Story readiness are separate controls.

7. **A `done` card without artifact / commit / push evidence is `not-ready-for-close`.**
   - Kanban `done` does not prove a document exists.
   - It does not prove tests passed.
   - It does not prove a commit or push happened.

8. **If `origin/main..HEAD > 0`, the Planner may report a `ready-for-push` candidate.**
   - The candidate must remain push-only.
   - Human approval is required before `git push origin main`.
   - Bare `git push` and upstream push remain prohibited.

9. **If the worktree is dirty, the Planner may report a `ready-for-review-commit` candidate.**
   - The dirty diff must be inspected before staging or committing.
   - The Planner itself must not stage, commit, or edit.

10. **If there are no `ready`, `running`, or reviewable cards, candidate ranking may be zero.**
    - The Planner must not invent work.
    - `N/A` is a valid candidate result.

11. **The Planner must not force three candidates.**
    - Return the number of candidates supported by evidence.
    - If none are safe, return zero / `N/A`.

12. **Blocked cards are not execution candidates.**
    - They may be reported only as human-decision items.

13. **Candidate fields must be explicit.**
    - Each candidate must include classification, required mode, risk level, reason, blocked reason, and next human approval.
    - Use `N/A` when evidence is unavailable rather than inventing it.

## 6. Output Contract

Planner output must use a stable, reviewable contract so it can later be converted into a CLI planner or dispatcher gate.

Required fields:

- `mode`
- board summary
- git status
- gate assumption
- candidate ranking
- classification
- required mode
- risk level
- reason
- blocked reason
- next human approval
- must-not-run list
- notes

Recommended format:

```text
mode: planner-read-only

board summary:
- total cards:
- by status:
- ready/running/review:
- blocked:
- no-prefix:
- git status:
- ahead count:
- dirty worktree:
- gate assumption:

candidate ranking:
1. id/title or N/A
   - classification:
   - required mode:
   - risk level:
   - reason:
   - blocked reason:
   - next human approval:

must-not-run list:
- ...

notes:
- gate/doc mismatch:
- evidence mismatch:
- missing mode/prefix:
```

Output rules:

- Use confirmed facts from board, Git, and docs.
- Separate confirmed blockers from assumptions.
- Use `N/A` when a field does not apply.
- Candidate ranking is a recommendation, not authorization.
- The Planner should explicitly state when human approval is required before the next step.

## 7. Current Board Lessons

The initial `hermes-product` design investigation produced the following lessons.

- The current board has many no-prefix cards.
- No-prefix cards should be treated as Level 0 until a human assigns a prefix or mode.
- If there are no `ready` or `running` cards, there is no automatic execution candidate.
- Blocked cards should be reported only as human-decision items, not execution candidates.
- `done` cards must not be considered truly closed without artifact, commit, push, test, review, or other required evidence.
- The Planner must be able to return zero candidates instead of forcing a candidate list.

These lessons apply to manual prompt operation and should also shape future CLI planner and dispatcher gate behavior.

## 8. Implementation Path

The recommended path is:

```text
C -> A -> D
```

Meaning:

1. **C: docs + manual prompt operation**
   - Use the Manual Prompt to run read-only Planner checks by hand.
   - Fix judgment rules and output format before code or runtime enforcement.
   - This is the safest first step because it changes no runtime behavior.

2. **A: CLI planner minimal implementation**
   - Add a read-only command that gathers board, Git, and Planning-doc evidence.
   - Produce the same output contract as the Manual Prompt.
   - Keep it non-mutating and testable.

3. **D: dispatcher pre-gate**
   - Put Planner judgment in front of dispatcher execution.
   - Block `not-ready`, `blocked-by-gate`, `high-risk-needs-human`, `backlog-never-run`, and no-prefix automatic execution.
   - This is the target runtime guard, but it should come last because dispatcher behavior has higher blast radius.

Short comparison of implementation options:

| Option | Summary |
| --- | --- |
| Manual Prompt | Safest and requires zero runtime change, but depends on human operation. |
| CLI Planner | Read-only, testable, and a good bridge from manual operation to enforcement. |
| Dispatcher Gate | Strongest protection against dispatcher runaway, but high risk and should come after the planner contract is stable. |
| Worker Prompt only | Lightweight but weak because prompt-only enforcement can drift and is hard to test deterministically. |
| API endpoint | Potentially useful later, but currently excessive and high risk because it exposes another surface. |

## 9. Next Stories

Recommended next Story candidates:

1. **Kanban Planner CLI Minimal Implementation**
   - Implement a read-only CLI command that emits the Planner output contract.
   - No dispatcher changes.
   - No Kanban mutation.

2. **Dispatcher Prefix Guard Design**
   - Design how dispatcher should treat `[Backlog]`, `[Planning]`, `[High-Risk]`, and no-prefix cards before any code change.

3. **Dispatcher Prefix Guard Minimal Implementation**
   - Add the smallest guard that prevents unsafe prefix / no-prefix automatic execution.
   - Only after design and CLI planner behavior are stable.

4. **Board Prefix Cleanup Planning**
   - Plan how to classify existing no-prefix cards without automatic mutation.
   - Any actual card mutation should be a separate explicitly approved Kanban task.

## 10. Non-goals

Planner Design v1 does not do any of the following:

- CLI implementation
- dispatcher changes
- Kanban changes
- card creation
- prefix completion
- mode completion
- High-Risk automatic approval
- gateway/API/CLI publication
- memory updates
- Human Model updates
- runtime behavior changes
- upstream operations

It is a design artifact only. It defines the Planner contract so later implementation can be narrow, testable, and safer.

## 11. Success Criteria

Planner Design v1 is successful when:

1. The Planner's responsibilities are clear.
2. The Planner's non-responsibilities and mutation boundaries are explicit.
3. Ready / Not Ready classifications are stable enough for manual operation.
4. Judgment rules distinguish backlog, planning, implementation, high-risk, push, sync, and close-evidence cases.
5. Output fields are stable enough to become a CLI contract later.
6. The implementation path preserves the sequence: manual prompt operation, then CLI planner, then dispatcher gate.
7. Human approval remains required before mutation, execution, push, Planning Gate changes, and high-risk work.
