# Story 3.3 - Decision Framework Runtime Skeleton Design

## Story Goal

Add the minimal Decision Framework runtime skeleton for Epic 3 without connecting it to the agent loop, prompts, memory, gateway, API, or domain-specific decision logic.

The skeleton exists to preserve the accepted Decision Framework baseline in code:

- Inputs: Identity, Energy, Habit, Growth, Communication, Coaching
- Outputs: Perspective, Decision Synthesis, Next Step, Review Point
- Decision owner: the user
- Decision Style: candidate only, not v1 runtime input
- Domain Models: out of scope for this story

## Implemented Files

```text
agent/decision_framework.py
tests/agent/test_decision_framework.py
docs/decision-framework/story-3.3-runtime-skeleton-design.md
```

## Runtime Responsibility

`run_decision_framework(input_data)` is a pure, side-effect-free runtime entrypoint.

It is responsible only for:

1. Accepting `DecisionFrameworkInput` or a mapping.
2. Normalizing allowed Human Model fields into `DecisionFrameworkInput`.
3. Returning a `DecisionFrameworkOutput` that follows the v1 output contract.
4. Staying empty/minimal until future stories add approved behavior.

It does not choose for the user and does not perform specialized domain judgment.

## Input Contract

`DecisionFrameworkInput` contains exactly six Human Model fields:

```text
identity
energy
habit
growth
communication
coaching
```

Each field is a `Mapping[str, Any]` and defaults to an empty mapping.

Unknown mapping keys are ignored by the skeleton. This keeps the runtime tolerant of caller payloads while preventing candidate or domain-specific fields from becoming part of the v1 schema.

## Output Contract

`DecisionFrameworkOutput` contains exactly four decision-support fields:

```text
perspective
decision_synthesis
next_step
review_point
```

The initial skeleton returns an empty safe structure:

```python
DecisionFrameworkOutput(
    perspective="",
    decision_synthesis={
        "options": [],
        "tradeoffs": [],
        "constraints": [],
        "unknowns": [],
    },
    next_step="",
    review_point="",
)
```

The output contract intentionally excludes final-decision fields such as `decision`, `final_decision`, `recommendation`, and `domain_decision`.

## Guardrails

The Story 3.3 runtime skeleton must obey these constraints:

- Must not decide.
- Must not produce final decision.
- Must not perform domain-specific judgment.
- Must not modify Human Model.
- Must not require Decision Style.
- Must not connect to LLM prompt.
- Must not connect to memory.
- Must not connect to gateway/API.
- Must not connect to `run_agent.py`.
- Must not connect to `prompt_builder.py`.

## Non-goals

Story 3.3 does not implement:

- Domain Models
- Decision Style
- LLM prompt integration
- memory integration
- `run_agent.py` integration
- gateway/API integration
- final decision generation
- policy logic expansion
- Human Model mutation
- UI integration
- specialized domain reasoning

## Test Coverage

`tests/agent/test_decision_framework.py` covers the minimal runtime contract:

- `run_decision_framework({})` returns `DecisionFrameworkOutput`.
- `run_decision_framework(DecisionFrameworkInput())` returns `DecisionFrameworkOutput`.
- Input schema is limited to the six Human Model fields.
- Mapping input accepts the six allowed fields.
- Unknown extra keys are safely ignored.
- Decision Style is not required input.
- Output schema is limited to four fields.
- `decision_synthesis` contains `options`, `tradeoffs`, `constraints`, and `unknowns`, all lists.
- Final-decision and domain-specific fields are not present in output.

## Next Possible Story

A safe next story could add one narrow layer on top of this skeleton, for example:

```text
Story 3.4 - Decision Framework Contract Validation
```

Possible scope:

- explicit validation errors for malformed known fields
- serialization helpers if needed by a future caller
- additional tests for schema stability

Still out of scope until separately approved:

- Domain Models
- Decision Style
- LLM prompt integration
- memory integration
- gateway/API integration
- final decision generation
