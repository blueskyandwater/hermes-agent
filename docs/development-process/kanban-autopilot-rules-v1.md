# Kanban Autopilot Rules v1

## Goal

Define when Kanban cards may be executed automatically and where human approval is required.

These rules are a development-process document only. They do not change code, runtime behavior, Kanban dispatcher behavior, worker behavior, gateway/API/CLI behavior, memory behavior, or Human Model behavior.

Use this document together with `docs/development-process/hermes-development-autopilot-policy-v1.md`. The policy defines development modes; this document defines how those modes map to Kanban automation and card prefixes.

## Background

Hermes development increasingly uses Kanban dispatcher and worker automation. This is useful because workers can pick up cards, inspect the repository, produce documentation, run tests, and close narrow tasks without repeated long prompts.

However, Kanban automation has operational risk:

- The Kanban dispatcher can automatically move cards through `ready`, `running`, and `done`.
- A card that was meant to be only a backlog registration can be picked up by a worker if it becomes executable.
- `done` is a workflow state. It does **not** prove that a concrete artifact exists, that tests passed, that a commit exists, or that a push happened.
- Git reality, documentation artifacts, commits, pushes, and Kanban state must be verified separately.
- Autopilot modes should therefore be explicit and narrow, and high-risk areas must remain behind human approval.

The safe default is: automate small, reversible, inspectable steps; stop before broad implementation, external exposure, memory mutation, Human Model mutation, or upstream operations.

## Core Rules

1. `[Backlog]` cards must never be auto-run.
   - They are inventory, not execution authorization.
   - If a backlog card becomes `ready` or `running`, automation should stop and report it.

2. `[Planning]` cards are limited to read-only or design-only work.
   - They may inspect current state and propose boundaries.
   - They must not implement code, commit, push, or sync Kanban to `done` unless a separate approved mode authorizes it.

3. Design cards may be automated through documentation and local commit.
   - `design-doc-commit-only` may create or edit explicitly requested docs files and commit those docs.
   - It must not push, mutate Kanban, or change runtime behavior.

4. Implementation cards are normally limited to implementation plus tests without commit.
   - `implementation-no-commit` may modify explicitly scoped code/tests and run tests.
   - It must stop before staging or committing.

5. Commits require bounded scope and passing verification.
   - Commit automation is allowed only when target files are explicitly limited.
   - The relevant tests or checks must pass, or the failure must be reported and the commit skipped.
   - `git add .` and `git commit -a` are prohibited.

6. Pushes must be isolated as `push-only`.
   - Push automation may only push already-created local commits.
   - It must use `git push origin main`.
   - Bare `git push` is prohibited.

7. Kanban sync may happen only after Git/artifact reality is verified.
   - `kanban-sync-only` may update only the explicitly named target card.
   - It may mark the card `done` or clear assignee only when the completed artifact, commit, push, or other stated evidence has already been verified.

8. Gateway/API/CLI, memory, and Human Model changes always require human approval.
   - These areas can affect external surfaces or future behavior and must not be widened by automation.

9. Upstream operations are prohibited.
   - Do not push to `upstream`.
   - Do not create upstream PRs unless the user explicitly authorizes a separate PR task.

## Automation Levels

### Level 0: read-only

Purpose: inspect and report only.

Allowed:

- Read repository files.
- Run read-only commands.
- Read Kanban card state.
- Report current status and risks.

Prohibited:

- File edits.
- Git staging, commit, or push.
- Kanban mutation.
- Runtime changes.

### Level 1: design-only

Purpose: produce a design recommendation or execution boundary.

Allowed:

- Read-only investigation.
- Design analysis and recommendation.
- Kanban card creation only when explicitly requested.

Prohibited:

- Code implementation.
- Docs commit.
- Push.
- Kanban execution or `done` sync.
- Runtime changes.

### Level 2: design-doc-commit-only

Purpose: write a bounded documentation artifact and commit it locally.

Allowed:

- Create or edit explicitly requested docs files.
- Run relevant checks if needed.
- Stage only the explicitly requested docs path(s).
- Create a local commit.

Prohibited:

- Code implementation.
- Runtime changes.
- Kanban changes.
- Push.
- PR creation.

### Level 3: implementation-no-commit

Purpose: make a small implementation and run tests, then stop for review.

Allowed:

- Modify explicitly scoped implementation files.
- Add or update explicitly scoped tests.
- Run relevant tests.
- Report diff and test result.

Prohibited:

- `git add`.
- Commit.
- Push.
- Kanban `done` sync.
- Gateway/API/CLI exposure unless separately approved.

### Level 4: implementation-review-commit

Purpose: commit only a human-reviewed implementation diff.

