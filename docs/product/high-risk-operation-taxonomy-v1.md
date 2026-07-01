# High-risk Operation Taxonomy v1 Draft

Status: Draft  
Scope: Foundation support document  
Target: Hermes Agent product / governance documentation  
Mode: Documentation only  
Authorization: This document does not authorize execution, mutation, dispatch, push, or deployment.

---

## 1. Purpose

High-risk Operation Taxonomy v1 defines a shared risk vocabulary for Hermes operations.

Its purpose is to make high-impact actions visible before they happen.
It classifies operations by blast radius, reversibility, persistence, external exposure, and required approval level.

This document is intended to be referenced by:

- Planning Gate Policy
- Worker Architecture
- Quality Framework
- Implementation Readiness Review
- Continuous Evolution
- Improvement Backlog
- Weekly Quality Report
- future runtime guardrails, if explicitly approved later

The taxonomy exists to answer practical questions:

- Is this operation low, medium, high, or critical risk?
- Does it mutate durable state?
- Does it affect external users or services?
- Does it require current explicit user approval?
- What verification is required before and after execution?
- What rollback or recovery expectation should exist?

Core principle:

> High-risk operation requires current explicit approval.

Past preference, memory, backlog entries, roadmap sequence, readiness review, quality findings, and worker confidence are all context.
They are not permission.

---

## 2. Scope

This document covers risk classification for Hermes-related operations, including:

- Git operations
- push / merge / branch publication
- Kanban mutation
- task status changes
- worker dispatch
- dispatcher behavior
- cron creation or modification
- Memory mutation
- Human Model mutation
- Decision Profile mutation
- external gateway changes
- API / CLI surface changes
- CI and workflow reruns
- Constitution / Gate rule changes
- Quality scorecard changes
- suppression or bypass behavior
- runtime code changes that affect user-facing behavior
- operations with broad persistence or external blast radius

The taxonomy applies to both human-initiated and AI-assisted operations.

It applies before execution, not after damage is done.

---

## 3. Non-goals

This document does not:

- approve any operation
- create a task
- complete a task
- mutate Kanban state
- mutate Memory
- mutate the Human Model
- mutate the Decision Profile
- change Constitution rules
- change Planning Gate behavior
- change Quality Framework behavior
- change runtime code
- dispatch a worker
- create or update cron jobs
- rerun CI workflows
- push to any remote
- create PRs
- define implementation details for enforcement
- replace user instruction

This is a classification document only.

A risk label is not an approval token.

---

## 4. Risk level model

Hermes operations are classified into four risk levels:

1. Low
2. Medium
3. High
4. Critical

Risk level is determined by these dimensions:

| Dimension | Question |
| --- | --- |
| Persistence | Does the operation write durable state? |
| Reversibility | Can it be safely undone? |
| Blast radius | Who or what can be affected? |
| External surface | Does it affect users, channels, APIs, gateways, or services? |
| Automation | Can it run repeatedly or without attention? |
| Authorization sensitivity | Could it bypass the user's current intent? |
| Trust impact | Could it corrupt memory, profile, policy, or decision support? |
| Operational impact | Could it interrupt service, tasks, sessions, or workflows? |
| Publication impact | Does it publish code, docs, messages, artifacts, or notifications? |
| Security impact | Does it affect secrets, permissions, auth, or access paths? |

If dimensions disagree, use the higher risk level.

Examples:

- A small file edit can be low risk if local and reversible.
- The same edit becomes high risk if it changes runtime governance.
- A read-only command is usually low risk.
- A read-only command against sensitive external systems may be medium if it exposes data.
- A cron job that silently mutates state is high or critical depending on blast radius.

Conservative rule:

> When unsure, classify upward and require explicit approval.

---

## 5. Low / medium / high / critical operations

### Low-risk operations

Low-risk operations are normally local, read-only, reversible, and narrow.

Examples:

- reading files
- checking `git status`
- checking `git diff`
- running `git diff --check`
- reading logs
- listing local branches
- inspecting untracked documentation files
- validating markdown formatting without mutation
- running non-mutating tests
- generating local draft content when explicitly requested

Low-risk operations may proceed when they are clearly within the current request.

Low risk does not mean no discipline.
It still requires scope awareness.

### Medium-risk operations

