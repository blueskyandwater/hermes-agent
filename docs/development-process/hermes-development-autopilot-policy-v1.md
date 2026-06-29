# Hermes Development Autopilot Policy v1

## Goal

Define safe autopilot modes for Hermes development work.

The purpose of this policy is to reduce the need to repeat long prompts for common lanes such as "design only", "implementation only", "commit only", "push only", and "Kanban sync only", while preventing unsafe automation such as runaway implementation, surprise pushes, gateway/API exposure, or memory mutation.

This policy is a development-process document only. It does not change runtime behavior, router behavior, gateway behavior, Kanban dispatch behavior, or memory/Human Model behavior.

## 1. Background

Hermes development often uses Kanban cards, worker profiles, local commits, design notes, and runtime entry points together. That is powerful, but it creates risk when multiple responsibilities are mixed in one automated task.

Key observations:

- Kanban is useful for tracking development work, but the dispatcher can automatically move cards through `ready`, `running`, and `done` depending on board configuration and worker behavior.
- A Kanban `done` state does not, by itself, prove that the expected artifact exists, was reviewed, was committed, or was pushed.
- Design, docs creation, implementation, commit, push, and Kanban synchronization are separate operations. Mixing them in one unattended flow increases the chance of unintended changes.
- Some Hermes areas have a larger blast radius than ordinary documentation or local implementation work, especially:
  - `agent/conversation_loop.py`
  - `run_agent.py`
  - gateway/API/CLI entry points
  - memory read/write paths
  - Human Model paths
  - prompt construction and injection paths
- Gateway/API/CLI exposure can change the external input surface.
- Memory and Human Model mutation can affect future sessions and user-specific behavior.

Therefore, Hermes development work should be split into explicit modes with clear permission boundaries, stop conditions, and output contracts.

## 2. Core Principle

Hermes development autopilot must prefer small, reviewable steps.

Required principles:

- Move in small units.
- Do not combine implementation and push in the same automatic process.
- Keep gateway/API/CLI exposure in a separate Story from internal implementation.
- Memory updates and Human Model updates always require explicit human approval.
- Treat Kanban `done` as workflow state, not proof that a concrete artifact exists. Docs, commits, pushes, and tests must be verified separately.
- Do not use `git add .`.
- Do not use bare `git push`.
- When pushing to the user's fork main branch, use `git push origin main` explicitly.
- Do not push to `upstream`.
- Do not create PRs unless the user explicitly asks; by default, upstream PR creation is prohibited.
- If the current state does not match the requested mode, stop and report rather than broadening scope.

## 3. Autopilot Modes

### mode: `design-doc-commit-only`

#### Purpose

Save an already-decided design result as documentation and commit only that documentation.

#### Allowed

- Create or edit the explicitly requested docs file(s).
- Run optional tests or documentation checks if relevant.
- Stage only the explicitly requested docs path(s).
- Create a local commit.

#### Prohibited

- Code implementation.
- Runtime connection or behavior changes.
- Git push.
- Kanban state changes.
- Gateway/API/CLI changes.
- Memory or Human Model changes.

#### Stop conditions

Stop immediately if any of the following occur:

- Files outside the requested docs scope are modified.
- Tests fail and the failure is relevant to the requested change.
- `git status` contains unexpected changes.
- The staged file list differs from the explicit target file list.

#### Success conditions

- The requested documentation exists.
- Only the requested documentation path(s) were staged.
- A local commit exists with the requested or scope-appropriate message.
- No push was performed.
- No Kanban mutation was performed.

### mode: `implementation-no-commit`

#### Purpose

Make a small implementation and run tests, then stop for human review before staging or committing.

#### Allowed

- Implement only the explicitly requested files or scope.
- Add or update tests for the requested implementation.
- Run relevant tests.
- Report the diff and test result.

#### Prohibited

- `git add`.
- Commit.
- Push.
- Kanban `done` synchronization.
- Gateway/API/CLI publication unless the Story explicitly authorizes that exposure.
- Memory or Human Model changes unless explicitly authorized.

#### Stop conditions

Stop immediately if any of the following occur:

- A file outside the requested implementation scope changes.
- Tests fail and cannot be fixed within the requested scope.
- The implementation requires changing gateway/API/CLI exposure not authorized by the Story.
- The implementation scope expands beyond the Story boundary.

#### Success conditions

- Requested implementation is present in the worktree.
- Relevant tests have been run and reported.
- No files are staged.
- No commit or push was performed.

### mode: `implementation-review-commit`

#### Purpose

Commit an already human-reviewed diff by staging only the approved files.

#### Allowed

- Inspect the current diff.
- Re-run relevant tests.
- Stage only explicitly approved files.
- Create a local commit.

#### Prohibited

- File editing.
- `git add .`.
- Push.
- Kanban changes.
- Runtime connection changes.
- Broadening the diff beyond the reviewed files.

#### Stop conditions

Stop immediately if any of the following occur:

- The staged target includes a file not explicitly approved.
- Tests fail.
- The worktree contains unexpected changes outside the reviewed set.
- The diff has changed since review in a way not acknowledged by the user.

#### Success conditions

- Only approved files were staged.
- Commit was created locally.
- No push was performed.
- No Kanban mutation was performed.

