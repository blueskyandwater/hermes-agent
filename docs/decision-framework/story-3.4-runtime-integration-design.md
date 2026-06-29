# Story 3.4 - Decision Framework Runtime Integration Design

## Story Goal

Design how the Story 3.3 Decision Framework runtime skeleton should be integrated into the Hermes runtime later.

This story is design-only. It does not connect the Decision Framework to the runtime, prompts, memory, gateway, API, Domain Models, Decision Style, or Human Model mutation.

The preserved boundary remains:

```text
Decision Framework must not decide.
Decision remains with the user.
```

## Runtime Investigation Results

The following files were inspected read-only to identify the safest future integration boundary.

### `run_agent.py`

`run_agent.py` owns the broad `AIAgent` runtime object and high-level runtime glue. It forwards system prompt construction to the agent prompt/system-prompt layer rather than being the narrow place where per-turn decision-support context should be assembled.

Findings:

- It is too broad a runtime surface for direct Decision Framework logic.
- Direct integration here would make the `AIAgent` object responsible for decision-support input normalization and output formatting.
- That would increase coupling between the core agent runtime and a framework that should stay optional and side-effect free.

Design implication:

- Do not integrate Decision Framework directly into `run_agent.py`.
- If `run_agent.py` ever calls Decision Framework code, it should only do so through a small adapter/service boundary introduced and tested separately.

### `agent/prompt_builder.py`

`agent/prompt_builder.py` is responsible for assembling stable prompt sections such as skills, context files, and environment hints. Its functions are largely stateless and are used to build prompt text safely.

Findings:

- It is a reasonable future place for a static Decision Framework contract if Hermes needs a stable instruction block.
- It is not a good place for dynamic per-turn Decision Framework output.
- Injecting dynamic output here would risk changing system prompt content and could harm prompt-cache stability.
- It would also blur the boundary between stable prompt assembly and per-turn decision-support context.

Design implication:

- Do not integrate dynamic Decision Framework runtime output into `prompt_builder.py`.
- Keep any future use here limited to static contract text, and only if a later story explicitly approves it.

### `agent/conversation_loop.py`

`agent/conversation_loop.py` owns the live turn loop: user messages are appended, ephemeral context may be injected into the current turn, API messages are prepared, model calls happen, and tool calls are handled.

Findings:

- The natural future runtime insertion point is near per-turn user-message/context preparation, not inside system prompt assembly.
- Existing ephemeral context patterns already keep dynamic context in the current user message rather than mutating the system prompt.
- Directly calling `run_decision_framework()` from the conversation loop would still be too early because the input mapping and output formatting contract are not yet isolated.

Design implication:

- `conversation_loop.py` is the likely future consumer of a prepared Decision Framework decision-support block.
- It should not own Human Model extraction, Decision Framework input construction, or output formatting directly.
- A future integration should pass a fenced decision-support context into the current user message only after an adapter is built and tested.

### `agent/decision_framework.py`

`agent/decision_framework.py` defines the Story 3.3 runtime skeleton:

```text
DecisionFrameworkInput
DecisionFrameworkOutput
run_decision_framework()
```

Findings:

- The module is intentionally small and side-effect free.
- It accepts and normalizes allowed Human Model fields.
- It returns the minimal Decision Framework output structure.
- It does not generate final decisions, mutate Human Model state, call memory, call gateway/API, or connect to prompts.

Design implication:

- Preserve this module as the pure core contract.
- Do not add Hermes runtime dependencies to this module.
- Any future runtime integration should wrap this module rather than moving runtime concerns into it.

### `agent/tool_guardrails.py`

`agent/tool_guardrails.py` owns per-turn tool-call safety and no-progress/repeated-failure handling. Its controller can warn, block, halt, or record tool-call outcomes.

Findings:

- Tool guardrails are execution-safety logic.
- Decision Framework is decision-support context logic.
- Directly mixing these concerns would confuse user decision support with tool execution control.

Design implication:

- Do not integrate Decision Framework with tool guardrails directly.
- If a future story needs safety checks for Decision Framework injection, those checks should live at the adapter/service boundary, not in the tool guardrail controller.

## Integration Candidate Comparison

