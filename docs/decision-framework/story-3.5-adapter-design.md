# Story 3.5 - Decision Framework Adapter Design

## Story Goal

Design an adapter layer that preserves the pure Decision Framework runtime skeleton while preparing a future bridge from Human Model snapshot / current turn context to conversation-loop injection.

The adapter should take a Human Model snapshot and current turn context, build a `DecisionFrameworkInput`, run the Decision Framework runtime, and generate a fenced decision-support context that can later be injected into the current user message by `conversation_loop`.

This story is design-only. It does not implement the adapter or connect it to runtime message injection.

## Recommended Placement

Conclusion:

```text
agent/decision_framework_adapter.py
```

Rationale:

- Preserves the pure function nature of `agent/decision_framework.py`.
- Separates adapter responsibilities from the Decision Framework runtime skeleton.
- Allows unit testing before any `conversation_loop` integration.
- Starts smaller than converting the module into a package.

### Placement Alternatives

| Option | Assessment |
| --- | --- |
| `agent/decision_framework_adapter.py` | Recommended. Keeps runtime skeleton and adapter responsibilities separate with low implementation overhead. |
| Add adapter functions to `agent/decision_framework.py` | Not recommended. It would mix input/context normalization and prompt formatting concerns into the pure runtime skeleton. |
| Convert to `agent/decision_framework/` package | Not recommended for Story 3.5. This may become useful later, but it is unnecessary before Domain Models or Decision Style extensions exist. |

## Adapter Responsibilities

### Adapter does

- Convert Human Model snapshot into `DecisionFrameworkInput`.
- Safely receive current turn context.
- Call `run_decision_framework()` inside the adapter.
- Convert `DecisionFrameworkOutput` into fenced decision-support context.
- Treat missing inputs as empty dictionaries.

### Adapter does not

- Generate final decisions.
- Generate recommendations.
- Perform Domain Model judgment.
- Use Decision Style.
- Mutate the Human Model.
- Read from or write to memory.
- Call an LLM.
- Connect to `conversation_loop`.
- Connect to `run_agent.py`.
- Connect to `prompt_builder.py`.
- Connect to gateway/API surfaces.

## Recommended Adapter API

Keep the public API minimal: one public function is enough for Story 3.5.

```python
build_decision_support_context(
    human_model_snapshot: Mapping[str, Any] | None,
    turn_context: Mapping[str, Any] | None = None,
) -> str
```

This public function owns the full adapter flow:

```text
Human Model snapshot / current turn context
        ↓
DecisionFrameworkInput
        ↓
run_decision_framework()
        ↓
DecisionFrameworkOutput
        ↓
fenced decision-support context
```

Private helper candidates:

```python
_build_decision_framework_input(...) -> DecisionFrameworkInput
_format_decision_support_context(...) -> str
```

Reasons not to expand the public API yet:

- Future `conversation_loop` integration can use a single connection point.
- The external contract stays small.
- Internal construction and formatting can change later without breaking callers.

## Fenced Context Format

Recommended format:

```text
<decision_support_context>
This is decision support context, not a final decision.
The user remains responsible for the decision.

Perspective:
{output.perspective}

Decision Synthesis:
Options:
- ...

Tradeoffs:
- ...

Constraints:
- ...

Unknowns:
- ...

Next Step:
{output.next_step}

Review Point:
{output.review_point}
</decision_support_context>
```

Format constraints:

- Explicitly state that this is not a final decision.
- Explicitly state that the user retains decision authority.
- Include only:
  - Perspective
  - Decision Synthesis
  - Next Step
  - Review Point
- Do not include Domain judgment.
- Do not add `recommendation`, `should`, or `must` language from the adapter layer.

## Test Plan

Future implementation should add tests in:

```text
tests/agent/test_decision_framework_adapter.py
```

Verification items:

- Adapter output is fenced with `<decision_support_context>` and `</decision_support_context>`.
- Adapter output does not include final decision or recommendation language added by the adapter.
- Adapter does not invent Domain-specific terms.
- `decision_style` is not required.
- Human Model snapshot is safe when it is `None`, `{}`, or an incomplete dictionary.
- Input dictionaries are not mutated.
- `conversation_loop.py` is not changed by Story 3.5 implementation.
- `run_decision_framework()` remains pure.

## Allowed Implementation Scope for Story 3.5

If Story 3.5 later moves from design to implementation, the allowed implementation scope is:

```text
agent/decision_framework_adapter.py
tests/agent/test_decision_framework_adapter.py
```

No runtime integration is part of this story.

## Non-goals

The following are explicitly out of scope:

- `conversation_loop` integration.
- `run_agent.py` integration.
- `prompt_builder.py` integration.
- gateway/API integration.
- memory integration.
- Domain Model implementation.
- Decision Style implementation.
- Human Model mutation.
- final decision generation.
- recommendation generation.
- LLM call.
- runtime injection.

## Notes

Story 3.5 should remain a small adapter boundary. The adapter prepares future runtime integration, but it should not decide when or how to inject context into messages. That decision belongs to a later integration story.