Medium-risk operations may change local state or consume resources, but have limited blast radius and clear recovery.

Examples:

- creating a new local documentation file at an explicitly requested path
- editing a specified local file
- running targeted tests that write caches
- installing local development dependencies in an isolated environment
- creating local temporary files
- staging exact files when explicitly authorized
- creating local commits when explicitly authorized

Medium-risk operations require:

- explicit scope
- bounded path or target
- verification
- no hidden escalation

### High-risk operations

High-risk operations affect durable state, automation, external surfaces, user-facing behavior, or project governance.

Examples:

- pushing to a remote branch
- creating or merging PRs
- mutating Kanban task status
- dispatching workers
- changing dispatcher behavior
- creating or modifying cron jobs
- changing gateway configuration
- restarting user-facing services
- mutating Memory / Human Model / Decision Profile
- changing Constitution or Planning Gate rules
- changing Quality Framework scorecards
- suppressing quality violations
- rerunning workflows with side effects
- modifying runtime code that controls execution permissions

High-risk operations require current explicit approval.

### Critical operations

Critical operations can cause broad, hard-to-reverse, externally visible, security-sensitive, or autonomous changes.

Examples:

- deleting data
- rewriting git history
- force-pushing
- changing production credentials or secrets
- rotating tokens
- changing external gateway routing for live users
- deploying autonomous mutation behavior
- enabling cron jobs that mutate governance state
- altering approval rules to reduce friction without review
- disabling safety gates
- broad memory rewrite
- mass task mutation
- automated worker dispatch from unreviewed findings
- publishing upstream changes without explicit approval

Critical operations require explicit current approval, strong verification, and rollback planning.
Some critical operations may be disallowed entirely unless separately designed.

---

## 6. Git operation risk

Git operations vary greatly in risk.

### Low-risk Git operations

- `git status -sb`
- `git diff -- <path>`
- `git diff --check`
- `git log --oneline -n N`
- `git branch --show-current`
- `git rev-parse --short HEAD`
- `git remote -v`
- `git diff --no-index -- /dev/null <new-file>` for untracked file proof

These are observational.
They do not mutate repository state.

### Medium-risk Git operations

- writing a requested local docs file
- `git add <exact-path>` when staging is explicitly approved
- local commit to a named branch when explicitly approved
- creating a local branch
- applying a patch to specified files

These mutate local state.
They require exact scope and verification.

### High-risk Git operations

- `git push origin main`
- pushing any branch
- creating a PR
- merging a PR
- changing remote tracking state
- creating tags
- rerunning release workflows via GitHub
- updating generated artifacts that are consumed by CI or release

These affect remote state, external visibility, or downstream workflows.
They require current explicit approval.

### Critical Git operations

- force push
- history rewrite on shared branch
- deleting remote branches or tags
- changing upstream remotes
- pushing to upstream repository
- creating upstream PRs when the user forbids upstream PRs
- publishing secrets

Critical Git operations should be treated as blocked unless explicitly approved with exact command, target, and recovery plan.

Core principle:

> Ready does not mean push-approved.

A clean status, passing tests, or successful readiness review does not authorize push.

---

## 7. Kanban mutation risk

Kanban state represents durable work coordination.
Changing it can alter what workers do next.

### Low-risk Kanban operations

- read-only task listing
- read-only task show
- reading comments
- reading task links
- reading board stats

These remain low risk only if no mutation occurs.

### High-risk Kanban operations

- creating tasks
- assigning tasks
- changing task status
- marking tasks complete
- blocking or unblocking tasks
- linking or unlinking tasks
- adding authoritative comments that change work interpretation
- dispatching a task
- changing task priority
- archiving tasks

These require explicit current approval.

### Critical Kanban operations

- mass mutation
- automated task creation from reports
- automated completion from worker self-report
- automated re-dispatch loops
- deleting or archiving large task sets
- changing board routing rules

Core principle:

> Backlog is inventory, not authorization.

The existence of a Kanban task does not authorize execution, completion, dispatch, or mutation outside the current user instruction.

---

## 8. Memory / Human Model / Decision Profile mutation risk

Memory and profile systems influence future behavior.
They require special caution.

### Low-risk operations

- reading current memory when relevant
- inspecting whether a fact exists
- summarizing known memory without mutation
- identifying candidate facts for user review

