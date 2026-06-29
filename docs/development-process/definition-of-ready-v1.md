# Definition of Ready v1

## 1. Purpose

Definition of Ready defines the minimum conditions that must be true before a Planning result may be handed to Implementation.

It is a readiness standard, not a completion standard. It does not prove that work is done; it proves that implementation may safely begin because purpose, scope, mode, risks, verification, and boundaries are clear enough.

The main purpose is to prevent:

- Implementation work from starting before Planning is sufficiently defined.
- Backlog cards from being treated as executable work.
- Planning cards from being auto-run as implementation.
- Dispatcher or worker automation from moving faster than product intent, safety boundaries, or evidence.

---

## 2. Scope

### 2.1 In Scope

This Definition of Ready applies to:

- **Implementation cards**
  - Cards that create, modify, verify, or commit artifacts.
- **Stories moving from Design to Implementation**
  - Work where a design note, planning artifact, or scoped request is being converted into executable work.
- **Stories involving high-risk areas**
  - Work that touches sensitive runtime, memory, model, security, gateway, CLI, or human-context paths.
- **Stories handed to Autopilot**
  - Work routed to dispatcher, workers, or mode-specific automation.

### 2.2 Out of Scope

This Definition of Ready does not apply to:

- **Backlog registration**
  - Capturing an idea does not require full implementation readiness.
- **Planning read-only investigation**
  - Reading current state, prior docs, or logs to prepare a plan is not implementation.
- **design-only work**
  - Pure design artifacts may be created under their own explicit mode and boundaries.
- **push-only work**
  - Push-only verifies and publishes an already completed commit; it does not define implementation readiness.
- **kanban-sync-only work**
  - Kanban sync reflects already-verified artifact / Git / push reality; it must not create new implementation scope.

---

## 3. Ready Checklist

A Story or Implementation card is Ready only when all required items below are satisfied or explicitly marked not applicable with a reason.

1. **Purpose is expressible in one sentence**
   - The work can be summarized as one clear purpose statement.
   - A reader can tell why this work exists without reconstructing prior conversation.

2. **Expected deliverable is clear**
   - The artifact, code change, document, verification result, or operational result is named.
   - The deliverable is concrete enough to review.

3. **Scope and Non-goals are present**
   - The work says what is included.
   - It also says what must not be changed or solved in this Story.

4. **Candidate target files or surfaces are identified**
   - Expected files, directories, modules, docs, commands, or runtime surfaces are listed.
   - If exact files are unknown, the discovery scope must be bounded.

5. **High-risk area status is assessed**
   - The Story says whether it touches any high-risk area.
   - If yes, the required human approval boundary is explicit.

6. **Mode is specified**
   - The execution mode is named, such as `design-doc-commit-only`, `implementation-no-commit`, `implementation-review-commit`, `push-only`, or `kanban-sync-only`.
   - The mode must match the allowed actions.

7. **Success Criteria are defined**
   - The Story says how to know the work succeeded.
   - Success Criteria must be checkable, not only aspirational.

8. **Tests or verification method is defined**
   - The Story names tests, commands, review steps, or artifact checks.
   - If automated tests are not applicable, the manual verification method must be stated.

9. **Git and Kanban boundaries are explicit**
   - The Story says whether `git add`, commit, push, PR, upstream operations, or Kanban mutation are allowed.
   - Forbidden operations must be stated when relevant.

10. **Dependencies are clear**
    - Required prior docs, commits, cards, approvals, data, or decisions are listed.
    - Unresolved dependencies are either closed before implementation or named as stop conditions.

11. **Rollback or stop conditions exist**
    - The Story says when the worker must stop instead of improvising.
    - For implementation work, rollback, revert, or leave-uncommitted behavior should be clear.

12. **Planning source doc or design note exists**
    - The handoff points to a Planning source, Product Vision, Roadmap item, design note, or explicit user request.
    - Implementation must not begin from an unstructured backlog title alone.

