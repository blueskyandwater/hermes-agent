# Human Model v0.2 to v0.3 Migration Plan

## 1. Purpose

This migration plan describes how to move from Human Model v0.2 to Human Model v0.3 safely.

This is a design plan only.
It does not modify Human Model v0.2.
It does not implement new profiles or Domain Models.

## 2. Current v0.2 Baseline

Human Model v0.2 integrates six existing Story artifacts:

- Identity
- Energy
- Habit
- Growth
- Communication
- Coaching

Current flow:

```text
Identity
↓
Energy
↓
Habit
↓
Growth
↓
Communication
↓
Coaching
```

This is valid as a v0.2 integration artifact.

## 3. Target v0.3 Architecture

Target structure:

```text
Human Model
├── Core Layer
│   ├── Identity
│   └── Decision Style  [candidate, not implemented]
├── Behavior Layer
│   ├── Energy
│   ├── Habit
│   └── Growth
└── Interaction Layer
    ├── Communication
    └── Coaching
```

## 4. Migration Principles

1. **Do not rewrite v0.2 immediately**
   - v0.2 remains the accepted integration baseline until v0.3 review is accepted.

2. **Separate architecture review from implementation**
   - Decision Style is proposed, not created.
   - Domain Models are proposed, not implemented.

3. **Keep Human Model domain-neutral**
   - Investment, Career, Health, Learning, and similar areas move to Domain Models.

4. **Avoid reverse dependency**
   - Domain Models may reference Human Model.
   - Human Model should not depend on Domain Models.

## 5. Proposed Migration Steps

### Step 1: Accept v0.3 architecture review

Input:

- Human Model v0.3 Architecture Review
- Decision Style Position Proposal
- Domain Models Proposal

Output:

- Human approval that the layer structure is correct.

No implementation occurs in this step.

### Step 2: Mark Decision Style as a candidate

Input:

- Decision Style Position Proposal

Output:

- Decision Style is listed as a Human Model Core candidate.
- It is not yet a profile artifact.

Guard:

- Do not create `decision-style-profile-v1.md` in this step.

### Step 3: Add Domain Boundary Rule to future reviews

Input:

- Domain Models Proposal

Output:

- Future Human Model reviews check whether a proposed concept is actually a Domain Model.

Guard:

- Do not implement Domain Models in this step.

### Step 4: Prepare Human Model v0.3 artifact only after approval

Input:

- Accepted architecture review
- Human approval

Output:

- A future `human-model-v0.3.md` may be created.

Guard:

- `human-model-v0.3.md` should not include domain-specific profiles.
- Decision Style may appear as candidate status unless separately approved for implementation.

### Step 5: Handoff to Epic 3 Decision Framework

Input:

- Human Model v0.3 architecture
- Decision Style candidate boundary

Output:

- Epic 3 can design Decision Framework without absorbing Human Model or Domain Models.

## 6. Migration Risk Register

| Risk | Impact | Mitigation |
|---|---|---|
| Decision Style becomes Decision Framework | Human Model takes process responsibility | Keep Decision Style descriptive, not procedural |
| Growth absorbs Learning/Career | Human Model becomes domain-heavy | Keep Growth as meaning/direction only |
| Energy absorbs Health | Medical/domain leakage | Keep Energy as capacity/pacing only |
| Coaching becomes domain advisor | Hermes oversteps support role | Keep Coaching as stance, not final judgment |
| Domain Models reverse-reference into Human Model | Architecture coupling | Enforce one-way dependency: Human Model -> Domain Models |

## 7. Acceptance Criteria for v0.3 Migration

Human Model v0.3 is ready only when:

- Core / Behavior / Interaction layers are accepted.
- Decision Style candidate boundary is accepted.
- Domain Models are explicitly outside Human Model.
- Existing six profiles still have clear positions.
- No new profile implementation has been mixed into the review step.
- No domain-specific model has been created as a Human Model profile.

## 8. Recommended Next Step

Next Story should be:

> Accept or revise Human Model v0.3 Architecture Review.

After that, Epic 3 Decision Framework can proceed with a cleaner boundary.