### High-risk operations

- adding memory
- replacing memory
- removing memory
- updating Human Model artifacts
- updating Decision Profile artifacts
- updating user preference records
- storing project assumptions as durable truth
- storing temporary task state as durable fact

### Critical operations

- broad memory rewrite
- automatic memory mutation from quality reports
- automatic Human Model mutation from behavioral inference
- automatic Decision Profile mutation from a single decision
- deleting large memory sections
- treating inferred traits as confirmed identity

Core principles:

> Memory is context, not authorization.  
> Human Model supports the user, not defines the user.  
> Decision Profile is soft guide, not policy.

Memory can reduce repeated explanation.
It cannot approve action.

Human Model can help adapt support.
It must not freeze the user into a label.

Decision Profile can guide tradeoffs.
It must not override current user instruction.

---

## 9. Worker / Dispatcher / Cron risk

Workers, dispatchers, and cron jobs introduce automation.
Automation increases risk because actions may happen outside the user's immediate attention.

### Worker risk

Low-risk worker behavior:

- read-only analysis inside a clearly scoped task
- producing a draft report
- returning a summary without mutation

High-risk worker behavior:

- editing files
- committing changes
- mutating Kanban
- calling external APIs
- starting long-running services
- changing runtime settings
- creating downstream tasks

Critical worker behavior:

- self-escalating scope
- self-approving high-risk actions
- dispatching other workers without approval
- changing its own permission model
- mutating governance docs as runtime policy

Core principle:

> Worker cannot self-escalate.

### Dispatcher risk

High-risk dispatcher behavior:

- claiming tasks
- launching workers
- retrying failed tasks
- changing routing behavior
- auto-blocking or auto-unblocking

Critical dispatcher behavior:

- approving tasks
- interpreting reports as permission
- bypassing Planning Gate
- launching workers from quality findings without human approval

Core principle:

> Dispatcher cannot approve.

Dispatcher may route only within approved rules.
It cannot grant permission.

### Cron risk

Cron jobs can repeat actions without immediate visibility.

Low-risk cron behavior:

- local report generation
- read-only monitoring
- non-mutating summaries

High-risk cron behavior:

- sending external notifications
- running workflow reruns
- mutating files
- mutating Kanban
- mutating memory
- dispatching workers
- changing configuration

Critical cron behavior:

- silently governing behavior
- auto-changing Constitution rules
- auto-suppressing quality findings
- auto-creating improvement tasks
- auto-deploying changes

Core principle:

> Cron must not silently govern.

Scheduled reporting is acceptable when explicitly configured.
Scheduled mutation requires explicit design and approval.

---

## 10. External surface / Gateway / API / CLI risk

External surfaces can affect users, channels, integrations, and live workflows.

### External surface examples

- Discord gateway
- Slack gateway
- Even AI gateway
- API server
- webhook receivers
- CLI commands exposed to users
- scheduled delivery targets
- notification systems
- external cloud services
- GitHub Actions
- OpenRouter / model provider configuration

### Low-risk operations

- reading gateway logs
- checking service status
- inspecting configuration without secrets
- running local CLI help
- reading API route definitions

### Medium-risk operations

- writing local docs about external behavior
- running local CLI smoke tests that do not mutate state
- validating configuration schema without applying changes

### High-risk operations

- restarting gateway services
- changing gateway routing
- changing platform home channels
- changing webhook subscriptions
- changing API behavior
- changing CLI command behavior
- sending messages to external channels
- deploying new external behavior
- changing provider routing

### Critical operations

- exposing secrets
- changing auth flows
- breaking message routing
- enabling public endpoints without review
- sending bulk external notifications
- changing production gateway behavior without explicit approval

Core principle:

> External surface has high blast radius.

Even small changes can affect real users or live automation.

---

## 11. CI / workflow rerun risk

CI and workflows can consume resources, publish results, deploy artifacts, or trigger downstream jobs.

### Low-risk CI operations

- reading workflow files
- reading workflow status
- reading logs
- checking local test commands
- inspecting skipped workflow results

### Medium-risk CI operations

- running local tests
- running local linters
- generating local coverage artifacts

### High-risk CI operations

