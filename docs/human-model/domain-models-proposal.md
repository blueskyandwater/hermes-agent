# Domain Models Proposal

## 1. Purpose

This document separates Human Model from Domain Models.

Human Model describes the person.
Domain Models describe specialized areas where the person's context is applied.

## 2. Core Rule

```text
Human Model = person-understanding model
Domain Models = specialized application models
```

Domain Models may use Human Model.
Human Model should not depend on Domain Models.

## 3. Proposed Domain Model Candidates

The following are not Human Model profiles:

- Career Domain
- Business Domain
- AI Domain
- Investment Domain
- Finance Domain
- Health Domain
- Mental Health Domain
- Learning Domain
- Travel Domain
- Lifestyle Domain
- Relationship Domain

They are Domain Models.

## 4. Domain Model Responsibility

A Domain Model may handle:

- domain-specific facts
- domain-specific constraints
- domain-specific vocabulary
- domain-specific decision inputs
- domain-specific risk considerations
- domain-specific plans and actions
- domain-specific review criteria

A Domain Model should not redefine:

- user identity
- general energy pattern
- general habit pattern
- general growth direction
- communication preferences
- coaching boundaries
- general decision style

## 5. Relationship to Human Model

Recommended direction:

```text
Human Model
↓
Decision Framework
↓
Domain Models
```

A Domain Model may ask:

- What does Identity say about this domain decision?
- What does Energy say about current capacity?
- What habits support execution?
- What growth direction gives this meaning?
- How should Hermes communicate this?
- What coaching posture is appropriate?
- What Decision Style adaptation is needed?

A Human Model profile should not ask:

- What does Investment Domain require?
- What does Career Domain require?
- What does Health Domain require?

That would create reverse dependency.

## 6. Domain Examples

### 6.1 Investment Domain

May handle:

- portfolio context
- risk exposure
- allocation rules
- asset research
- market interpretation
- investment decision support

Should reference Human Model for:

- risk posture
- long-term orientation
- information-density preference
- overtrading or overthinking signals

Should not be part of Human Model.

### 6.2 Career Domain

May handle:

- role direction
- job strategy
- compensation planning
- skill-positioning
- market opportunities

Should reference Human Model for:

- identity alignment
- energy limits
- growth direction
- communication preference

Should not be part of Human Model.

### 6.3 Health Domain

May handle:

- durable health context
- fitness constraints
- care considerations
- training constraints
- recovery plans

Should reference Human Model for:

- energy adaptation
- habit leverage
- coaching tone

Should not be part of Human Model.

### 6.4 Learning Domain

May handle:

- study path
- curriculum
- skill acquisition
- knowledge gaps
- practice plans

Should reference Human Model for:

- growth orientation
- habit patterns
- energy state
- communication density

Should not be part of Human Model.

## 7. Boundary Test

When evaluating a proposed profile, ask:

1. Does it describe the user across domains?
   - If yes, it may belong in Human Model.
2. Does it describe a specialized life/work/knowledge area?
   - If yes, it belongs in Domain Models.
3. Does it define a decision process?
   - If yes, it belongs in Decision Framework.
4. Does it evaluate output or process quality?
   - If yes, it belongs in Quality Framework.
5. Does it govern controlled improvement over time?
   - If yes, it belongs in Continuous Evolution.

## 8. Recommendation

Keep Human Model small and domain-neutral.

Recommended Human Model profile set for v0.3 review:

- Identity
- Decision Style candidate
- Energy
- Habit
- Growth
- Communication
- Coaching

Recommended Domain Model handling:

- Treat domain candidates as roadmap items, not Human Model expansion.
- Do not implement Domain Models until their owning Epic exists.
- Require every Domain Model to declare which Human Model profiles it references.
