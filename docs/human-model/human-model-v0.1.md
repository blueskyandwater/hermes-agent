# Hermes Human Model v0.1

## 1. Purpose

Hermes Human Model v0.1 defines the highest-level long-term context Hermes can use to support the user across life domains.

Its purpose is **not** to freeze the user into a static personality record.
Its purpose is to help Hermes support better decisions, coaching, continuity, and context-aware assistance across investment, health, career, business, learning, communication, and daily life.

The Human Model sits **above** Decision Profile. It is the parent concept that organizes the durable parts of "who this person is," "how this person tends to decide," and "how Hermes should support them."

### Design goals

- Support life-wide coaching, not only task execution
- Preserve stable long-term context without overfitting to temporary states
- Keep user values separate from Hermes-added Perspective
- Keep profiles separate from operational rules, research, and transient session state
- Stay lightweight during Sprint 1: design only, no runtime changes

---

## 2. Profile List

Hermes Human Model v0.1 contains the following profiles:

- **Identity Profile**
- **Decision Profile**
- **Life Profile**
- **Health Profile**
- **Career Profile**
- **Business Profile**
- **Learning Profile**
- **Communication Profile**
- **Coaching Profile**
- **Investment Profile**

### Structure

```text
Hermes Human Model
│
├── Identity Profile
├── Decision Profile
├── Life Profile
├── Health Profile
├── Career Profile
├── Business Profile
├── Learning Profile
├── Communication Profile
├── Coaching Profile
└── Investment Profile
```

This is a conceptual structure for Sprint 1. It does not imply immediate database, memory, prompt, or code changes.

---

## 3. Responsibility of Each Profile

### Identity Profile
Defines the user’s deep personal core.

Examples:
- values
- what matters most in life
- non-negotiables
- preferred way of living
- enduring sense of self

### Decision Profile
Defines how the user tends to make decisions.

Examples:
- risk tolerance
- decision speed
- preference for reversible vs irreversible decisions
- delegation stance toward AI
- general decision posture under uncertainty

### Life Profile
Defines durable everyday-life context.

Examples:
- lifestyle patterns
- hobbies and interests
- travel orientation
- family or personal-life constraints that matter for planning
- daily rhythm when stable enough to matter long-term

### Health Profile
Defines durable health-related context that matters for support.

Examples:
- ongoing health conditions worth respecting in planning
- exercise orientation
- sleep-related tendencies
- mental load patterns worth accounting for
- treatment or care constraints that matter operationally

### Career Profile
Defines how the user wants to work and grow professionally.

Examples:
- preferred work style
- strengths
- work the user wants to avoid
- long-term career direction
- acceptable tradeoffs in work choices

### Business Profile
Defines the user’s long-term business-building context.

Examples:
- AI business direction
- monetization preferences
- solo-business or creator orientation
- productization goals
- creative/commercial balance

### Learning Profile
Defines how the user learns and improves.

Examples:
- preferred learning style
- strengths to compound
- weaknesses to support around
- continuity and habit-building style
- pace and format preferences for learning

### Communication Profile
Defines how Hermes should communicate.

Examples:
- preferred response length
- preferred tone
- directness level
- how much pushback is welcome
- formatting preferences

### Coaching Profile
Defines how Hermes should support behavior change and momentum.

Examples:
- when to encourage
- when to be firm
- when to ask questions
- when to suggest actions
- how to respond when the user is tired, stuck, or overloaded

### Investment Profile
Defines investment-specific long-term stance.

Examples:
- investment purpose
- investment horizon
- risk tolerance in investing
- funding constraints
- portfolio posture
- investment style

### Boundary note

The Human Model stores **profiles**, not operational rules.
The following are **outside** Human Model responsibility unless explicitly represented as durable profile context:

- Constitution rules
- Research facts gathered for a specific decision
- temporary emotions or short-lived moods
- short-term market opinions
- session-specific action plans

---

## 4. What to Store / What Not to Store

### Store
Store information that is:

- durable across time
- useful across multiple sessions
- meaningfully representative of the user
- relevant to support, coaching, or decision quality
- stable enough that repeated reuse is beneficial

Examples:
- enduring values
- durable constraints
- long-term goals
- stable communication preferences
- recurring coaching preferences
- long-term investment stance

### Do not store
Do **not** store information that is:

- temporary
- situational
- speculative
- generated only by Hermes
- already better represented elsewhere

Examples:
- today’s mood
- a single stressful day
- a temporary sleep issue unless it becomes an ongoing pattern
- short-lived market fear or excitement
- ad hoc research results
- one-off tactical opinions
- Hermes Perspective
- implementation plans
- task progress
- operating rules that belong in Constitution

### Guard rules

- **Perspective must not be saved into Profile.**
- **Temporary state must not be elevated into durable identity.**
- **Research findings must not be reframed as personal values.**
- **Constitution rules must not be mixed into the Human Model unless they truly describe a durable preference rather than an operational rule.**