- rerunning GitHub Actions workflows
- dispatching workflows manually
- modifying workflow files
- changing CI gates
- changing branch protection assumptions
- changing release job behavior

### Critical CI operations

- rerunning deployment workflows
- changing secrets used by CI
- disabling required checks
- suppressing failures without review
- publishing release artifacts

Core principle:

> A workflow rerun is an action, not observation.

Reruns require explicit approval when they consume remote resources, publish status, or trigger downstream behavior.

---

## 12. Constitution / Gate rules / Quality scorecard change risk

Governance artifacts influence future behavior.
Changing them can silently alter how Hermes acts.

### Low-risk operations

- reading Constitution text
- reading Planning Gate docs
- reading Quality Framework docs
- summarizing current rules
- identifying unclear areas

### Medium-risk operations

- drafting proposed documentation changes in a specified file
- creating review-only candidate text
- adding open questions

### High-risk operations

- changing Constitution text
- changing Planning Gate rules
- changing Quality scorecards
- changing evaluation criteria
- changing thresholds
- changing enforcement language
- changing approval requirements

### Critical operations

- automatically changing rules based on one report
- removing approval requirements
- weakening gates without review
- making report findings self-executing
- embedding hidden exemptions

Core principle:

> Current user instruction wins.

Governance docs guide behavior only within the current instruction and explicit authorization boundaries.
They do not override the user.

---

## 13. Quality suppress behavior risk

Quality suppress behavior means hiding, ignoring, downgrading, or automatically resolving quality concerns.

This is high risk because it can erase evidence before the user reviews it.

### Examples of quality suppress behavior

- marking violations as resolved without human review
- hiding repeated issues from reports
- removing failed examples from benchmarks
- lowering severity to improve scores
- changing scorecards to avoid failures
- suppressing warnings from Weekly Quality Report
- treating lack of evidence as pass
- auto-closing improvement candidates

### High-risk suppress behavior

- suppression of known findings
- changing thresholds after a bad result
- filtering reports without recording the filter
- making exceptions without user approval

### Critical suppress behavior

- permanent suppression of safety violations
- automatic rule weakening
- deletion of quality history
- disguising regression as improvement
- suppressing evidence before review

Core principle:

> Quality finding is evidence, not permission.

Quality findings may justify investigation.
They do not authorize mutation.

---

## 14. Approval requirements by risk level

| Risk level | Approval requirement | Notes |
| --- | --- | --- |
| Low | May proceed if clearly within current request | Must remain read-only or non-mutating. |
| Medium | Requires explicit scoped request | Path, repo, branch, and operation should be clear. |
| High | Requires current explicit approval | Past memory, backlog, or readiness is insufficient. |
| Critical | Requires explicit current approval plus recovery plan | Some operations may remain blocked even with broad approval. |

Approval must be:

- current
- explicit
- scoped
- understandable
- tied to a concrete operation
- not inferred only from memory
- not inferred only from prior preference
- not inferred only from backlog existence
- not inferred only from worker confidence
- not inferred only from quality score

Examples of insufficient approval:

- "We usually push weekly"
- "The task exists in Kanban"
- "The report found an issue"
- "The readiness review says ready"
- "The worker says it is done"
- "The user previously liked this pattern"
- "The roadmap lists this next"

Examples of better approval:

- "Run `git push --dry-run origin main`, then `git push origin main` if dry-run succeeds."
- "Create only this Kanban task with this title and owner."
- "Update this one memory entry with this exact fact."
- "Rerun this named workflow once."

---

## 15. Mode requirements by risk level

Mode should match risk.

### Low-risk mode

Recommended modes:

- read-only-review
- inspect-only
- status-check
- diff-check
- docs-preview

Allowed behavior:

- observe
- report
- summarize
- validate

Disallowed behavior:

- mutation unless separately authorized

### Medium-risk mode

Recommended modes:

- docs-only-no-commit
- local-edit-only
- targeted-test-only
- local-commit-no-push when explicitly approved

Allowed behavior:

- create or edit specified local files
- run local verification
- report status

Disallowed behavior:

- push
- PR
- Kanban mutation
- memory mutation
- runtime integration
- worker dispatch

### High-risk mode

Recommended modes:

- push-only
- kanban-mutation-approved
- cron-change-approved
- gateway-change-approved
- memory-update-approved
- workflow-rerun-approved