| Candidate | Summary | Responsibility separation | Side-effect risk | Human Model connection | Domain Models future connection | Decision delegation risk | Testability | Implementation size |
|---|---|---|---|---|---|---|---|---|
| A. `prompt_builder.py` integration | Add Decision Framework output or contract during prompt assembly. | Medium for static contract; poor for dynamic output. | Medium to high if dynamic output changes system prompt content. | Weak; prompt builder should not extract Human Model state. | Weak; prompt builder should not coordinate domain model inputs. | Medium; system-prompt placement can make support look like instruction/decision authority. | Medium for static text; poor for per-turn dynamic behavior. | Small initially, but risky. |
| B. `run_agent.py` integration | Call Decision Framework from the main `AIAgent` runtime surface. | Poor; `run_agent.py` is already broad runtime glue. | Medium; easy to couple framework logic to agent state. | Medium technically, but too coupled. | Medium technically, but would grow `AIAgent` responsibilities. | Medium; direct runtime integration can blur support vs decision. | Medium to poor because tests need larger runtime setup. | Small initially, but likely to sprawl. |
| C. `conversation_loop.py` integration | Inject Decision Framework output during the live turn loop. | Medium if adapter-backed; poor if direct. | Medium; per-turn insertion is safer than system prompt mutation but still runtime-sensitive. | Good if the input is prepared elsewhere. | Good if a service/adapter prepares domain-aware context later. | Low to medium if output is fenced as support context. | Good with adapter; poor if direct loop logic grows. | Medium. |
| D. Adapter layer first | Build a narrow layer that maps context into `DecisionFrameworkInput` and formats `DecisionFrameworkOutput`. | Strong; isolates mapping/formatting from runtime loop. | Low; can stay side-effect free and unconnected at first. | Strong; adapter can define the Human Model snapshot contract. | Good; adapter can later accept domain context without changing the pure core. | Low; adapter can enforce support-only language and fenced output. | Strong; can be unit-tested without live agent loop. | Small to medium. |
| E. Dedicated service layer | Create a fuller Decision Framework service for orchestration and future domain expansion. | Strong if designed well. | Low to medium depending on service responsibilities. | Strong. | Strongest for future Domain Models. | Low if contract is explicit. | Strong, but needs more surface area. | Larger than needed now. |

## Recommendation

```text
Recommend adapter layer first
```

Reasons:

- It preserves the pure-function nature of `agent/decision_framework.py`.
- It avoids placing decision-support logic directly inside `conversation_loop.py`.
- It allows Decision Framework output to be treated as decision-support context rather than a final decision.
- It lets Hermes test the connection contract before Human Model, Domain Models, or Decision Style are implemented.
- It keeps the eventual runtime integration small: the conversation loop can consume a prepared fenced block instead of owning the framework logic.

## Recommended Structure

Future integration should follow this shape:

```text
Human Model snapshot / current turn context
        ↓
Decision Framework Adapter
        ↓
DecisionFrameworkInput
        ↓
run_decision_framework()
        ↓
DecisionFrameworkOutput
        ↓
fenced decision-support context
        ↓
conversation_loop current user message injection
```

The adapter should be responsible for:

1. Accepting a Human Model snapshot and current-turn context.
2. Constructing `DecisionFrameworkInput`.
3. Calling `run_decision_framework()`.
4. Formatting `DecisionFrameworkOutput` as a fenced decision-support context block.
5. Preserving the rule that the framework supports decisions but does not make them.

The future conversation-loop integration should be responsible only for:

1. Asking the adapter for optional decision-support context.
2. Injecting that context into the current user message using an approved ephemeral-context pattern.
3. Leaving the system prompt stable.

## Non-goals

Story 3.4 does not implement or approve any of the following:

- `run_agent.py` integration
- `prompt_builder.py` integration
- `conversation_loop.py` integration
- gateway/API integration
- memory integration
- Domain Model implementation
- Decision Style implementation
- Human Model mutation
- final decision generation

## Next Stories

Recommended next Story candidates:

1. `Story 3.5 - Decision Framework Adapter`
   - Define and test the adapter that maps Human Model/current-turn context into `DecisionFrameworkInput` and formats `DecisionFrameworkOutput` as fenced support context.

2. `Story 3.6 - Human Model Input Mapping`
   - Define where the six allowed Human Model fields come from and how missing values are represented before runtime integration.

3. `Story 3.7 - Prompt Contract for Decision Support`
   - Define the exact support-only language used when Decision Framework output is injected into a model turn, including explicit final-decision prohibition.

## Implementation Status

This document records design only.

No runtime connection was implemented. No code path was changed. No Kanban state transition is required by this story note.