Allowed:

- Inspect the reviewed diff.
- Re-run relevant tests.
- Stage only human-approved files.
- Create a local commit.

Prohibited:

- Editing beyond the reviewed diff.
- `git add .`.
- Push.
- Kanban mutation.
- Runtime connection changes.

### Level 5: push-only

Purpose: push existing local commits to `origin/main`.

Allowed:

- Verify branch and status.
- Verify ahead commits.
- Run `git push --dry-run origin main`.
- Run `git push origin main`.

Prohibited:

- Bare `git push`.
- Push to `upstream`.
- Commit.
- File editing.
- Staging.
- Kanban changes.
- PR creation.

### Level 6: kanban-sync-only

Purpose: synchronize one card with already-verified Git/artifact reality.

Allowed:

- Read the explicit target card.
- Update only the explicit target card.
- Mark it `done` and/or clear assignee only when the evidence is already verified.
- Verify the target card after mutation.

Prohibited:

- Git changes.
- File editing.
- Default board changes.
- Updating any card other than the explicit target.
- Creating follow-up cards unless explicitly requested.

## Prefix Rules

Use card prefixes to determine the highest allowed automation level.

| Prefix | Meaning | Maximum automatic level |
| --- | --- | --- |
| `[Backlog]` | Inventory only | Never auto-run |
| `[Planning]` | Planning and boundary definition | Level 1: design-only |
| `[Design]` | Documentation/design artifact | Level 2: design-doc-commit-only |
| `[Implementation]` | Small scoped implementation | Level 3: implementation-no-commit |
| `[Review]` | Human-reviewed commit lane | Level 4 only after human approval |
| `[Push]` | Push an existing commit | Level 5: push-only |
| `[Sync]` | Align Kanban with verified reality | Level 6: kanban-sync-only |
| `[High-Risk]` | Sensitive area | Human approval required |

If a card has no prefix, automation must treat it conservatively as Level 0 until a human assigns a mode or prefix.

## High-risk Areas

The following always require human approval before automation may modify, expose, or connect them:

- Gateway/API/CLI publication or external exposure.
- External schema changes.
- Broad `run_agent.py` changes.
- `agent/conversation_loop.py` injection-route changes.
- `prompt_builder.py` changes.
- Memory read/write integration.
- Human Model mutation.
- Domain Model implementation.
- Decision Style implementation.
- Quality judge behavior that suppresses or alters injection.
- Authentication, security, logging, or redaction changes.
- Upstream operations.

High-risk work should normally be split into:

1. `design-only`
2. `design-doc-commit-only`
3. human approval
4. `implementation-no-commit`
5. human review
6. `implementation-review-commit`
7. `push-only`
8. `kanban-sync-only`

## Stop Conditions

Automation must stop and report instead of continuing when any of the following occurs:

- Files outside the target scope are modified.
- Tests fail and the failure cannot be resolved within the authorized scope.
- Unexpected untracked files appear.
- Git status is unknown, ambiguous, or dirty outside the target scope.
- `origin/main..HEAD` has an unexpected ahead count.
- An auto-generated review card is already `running`.
- A `[Backlog]` card becomes `ready` or `running`.
- A high-risk file or subsystem appears in the proposed change set.
- A worker is about to cross a docs, commit, push, or Kanban-sync boundary not authorized by the current mode.
- The staged file list differs from the explicit approved target list.
- A command would use `upstream`, bare `git push`, `git add .`, or `git commit -a`.

When a stop condition is hit, the correct output is a short report with the confirmed state, the blocker, and the next human decision needed.

## Output Contract

Every Kanban automation run must finish with a report containing:

- `mode`
- Target card id and title
- Changed files
- Test result or check result
- Commit hash, if a commit was created
- Push state
- Kanban mutation state
- Whether high-risk files or systems were touched
- Blocking Issues
- Non-blocking Issues
- Next human approval needed

If the run is read-only or stops early, use `N/A` for fields that do not apply instead of inventing results.

## Recommended Next Step

Do not connect these rules directly to worker or dispatcher runtime behavior in this Story.

The next safe step is to make Kanban worker and dispatcher prompts load or reference this rules document so automation can classify cards consistently before executing them.

Runtime enforcement, dispatcher code changes, card-prefix parsers, or worker prompt wiring should be implemented in separate Stories with explicit human approval.

## Non-goals

This document does not:

- Implement dispatcher behavior.
- Change Kanban worker routing.
- Modify runtime behavior.
- Modify gateway/API/CLI behavior.
- Read from or write to memory.
- Mutate Human Model data.
- Define Domain Model or Decision Style behavior.
- Authorize upstream operations.
- Replace human approval for high-risk operations.