Allowed behavior:

- only the specifically approved operation
- exact target only
- verification before and after

Disallowed behavior:

- adjacent improvements
- opportunistic cleanup
- scope expansion
- broad automation

### Critical-risk mode

Recommended mode:

- explicit-critical-operation-review

Required before execution:

- exact target
- exact command or procedure
- impact explanation
- rollback or recovery plan
- confirmation of no safer alternative
- explicit current approval

Critical mode should be rare.

---

## 16. Verification requirements by risk level

### Low-risk verification

- show command output or file path inspected
- distinguish fact from inference
- report if no mutation occurred

### Medium-risk verification

- show created or changed path
- show `git status -sb` when in repo
- show relevant diff or no-index diff for untracked file
- run format or whitespace check when applicable
- state no commit / push if not authorized

### High-risk verification

Before execution:

- confirm repo / branch / target
- confirm current state
- confirm exact command or operation
- confirm authorization is current
- run dry-run when available

After execution:

- show final state
- show success output
- show remaining delta
- show no extra operations occurred
- show rollback status if relevant

### Critical verification

Before execution:

- capture baseline
- confirm backups or recovery path
- verify target identity
- verify blast radius
- verify approval
- require human-readable go/no-go point

After execution:

- verify primary success
- verify secondary side effects
- verify no unexpected scope expansion
- verify recoverability remains understood
- document exact evidence

---

## 17. Rollback / recovery expectations

Rollback planning depends on risk level.

| Risk level | Recovery expectation |
| --- | --- |
| Low | Usually no rollback needed; confirm no mutation. |
| Medium | Local revert should be obvious. Keep changes scoped. |
| High | Recovery path should be known before execution. Dry-run when possible. |
| Critical | Recovery plan should be explicit before execution. Backup or restore path may be required. |

Examples:

- Local docs edit: delete or patch the file.
- Local commit: revert commit or reset if still local and explicitly approved.
- Push: revert with new commit; do not rewrite shared history without approval.
- Kanban mutation: record previous state before mutation where possible.
- Memory mutation: record old text before replace/remove.
- Cron mutation: list job before change and verify after change.
- Gateway change: capture previous config and avoid restart unless explicitly approved.

Recovery must not be improvised after unauthorized mutation.

---

## 18. Dangerous examples

### Example 1: Readiness becomes push

Dangerous chain:

1. Readiness Review says a docs change is ready.
2. Agent commits it.
3. Agent pushes it because branch is ahead.

Why dangerous:

- readiness is not authorization
- ready does not mean push-approved
- push changes remote state

Correct behavior:

- report readiness
- wait for explicit push instruction

### Example 2: Quality finding becomes Kanban task

Dangerous chain:

1. Weekly Quality Report finds repeated issue.
2. Agent creates improvement task automatically.
3. Dispatcher assigns worker.

Why dangerous:

- quality finding is evidence, not permission
- improvement candidate is not authorization
- dispatcher cannot approve

Correct behavior:

- list candidate for human review
- no task creation without explicit approval

### Example 3: Memory inference becomes durable truth

Dangerous chain:

1. User makes a tired comment.
2. Agent infers stable preference.
3. Agent updates Human Model.

Why dangerous:

- one moment is not stable identity
- Human Model supports user, not defines user
- memory mutation needs care

Correct behavior:

- treat as session context unless durable and useful
- ask or wait for explicit memory instruction when uncertain

### Example 4: Worker self-escalates

Dangerous chain:

1. Worker is assigned read-only review.
2. Worker edits files to fix issues.
3. Worker marks task complete.

Why dangerous:

- worker cannot self-escalate
- read-only mode forbids mutation
- task completion is Kanban mutation

Correct behavior:

- report findings only
- wait for explicit execution instruction

### Example 5: Cron silently governs

Dangerous chain:

1. Cron report detects score drop.
2. Cron updates scorecard threshold.
3. Future reports look better.

Why dangerous:

- cron must not silently govern
- quality suppress behavior hides evidence
- rule changes require human review

Correct behavior:

- report regression candidate
- no automatic scorecard mutation

### Example 6: Gateway restart interrupts user

Dangerous chain:

1. Agent changes config.
2. Agent restarts gateway from Discord session.
3. Current conversation is interrupted.

