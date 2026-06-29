# Decision Framework Dependency Diagram v1

## 1. Purpose

This document diagrams the allowed dependency direction for Human Model, Decision Framework, and Domain Models.

## 2. Approved Direction

```text
Philosophy
    ↓
Human Model
    ↓
Decision Framework
    ↓
Domain Models
    ↓
Quality Framework
    ↓
Continuous Evolution
```

## 3. Expanded View

```text
Human Model
├── Core Layer
│   ├── Identity
│   └── Decision Style [candidate, not implemented]
├── Behavior Layer
│   ├── Energy
│   ├── Habit
│   └── Growth
└── Interaction Layer
    ├── Communication
    └── Coaching
        ↓
Decision Framework Interface v1
├── Input Definition
├── Output Definition
├── Boundary Definition
├── Responsibility Comparison
└── Future Extension Note
        ↓
Domain Models
├── Career Domain
├── Business Domain
├── AI Domain
├── Investment Domain
├── Finance Domain
├── Health Domain
├── Mental Health Domain
├── Learning Domain
├── Travel Domain
├── Lifestyle Domain
└── Relationship Domain
```

## 4. Forbidden Directions

The following dependencies are not allowed:

```text
Decision Framework → modifies Human Model
Domain Models → modifies Human Model
Human Model → depends on Domain Models
Human Model → depends on Decision Framework
Domain Models → bypasses Decision Framework for user-specific decision process
```

## 5. Circular Dependency Check

| Pair | Allowed Direction | Reverse Allowed? | Result |
|---|---|---:|---|
| Human Model / Decision Framework | Human Model → Decision Framework | No | No cycle |
| Decision Framework / Domain Models | Decision Framework → Domain Models | No | No cycle |
| Human Model / Domain Models | Human Model context may flow down | No direct reverse dependency | No cycle |

## 6. Dependency Rule

Domain Models may use Human Model context only through a stable interface or decision-support context.

They should not redefine Human Model profiles.
