# Kanban Autopilot Planner Manual Prompt v1

## 1. Purpose

The Kanban Autopilot Planner Manual Prompt is not an execution mechanism.

It is a read-only operating prompt for inspecting the `hermes-product` board and the Planning documents before any dispatcher or worker automation is allowed to decide what to run next.

Its purpose is to organize:

- which cards may be candidates for the next step;
- which cards must be stopped or treated as not ready;
- which boundaries require human approval;
- which actions must not be performed by the planner.

Manual Planner output is a recommendation and safety report only. It does not authorize Kanban mutation, file mutation, Git mutation, implementation, push, dispatcher execution, or high-risk approval.

This document supports the first stage of the recommended progression:

```text
manual prompt operation -> CLI planner -> dispatcher gate
```

## 2. Inputs

The Manual Planner reads the following sources.

### Board and Git state

- `hermes-product` board
- `git status`
- `origin/main..HEAD`
- worktree dirty state

### Planning documents

- `docs/development-process/hermes-planning-system-note-v1.md`
- `docs/product/hermes-product-vision-v1.md`
- `docs/development-process/definition-of-ready-v1.md`
- `docs/product/hermes-roadmap-v1.md`
- `docs/development-process/planning-gate-policy-v1.md`
- `docs/development-process/hermes-development-autopilot-policy-v1.md`
- `docs/development-process/kanban-autopilot-rules-v1.md`

The Manual Planner should treat these inputs as evidence sources, not as permission to mutate anything.

## 3. Read-only Rule

The Manual Planner must not perform any of the following actions:

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

If a requested next step would require any of these actions, the Manual Planner must report the required human approval instead of taking the action.

## 4. Classification

The Manual Planner classifies each relevant card into one of the following readiness classes:

- `ready-for-design`
- `ready-for-design-doc`
- `ready-for-implementation-no-commit`
- `ready-for-review-commit`
- `ready-for-push`
- `ready-for-kanban-sync`
- `not-ready`
- `blocked-by-gate`
- `high-risk-needs-human`
- `backlog-never-run`
- `not-ready-for-close`

Classification is advisory. It identifies the safest next operating lane; it does not execute that lane.

## 5. Judgment Rules

The Manual Planner uses these rules when classifying cards and ranking candidates.

1. `[Backlog]` is `backlog-never-run`.
   - Backlog cards are inventory, not execution authorization.

2. `[Planning]` is limited to `ready-for-design`.
   - Planning cards may support read-only or design-only work.
   - They must not be treated as implementation work.

3. `[High-Risk]` is `high-risk-needs-human`.
   - High-risk work requires explicit human approval before any modifying action.

4. Cards without a prefix are not automatic execution targets.
   - No-prefix cards are treated conservatively as Level 0 until a human assigns a mode or prefix.

5. Implementation cards without a mode are `not-ready`.
   - A card must not be routed to implementation from title, status, or assignee alone.

6. If the Planning Gate is closed, implementation is `blocked-by-gate`.
   - Roadmap or policy existence does not by itself open the gate.

7. A `done` card with unknown artifact, commit, or push evidence is `not-ready-for-close`.
   - Kanban `done` does not prove that an artifact exists, tests passed, a commit exists, or a push happened.

8. If `origin/main..HEAD > 0`, the Planner may report a `ready-for-push` candidate.
   - The push lane must remain `push-only` and must require explicit human approval before the actual push.

9. If the worktree is dirty, the Planner may report a `ready-for-review-commit` candidate.
   - The dirty diff must be inspected before staging or committing.
   - The Manual Planner itself must not stage or commit.

10. If there are no `ready`, `running`, or reviewable cards, candidate ranking may be zero.
    - The Planner must not invent work to fill the list.

11. The Planner must not force three candidates.
    - If only one safe candidate exists, report one.
    - If no safe candidate exists, report `N/A`.

12. Blocked cards are not execution candidates.
    - They may be reported as human-decision items only.

13. A candidate must include the required mode, risk level, reason, blocked reason if any, and next human approval.

## 6. Output Format

The Manual Planner should use this output format.

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

Required fields:

- board summary
- candidate ranking
- reason
- required mode
- risk level
- blocked reason
- next human approval
- must-not-run list

If a field does not apply, use `N/A` instead of inventing evidence.

## 7. Manual Prompt Template

Use the following short prompt when manually asking Hermes to act as the Kanban Autopilot Planner.

```text
mode: planner-read-only

hermes-product boardとPlanning docsをread-onlyで確認し、次に進めてよいカード候補を最大3件出してください。

参照:
- Hermes Planning System Note v1
- Product Vision v1
- Definition of Ready v1
- Roadmap v1
- Planning Gate Policy v1
- Development Autopilot Policy v1
- Kanban Autopilot Rules v1

禁止:
Kanban変更、assignee変更、カード作成、Git操作、ファイル編集、実装、commit、push、Planning Gate変更、dispatcher実行。

出力:
board summary、candidate ranking、classification、required mode、risk level、blocked reason、must-not-run list、next human approval。
候補がなければN/Aと明記してください。
```

## 8. Current Board Lesson

The design investigation for this prompt produced the following operational lessons.

- The current board has many no-prefix cards.
- No-prefix cards should be treated as Level 0 until a human assigns a mode or prefix.
- If there are no `ready` or `running` cards, there is no automatic execution candidate.
- Blocked cards should be reported only as human-decision items, not execution candidates.
- `done` cards must not be considered truly closed without artifact, commit, push, or other required evidence.

These lessons should shape both manual operation and any future CLI planner or dispatcher gate.

## 9. Non-goals

Manual Prompt v1 does not do any of the following:

- CLI planner implementation
- dispatcher gate implementation
- prefix automatic completion
- mode automatic completion
- Kanban mutation
- High-Risk automatic approval
- gateway/API/CLI publication

It also does not authorize code implementation, runtime behavior changes, memory mutation, Human Model updates, upstream operations, PR creation, or push.

## 10. Success Criteria

Manual Prompt v1 is successful when:

1. It can be used to inspect the board and Planning docs without mutation.
2. It produces a bounded candidate ranking or `N/A` when no safe candidate exists.
3. It clearly separates ready, not-ready, blocked, backlog, high-risk, push, sync, and close-evidence cases.
4. It requires human approval at Git, Kanban, dispatcher, Planning Gate, push, and high-risk boundaries.
5. It provides a stable output format that can later be converted into a CLI planner or dispatcher gate.