### mode: `push-only`

#### Purpose

Push an existing local commit from `main` to `origin/main`.

#### Allowed

- Verify `git status`.
- Verify the local commit(s) that are ahead of `origin/main`.
- Run `git push --dry-run origin main`.
- Run `git push origin main`.

#### Prohibited

- Bare `git push`.
- Push to `upstream`.
- Commit.
- File editing.
- Staging.
- Kanban changes.
- PR creation.

#### Stop conditions

Stop immediately if any of the following occur:

- The current branch is not the expected branch.
- The worktree is not clean.
- The ahead commit list contains unexpected commits.
- The dry-run indicates a target other than `origin main`.

#### Success conditions

- `origin/main..HEAD` is empty.
- `git rev-list --count origin/main..HEAD` returns `0`.
- `git status -sb` shows the branch aligned with `origin/main`.
- No upstream push or PR creation occurred.

### mode: `kanban-sync-only`

#### Purpose

Synchronize a single Kanban card with already-verified Git/artifact reality, such as marking a card done or unassigning a completed card.

#### Allowed

- Read the target card.
- Update only the target card's status and/or assignee as explicitly requested.
- Verify the target card after mutation.

#### Prohibited

- Git changes.
- File editing.
- Modifying any card other than the explicitly named target card.
- Changing the default board.
- Creating follow-up cards unless explicitly requested.

#### Stop conditions

Stop immediately if any of the following occur:

- The target card cannot be uniquely identified.
- The requested board differs from the active/default board and the command cannot explicitly target it.
- The requested mutation would affect another card.
- Git worktree is dirty when the sync depends on clean Git state.

#### Success conditions

- The target card reaches the requested safe final state.
- No other Kanban cards were changed.
- Git worktree remains clean.

### mode: `design-only`

#### Purpose

Perform read-only investigation and produce a design recommendation before implementation.

#### Allowed

- Read-only repository inspection.
- Read-only command execution.
- Create a Kanban card only if explicitly requested.
- Produce recommendation, next Story, and Test Plan.

#### Prohibited

- File editing.
- Documentation creation.
- Code implementation.
- Commit.
- Push.
- Runtime connection.
- Gateway/API/CLI exposure.
- Memory or Human Model changes.
- Kanban mutations beyond explicitly authorized card creation.

#### Success conditions

- Current state is summarized from real inspection.
- Recommended direction is stated.
- Next Story boundary is proposed.
- Test Plan is provided.
- No implementation or repository mutation occurred, except explicitly authorized Kanban card creation.

## 4. High-risk Areas

The following always require explicit human approval before modification or exposure:

- Gateway/API/CLI publication or external schema exposure.
- Broad `run_agent.py` changes.
- `prompt_builder.py` changes.
- Memory read/write integration.
- Human Model mutation.
- Decision Style implementation.
- Domain Model implementation.
- External input schema changes.
- Security, authentication, logging, or redaction changes.
- Upstream operations.
- PR creation.
- Any operation that can affect future sessions without an immediate local diff.

For these areas, prefer an additional `design-only` Story before implementation.

## 5. Standard Output Contract

Every autopilot mode should end with a report containing:

- `mode`
- Changed files
- Tests or checks executed
- `git status`
- Commit hash, if a commit was created
- Push state
- Kanban mutation state
- Blocking Issues
- Non-blocking Issues
- Next human approval needed

If the user provides a stricter output checklist, use the user's checklist while still preserving the above safety facts.

## 6. Recommended Workflow

Standard safe flow:

1. `design-only`
2. `design-doc-commit-only`
3. `push-only`
4. `implementation-no-commit`
5. `implementation-review-commit`
6. `push-only`
7. `kanban-sync-only`

When gateway/API/CLI, memory, Human Model, security/auth/logging/redaction, external schema, Decision Style, or Domain Model changes are involved, insert an additional `design-only` step before implementation.

Recommended high-risk flow:

1. `design-only`
2. `design-doc-commit-only`
3. `push-only`
4. additional `design-only` for the high-risk boundary
5. `implementation-no-commit`
6. human review
7. `implementation-review-commit`
8. `push-only`
9. `kanban-sync-only`

## 7. Practical Checklist

Before acting, identify the mode explicitly.

For local commits:

- Confirm the target repo.
- Confirm the target branch.
- Run `git status -sb`.
- Check for unexpected pre-existing changes.
- Stage exact paths only.
- Run `git diff --cached --name-only`.
- Abort if the staged list contains anything unexpected.

For pushes:

- Confirm the current branch.
- Confirm worktree is clean.
- Confirm ahead commits.
- Run dry-run first.
- Push with `git push origin main` only when that is the authorized target.

For Kanban sync:

- Use the explicit board.
- Use the explicit card id.
- Mutate only that card.
- Report whether automatic dispatcher behavior affected the card.

## 8. Non-goals

This policy does not implement automation by itself.

It does not:

- Modify code.
- Change runtime behavior.
- Change gateway/API/CLI behavior.
- Change Kanban dispatcher behavior.
- Add memory integration.
- Add Human Model behavior.
- Define Decision Style or Domain Model behavior.
- Replace human approval for high-risk operations.