---

## 4. Autopilot Mode Readiness

Autopilot modes are readiness contracts. A Story is not ready for a mode unless the corresponding conditions are satisfied.

### 4.1 `design-doc-commit-only`

Ready when:

- The documentation target path is explicit.
- The source documents to inspect are listed.
- Code implementation and runtime changes are explicitly forbidden.
- The commit target is limited to the named docs file or files.
- `git add .` and broad staging are forbidden.
- Push, PR creation, Kanban mutation, gateway/API/CLI changes, memory changes, and Human Model updates are forbidden unless separately authorized.

This mode is appropriate for bounded documentation artifacts that should be committed locally but not pushed.

### 4.2 `implementation-no-commit`

Ready when:

- Target files, modules, or discovery boundaries are limited.
- The test or verification plan is clear.
- Commit and push are explicitly forbidden.
- Expected final state is clear, usually changed files left unstaged for review.
- Stop conditions exist for scope expansion, high-risk discovery, failing tests that need design changes, or unexpected unrelated worktree changes.

This mode is appropriate for creating or modifying implementation artifacts before human review and commit authorization.

### 4.3 `implementation-review-commit`

Ready when:

- The diff has already been reviewed or the review boundary is explicitly part of the task.
- Target files are limited and unrelated changes are excluded.
- Required tests or checks have passed, or blockers are documented and accepted by the user.
- Commit is allowed, but push is explicitly forbidden.
- The staged file set must be verified before commit.
- The commit message matches the narrow scope.

This mode is appropriate when implementation is already bounded enough to create a local commit after verification.

### 4.4 `push-only`

Ready when:

- The worktree is clean.
- The current branch is known.
- The exact HEAD commit, commit message, and changed files are known.
- The ahead count is clear.
- The push target is explicitly `origin main` or another approved origin branch.
- `git push` without remote / branch is forbidden.
- `git push upstream`, PR creation, rebase, reset, new commits, file edits, and Kanban changes are forbidden.
- A dry-run push is requested or otherwise appropriate before the real push.

This mode is appropriate only for publishing already-reviewed local commits to the approved remote branch.

### 4.5 `kanban-sync-only`

Ready when:

- Git, artifact, test, commit, and push reality is already verified as applicable.
- The target card is explicitly identified.
- The intended Kanban state transition is explicit.
- File edits, Git changes, commits, pushes, PRs, runtime changes, and implementation are forbidden.
- The sync records evidence rather than creating new work.

This mode is appropriate only for aligning board state to already-confirmed reality.

---

## 5. High-risk Readiness

A Story that touches any high-risk area is not Ready for implementation until the user has explicitly approved the risk boundary and allowed actions.

High-risk areas include:

1. **Gateway / API / CLI exposure**
   - Adding or changing externally reachable surfaces, commands, endpoints, adapters, or invocation paths.

2. **External schema changes**
   - Changing message formats, persisted state formats, webhook payloads, API contracts, or data shared with other systems.

3. **Memory read/write behavior**
   - Changing what memory is read, written, inferred, injected, filtered, or persisted.

4. **Human Model mutation**
   - Changing durable user-model content, mutation rules, snapshot behavior, or approval requirements.

5. **Broad `run_agent.py` changes**
   - Modifying core loop behavior, routing of tool calls, model calls, role alternation, or multi-turn execution semantics.

6. **`conversation_loop` injection path changes**
   - Changing where user context, memory, system prompt fragments, tool outputs, or runtime metadata are injected.

7. **`prompt_builder.py` changes**
   - Changing system prompt construction, environment hints, constitutional layers, memory rendering, or execution guidance.

8. **Domain Model / Decision Style integration**
   - Adding or applying specialized user decision layers that may affect recommendation behavior.

9. **Quality judge inject suppress behavior**
   - Allowing a judge, metric, or review layer to suppress, rewrite, or inject content into normal responses.