Why dangerous:

- external surface has high blast radius
- restart may disrupt active chat
- user preference may require manual restart

Correct behavior:

- provide command for user to run if restart is needed
- do not restart without explicit current approval

---

## 19. Relationship with Planning Gate

Planning Gate uses this taxonomy to decide whether an operation can proceed.

The taxonomy supplies risk classification.
Planning Gate supplies go/no-go checks.

Planning Gate should ask:

- Is the requested operation clearly defined?
- What risk level applies?
- Does the current mode allow this risk level?
- Is approval current and explicit?
- Is the target scoped?
- Is read-only verification needed first?
- Is rollback understood?

This taxonomy does not replace Planning Gate.
It gives Planning Gate a shared vocabulary.

Core principle:

> Planning Gate prevents premature action.

---

## 20. Relationship with Worker Architecture

Worker Architecture defines role boundaries.
This taxonomy defines risk boundaries.

Workers should not use role confidence as permission.

A worker may be capable of doing something and still not be authorized to do it.

Worker Architecture should use this taxonomy to determine:

- which operations workers may perform by default
- which operations require planner approval
- which operations require direct user approval
- which operations should remain impossible for workers
- how dispatcher behavior should be constrained

Important boundaries:

- Worker cannot self-escalate.
- Dispatcher cannot approve.
- Worker output is evidence, not completion proof by itself.
- Worker success does not authorize Kanban completion unless explicitly allowed.

---

## 21. Relationship with Implementation Readiness Review

Implementation Readiness Review checks whether work is ready to implement.
This taxonomy checks risk class and approval requirements.

Readiness Review should reference this taxonomy when answering:

- Is implementation local-only or externally visible?
- Does the work mutate durable state?
- Does it affect governance behavior?
- Does it require push, workflow rerun, or service restart?
- Does it require memory or profile mutation?
- Does it need rollback planning?

Readiness means the scope is understandable.
It does not authorize execution.

Core principle:

> Implementation readiness is review, not authorization.

---

## 22. Relationship with Quality Framework

Quality Framework evaluates behavior.
This taxonomy classifies actions that may follow from evaluation.

Quality Framework may detect:

- repeated issue
- regression candidate
- process violation
- safety boundary breach
- missing verification
- over-broad action

Those findings are evidence.
They may support improvement review.
They do not authorize mutation.

Quality Framework should use this taxonomy to avoid these failures:

- auto-suppressing findings
- auto-changing scorecards
- auto-creating tasks
- auto-mutating rules
- auto-dispatching workers
- treating score improvement as permission

Core principle:

> Quality Framework evaluates behavior, not the user.

And:

> Quality finding is evidence, not permission.

---

## 23. Open questions

The following questions remain open for future review:

1. Should Hermes define a machine-readable risk registry later?
2. Should CLI commands declare their risk class explicitly?
3. Should worker profiles have static maximum risk levels?
4. Should cron jobs require declared mutation capability at creation time?
5. Should Quality Reports tag findings by risk class?
6. Should Memory / Human Model updates require a separate approval phrase?
7. Should gateway restarts have a dedicated manual-only policy?
8. Should workflow reruns be classified differently for test-only vs deploy workflows?
9. Should critical operations require two-step confirmation in all gateway contexts?
10. Should this taxonomy become a runtime guard only after docs stabilize?

Open questions are not permission to implement.
They are future review items.

---

## 24. Next recommended task

Recommended next Foundation support document:

`docs/product/foundation-docs-index-v1.md`

Purpose:

- provide a compact index of all Foundation docs
- list each document's role in one paragraph
- distinguish guide, review, report, inventory, and taxonomy documents
- make clear which docs authorize nothing
- help future implementation tasks find the right prerequisite docs quickly

This next task should remain docs-only unless explicitly changed by the user.

---

## Summary principles

- High-risk operation requires current explicit approval.
- Past preference is context, not current approval.
- Memory is context, not authorization.
- Backlog is inventory, not authorization.
- Ready does not mean push-approved.
- Worker cannot self-escalate.
- Dispatcher cannot approve.
- Cron must not silently govern.
- Quality finding is evidence, not permission.
- External surface has high blast radius.
- Mutation must be explicit, scoped, reviewable, and reversible where possible.
