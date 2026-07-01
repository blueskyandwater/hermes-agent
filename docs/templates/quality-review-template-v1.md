# Quality Review Template v1

## Purpose

This template is a review aid, not authorization.

Use it to hand a quality finding or candidate preview into human review in a consistent, minimal format.

Boundary reminders:
- review aid != authorization
- review verdict != implementation permission
- candidate preview != Kanban task creation
- report output != authorization
- quality finding != permission
- human review is required before backlog mutation
- human approval is required before implementation
- `auto_apply_allowed` is always `false` in v1
- current user instruction wins

## Review Target

- Candidate title:
- Repo:
- Branch:
- Review surface: docs-only / review-only / other:
- Related docs:
  -
  -

## Source and Evidence

### Source
- 

### Evidence
- 

### Evidence Quality Note
- direct evidence / mixed evidence / weak evidence:
- gaps or unknowns:

## Candidate Schema Alignment

Schema source of truth:
- `docs/product/continuous-evolution-v1.md` section 5.1

Checklist:
- [ ] `title`
- [ ] `summary`
- [ ] `source`
- [ ] `evidence`
- [ ] `issue_type`
- [ ] `affected_area`
- [ ] `risk_level`
- [ ] `approval_required`
- [ ] `verification_plan`
- [ ] `next_review_step`
- [ ] `auto_apply_allowed = false`

Note:
- This checklist references the schema. It does not redefine or override it.

## Boundary Checks

- [ ] candidate != authorization
- [ ] candidate preview != task creation
- [ ] review verdict != implementation permission
- [ ] quality finding != permission
- [ ] weekly report output != authorization
- [ ] human review before backlog mutation
- [ ] human approval before implementation
- [ ] no automatic Kanban mutation is implied
- [ ] no automatic runtime action is implied

## Risk and Approval Check

- Risk level:
- Approval required:
- Confirmed meaning: `approval_required` means approval is required, not already granted.
- High-risk operation note:

## Verification and Next Review Step

### Verification Plan
- 

### Next Review Step
- 

### Must Be Reviewed Before Further Action
- Before docs edit:
- Before backlog mutation:
- Before implementation:

## Explicit Non-Actions

This review does not authorize or perform the following:
- no Kanban mutation
- no task creation
- no worker dispatch
- no runtime code change
- no git add / commit / push
- no Memory / Human Model / Decision Profile mutation
- no auto-approve / auto-dispatch / auto-mutate

## Reviewer Verdict

Allowed verdicts:
- `ready for docs-only drafting`
- `needs clarification`
- `insufficient evidence`
- `not ready`

Avoid:
- `approved`
- `execute`
- `implementation allowed`
- `dispatch allowed`

Selected verdict:
- 

Reviewer note:
- 