10. **Auth, security, logging, or redaction changes**
    - Changing credentials, token handling, permission checks, logging of sensitive data, or redaction boundaries.

11. **Upstream operations**
    - Pushing to upstream, creating upstream PRs, changing upstream remotes, or treating upstream as a write target.

For high-risk Stories, the handoff must include:

- explicit risk label
- human approval record or direct user instruction
- allowed files / surfaces
- forbidden files / surfaces
- verification plan
- rollback or stop condition

---

## 6. Not Ready Conditions

A Story or card is Not Ready if any of the following are true:

- It is still only a **Backlog** card.
- It is still only a **Planning** card.
- Purpose is vague or cannot be written in one sentence.
- Expected deliverable is unknown.
- Tests or verification method is unknown.
- Mode is missing.
- High-risk status has not been assessed.
- Dependencies are unresolved or not listed.
- There is no docs / design seed, Planning source, or explicit user request.
- An automatic dispatcher moved the card to `ready` or `running` without a valid handoff.
- `done` status does not match artifact / commit / push reality.
- Target files or surfaces are too broad for safe execution.
- The task requires human approval but approval is missing.
- The task asks a worker to infer forbidden actions from context instead of stating them.

When a Not Ready condition is found, the correct action is to stop, report the missing readiness item, and return the item to Planning rather than improvising implementation.

---

## 7. Handoff Template

The following is the minimum handoff template for moving work from Planning to Implementation.

```markdown
# Implementation Handoff

mode: <execution mode>

Story title: <short title>

Planning source: <doc path, design note, card id, commit, or user request>

Goal:
<one-sentence purpose>

Scope:
- <included item>
- <included item>

Non-goals:
- <excluded item>
- <excluded item>

Target files:
- <path or bounded discovery area>

Allowed actions:
- <allowed action>

Forbidden actions:
- <forbidden action>

Tests / verification:
- <command, review step, or artifact check>

Success Criteria:
- <checkable criterion>

Stop Conditions:
- <condition that requires stopping and reporting>

Output Contract:
- <required final response fields>
```

The template may be expanded for complex work, but it should not remove these fields for implementation handoff.

---

## 8. Relationship to Planning Gate

Definition of Ready is used at Planning Gate Level 2 and later.

While the Planning Gate is closed, Implementation cards should not be created, marked ready, or routed to workers. Planning may continue as read-only or design-only work, but it must not be converted into implementation by status movement alone.

Definition of Ready is separate from the Planning Gate release condition:

- **Planning Gate Policy** decides whether the system is allowed to create and route implementation work at all.
- **Definition of Ready** decides whether a specific Story is ready to become implementation work after the gate allows handoff.

When the gate is open, DoR still applies per Story. A globally open gate does not make every backlog or planning item ready.

---

## 9. Non-goals

Definition of Ready v1 is not:

- an implementation procedure
- a Roadmap
- a Product Vision
- a Kanban dispatcher implementation
- a permission slip for high-risk work without approval
- a replacement for tests, review, or Definition of Done
- a mechanism for auto-promoting backlog or planning cards
- a runtime, gateway, API, CLI, memory, or Human Model change

---

## 10. Success Criteria

Definition of Ready v1 is successful when:

1. It clearly explains when Planning output may be handed to Implementation.
2. It distinguishes readiness from done.
3. It prevents Backlog and Planning cards from becoming executable by status drift alone.
4. It defines mode-specific readiness for docs commit, implementation, push, and Kanban sync lanes.
5. It names high-risk areas that require human approval before implementation.
6. It provides a reusable handoff template.
7. It can be used with Planning Gate Level 2+ as a Story-level readiness standard.

---

## 11. Change Rule

Definition of Ready v1 is a durable development-process artifact.

It may be revised, but revisions should be explicit and reviewed. Changes that loosen high-risk approval, allow automatic memory or Human Model mutation, broaden gateway/API/CLI exposure, weaken Git/Kanban boundaries, or allow Implementation without Planning require human approval.
