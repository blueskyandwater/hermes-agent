# Decision Framework Risk Register v1

## 1. Purpose

This document records architecture risks for Decision Framework Architecture Baseline v1.

## 2. Risk Register

| ID | Risk | Impact | Mitigation |
|---|---|---|---|
| R1 | Decision Framework outputs a final decision | High | Keep output contract limited to Perspective, Decision Synthesis, Next Step, Review Point. Explicitly state that the user decides. |
| R2 | Domain-specific judgment leaks into framework | High | Route Investment, Career, Health, Learning, Finance, Business, and Mental Health judgment to Domain Models. |
| R3 | Human Model becomes prescriptive | Medium | Treat Identity/Energy/Habit/Growth/Communication/Coaching as context, not commands. |
| R4 | Output contract expands too quickly | Medium | Require review before adding new output types. Prefer composing existing outputs first. |
| R5 | Decision Style is implemented prematurely | Medium | Keep Decision Style Candidate until a dedicated story validates its fields and boundary. |

## 3. Highest-Risk Failure Mode

The highest-risk failure mode is Decision Framework becoming a hidden decision-maker.

Guardrail:

```text
Decision Framework may support, synthesize, and suggest next steps.
Decision Framework must not decide.
Decision remains with the user.
```

## 4. Review Trigger

Review this risk register when any of the following happens:

- A new Decision Framework output type is proposed.
- A Domain Model is added.
- Decision Style moves from Candidate to implemented profile.
- User feedback indicates Hermes is becoming too directive.
