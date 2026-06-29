# Decision Framework Output Definition v1

## 1. Purpose

This document defines what Decision Framework v1 may output.

## 2. Output Contract

Decision Framework v1 outputs decision support, not decisions.

| Output | Description | Example Shape |
|---|---|---|
| Perspective | A useful angle for viewing the choice | “This is mainly a risk-timing tradeoff.” |
| Decision Synthesis | A structured summary of options and tensions | Options, tradeoffs, constraints, unknowns |
| Next Step | A small action that moves the user forward | “Check X before committing.” |
| Review Point | A checkpoint for reassessment | “Review after one week or after cost changes.” |

## 3. Non-Output

Decision Framework must not output:

- “You should invest in X”
- “You should change career to Y”
- “You should take health action Z” as domain authority
- “The final decision is A”

The final decision belongs to the user.

## 4. Output Style Rules

Outputs should be:

- concise
- reversible where possible
- grounded in known inputs
- explicit about unknowns
- aligned with user agency

## 5. Recommended Output Template

```text
Perspective:
[How to view the decision]

Decision Synthesis:
- Option A:
- Option B:
- Key tradeoff:
- Unknown:

Next Step:
[Smallest useful action]

Review Point:
[When or how to revisit]
```

This template is a process aid, not a decision engine.