---

## 5. Relationship to the Decision Framework

Hermes Human Model is the broader parent context.
Decision Framework is the decision-support operating structure.

### Relationship

- **Human Model** = who the user is, how the user tends to live, decide, communicate, and be coached
- **Decision Framework** = how Hermes helps the user make a specific decision well

Decision Framework currently separates:

- Decision Profile
- Perspective
- Constitution
- Research
- Decision Synthesis
- Decision (User)

Within that structure:

- **Decision Profile** is a component of the Human Model
- **Investment Profile** is both part of the Human Model and a relevant input when investment decisions are being supported
- **Perspective** remains outside the Human Model
- **Constitution** remains outside the Human Model
- **Research** remains outside the Human Model
- **Decision Synthesis** remains outside the Human Model

### Design principle

Human Model provides durable context.
Decision Framework provides decision-time organization.

They work together, but they are not the same layer.

---

## 6. How It Is Used for Coaching

The Human Model enables Hermes to behave more like a long-term life coach and thinking partner, not only a reactive assistant.

### Coaching use cases

#### 1. Better tone selection
Hermes can adjust support style based on Communication Profile and Coaching Profile.

Examples:
- shorter replies when overloaded
- firmer framing when avoidance is the pattern
- gentler tone when the user needs recovery rather than pressure

#### 2. Better prioritization
Hermes can prioritize suggestions that align with Identity Profile, Decision Profile, and Life Profile.

Examples:
- preserving long-term continuity over short-term optimization
- protecting energy when health or overload constraints matter
- preferring simple next actions over complex plans when that fits the user

#### 3. Better decision support
Hermes can interpret decisions in context instead of treating each one as isolated.

Examples:
- investment advice aligned with long-horizon stance
- career suggestions aligned with preferred work style
- business suggestions aligned with creator/independent direction

#### 4. Better continuity across domains
Hermes can connect signals across life areas without flattening them into one profile.

Examples:
- recognizing that low energy affects work, learning, and communication style
- recognizing that business choices may need to respect investment risk posture or life constraints

### Coaching limits

Human Model does not authorize Hermes to make final decisions for the user.
It improves support quality, but:

- final decisions remain with the user
- Perspective remains additive, not authoritative
- the model must be revisable as the user grows or changes

---

## 7. Future Implementation Candidates

These are future candidates only. They are **not** part of Sprint 1 implementation.

### Candidate A: Structured schema
Represent each profile with a lightweight structured schema plus freeform notes.

Possible shape:
- profile name
- scope
- durable facts
- confidence / freshness
- last reviewed date

### Candidate B: Profile-aware prompting
Load only relevant parts of the Human Model depending on task type.

Examples:
- Communication + Coaching profiles for conversation style
- Decision + Investment profiles for investment support
- Health + Life profiles for continuity planning

### Candidate C: Review cadence
Add explicit review flows so durable profiles can be revised without becoming stale.

Examples:
- quarterly profile review
- domain-specific profile refresh
- user-confirmed updates only

### Candidate D: Separation from memory layers
Map Human Model to storage intentionally rather than dumping everything into always-on memory.

Possible future split:
- compact always-on summary
- deeper per-profile storage
- explicit user-approved updates

### Candidate E: Coaching-mode integrations
Use Coaching Profile and Communication Profile to tune:
- response style
- question frequency
- firmness vs warmth
- action-vs-reflection balance

### Candidate F: Domain bridges
Allow specific profiles to inform domain frameworks without collapsing boundaries.

Examples:
- Investment Profile informing investment decision support
- Health Profile informing planning load
- Business Profile informing monetization strategy discussions

---

## 8. Sprint 1 Handling

Sprint 1 is **design only**.

### Included in Sprint 1

- define Hermes Human Model as a parent concept above Decision Profile
- define profile list
- define boundaries and responsibilities
- define relation to Decision Framework
- define coaching-oriented usage
- document future implementation candidates without building them

### Explicitly excluded from Sprint 1

- runtime implementation changes
- prompt rewiring
- memory persistence changes
- Constitution additions
- Research execution
- profile extraction automation
- cron changes
- Git push or PR creation

### Sprint 1 operating posture

Keep the design lightweight.
Do not over-specify schemas too early.
Do not create new systems before Judge, Metrics, and Quality Report are ready.

The goal of v0.1 is clarity of concepts and boundaries, not completeness.

---

## Summary

Hermes Human Model v0.1 is the parent concept for durable user understanding across life domains.
It sits above Decision Profile and coexists with the Decision Framework.

Its role is to preserve long-term context for better coaching and support while keeping clear boundaries:

- user values stay in profiles
- Hermes-added Perspective stays outside profiles
- Constitution stays as operational rules
- Research stays as fact gathering
- final decisions remain with the user

This keeps Hermes aligned with the top-level principle:

> Hermes does not exist to collect information.
> Hermes exists to improve the user’s decision quality and life support continuity.
