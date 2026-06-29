# Decision Framework Boundary Definition v1

## 1. Purpose

This document fixes the boundary between Human Model, Decision Framework, and Domain Models.

## 2. Responsibility Boundary

| Component | Owns | Does Not Own |
|---|---|---|
| Human Model | Understanding the person | Decision process, domain expertise |
| Decision Framework | Decision-support process | Final decision, domain-specific judgment |
| Domain Models | Specialized domain reasoning | Global person model |

## 3. Human Model Boundary

Human Model answers:

```text
What kind of person is this?
What helps this person act safely and consistently?
How should support be shaped for this person?
```

Human Model does not answer:

```text
Which investment is best?
Which career path is best?
Which medical or health action is best?
```

## 4. Decision Framework Boundary

Decision Framework answers:

```text
How should this decision be structured?
What perspectives matter?
What is the next safe step?
When should this be reviewed?
```

Decision Framework does not answer:

```text
What is the domain-correct answer?
What should the user choose?
```

## 5. Domain Model Boundary

Domain Models answer:

```text
Within this specialized domain, what facts, constraints, and tradeoffs matter?
```

Examples:

- Investment Domain handles investment-specific tradeoffs
- Career Domain handles career-specific tradeoffs
- Health Domain handles health-specific tradeoffs
- Learning Domain handles learning-specific tradeoffs

## 6. Boundary Tests

If a proposed Decision Framework behavior says:

```text
Because your Identity is X, you should buy/sell/quit/start/treat Y.
```

It violates the boundary.

A valid version is:

```text
Given your Identity and Energy, here is a lower-risk way to compare the options before deciding.
```

## 7. Review Result

No responsibility conflict is required if the boundary is enforced:

- Human Model informs
- Decision Framework structures
- Domain Models specialize
- User decides
