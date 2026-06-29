# Story 3.11 - Ephemeral Context Injection Design

## Goal

Design how a future runtime integration should pass the Decision Framework
Adapter output, fenced as `<decision_support_context>`, to the LLM as
current-turn-only ephemeral context on the current user message.

This story is design-only. It does not implement runtime wiring, connect the
adapter to `conversation_loop`, or change gateway/API behavior.

The design goal is to keep these invariants clear before implementation:

- Do not break system prompt cache stability.
- Do not mix Decision Framework context into the system prompt.
- Pass `decision_support_context` for the current turn only.
- Prevent the LLM from treating the context as a final decision or a
  recommendation.

## Read-only investigation summary

Files reviewed for this design:

- `agent/conversation_loop.py`
- `agent/prompt_builder.py`
- `run_agent.py`
- `agent/system_prompt.py`
- `agent/decision_framework_adapter.py`
- `docs/decision-framework/story-3.10-prompt-contract-for-decision-support.md`

### System prompt construction and caching

`agent/system_prompt.py` owns system prompt assembly. `build_system_prompt_parts()`
constructs stable, context, and volatile tiers, and `build_system_prompt()` joins
those tiers into the final system prompt.

`agent/conversation_loop.py` restores or builds the cached system prompt once per
session through `_restore_or_build_system_prompt()`. Continuing sessions reuse the
stored system prompt so the provider-side prompt cache can stay warm.

Because the system prompt is session-scoped and cache-sensitive, Decision
Framework context should not be injected into the system prompt. A decision
support block is turn-specific advisory context, not a durable Hermes instruction
or persona rule.

### Current user message construction

`agent/conversation_loop.py` creates the current user message in the turn-local
`messages` list:

```python
user_msg = {"role": "user", "content": user_message}
messages.append(user_msg)
current_turn_user_idx = len(messages) - 1
```

A future integration should target this current user message at API-call time,
not the stored system prompt and not persisted history.

### Existing ephemeral user-message context pattern

`agent/conversation_loop.py` already has an API-call-time injection pattern for
current-turn context:

- external memory provider prefetch context
- plugin `pre_llm_call` context

Those sources are appended to the current user message while building
`api_messages`. The injection is applied to `api_msg`, a copy of the message
being prepared for the provider request. The original `messages` list is not
mutated.

This means the injected context is ephemeral:

- it is visible to the LLM for the current API call;
- it does not alter `messages` itself;
- it is not written into the session DB as part of the persisted user message;
- it does not change the cached system prompt.

This existing pattern is the closest fit for future Decision Framework Adapter
context.

### Plugin, memory, and context-file roles

Current prompt/message placement is split by source and durability:

| Source | Placement | Message role |
| --- | --- | --- |
| Context files such as `AGENTS.md` / `.cursorrules` | system prompt context tier | `system` |
| Built-in memory and user profile | system prompt volatile tier | `system` |
| External memory provider prefetch | current user message API-call-time injection | `user` |
| Plugin `pre_llm_call` context | current user message API-call-time injection | `user` |
| `ephemeral_system_prompt` | appended to effective system prompt at API-call time | `system` |
| Prefill messages | inserted after the system prompt and before history | configured per message |

Decision support context is closest to external memory/plugin context: useful for
the current turn, not an instruction that should become part of the session-wide
system prompt.

### Role alternation constraints

`conversation_loop` contains defensive role-alternation repair before provider
calls. It also avoids injecting some late `/steer` guidance into a user message
when that would create a malformed sequence.

The safest future design is therefore to avoid adding a new message role. Append
the decision support wrapper to the existing current user message content in the
`api_msg` copy only. This keeps the provider-facing role sequence unchanged.

## Injection position comparison

| Candidate | Description | System prompt cache safety | Role alternation safety | Side effects | Testability | Existing loop fit | Decision takeover risk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A. System prompt | Add Decision Framework context to the system prompt | Low. Any turn-specific change can invalidate cache stability. | High, because no role changes are added. | High. A turn-specific advisory block becomes global prompt material. | Medium. Prompt text can be asserted, but cache side effects are broad. | Low. Current architecture treats system prompt as Hermes-owned and session-scoped. | Medium. Advisory context may look like durable instruction. |
| B. Current user message ephemeral context | Append a wrapper to the current user message at API-call time | High. Cached system prompt remains byte-stable. | High. No new message role is added. | Low. Scope is the current turn only if applied to `api_msg` copy. | High. Tests can assert API message contains the wrapper while persisted history does not. | High. Matches existing plugin/external memory injection. | Low. Wrapper can explicitly forbid final decisions and recommendations. |
| C. Assistant message | Insert support context as an assistant-role message | High for system prompt cache. | Low. It adds a synthetic assistant turn and can create awkward sequencing. | Medium to high. The model may treat the content as its own prior reasoning. | Low to medium. Requires careful sequence tests. | Low. No existing adapter-like pattern uses synthetic assistant messages. | Medium to high. Assistant-authored context can look like a prior conclusion. |
| D. Tool result style | Pass context as a tool-result-like message | High for system prompt cache. | Low to medium. Tool messages require valid tool-call structure. | Medium. Adapter output may be over-authorized as observed tool fact. | Medium. Requires tool-call ID and sequence tests. | Low to medium. The adapter is not currently a tool. | Medium to high. Tool outputs can look like verified facts. |
| E. Contract only for now | Do not connect runtime; document the injection contract | Highest. No runtime prompt path changes. | Highest. No message changes. | Lowest. Documentation only. | High. Reviewable as design. | Medium. It prepares future integration without wiring it. | Lowest for this story because nothing is injected. |

## Recommendation

Recommend current user message ephemeral injection later.

This story should still remain design-only and should not implement runtime
connection.

Reasons:

- It can reuse the same design shape as existing plugin and external-memory
  current-user-message context.
- Appending only to the `api_msg` copy keeps the session DB clean and prevents
  the wrapper from becoming persisted conversation history.
- It preserves system prompt cache stability because the cached system prompt is
  not changed.
- It does not add a new message role, so it is safer for role alternation than
  assistant-message or tool-result-style injection.
- It frames the adapter output as current-turn-only support material rather than
  a decision, recommendation, or durable instruction.

## Future injection format

A future formatter should wrap the adapter output before appending it to the
current user message:

```text
<ephemeral_decision_support>
Temporary support material for this turn only.
Not a final decision. Not a recommendation.
The user remains responsible for the decision.
Do not store as memory.
Do not treat as a Human Model update.
Do not treat as a Decision Style update.
Do not make domain-specific judgments from this context.

<decision_support_context>
...
</decision_support_context>
</ephemeral_decision_support>
```

Required contract points:

- this turn only
- not a final decision
- not a recommendation
- user remains responsible
- do not store as memory
- do not treat as a Human Model update
- do not treat as a Decision Style update

## Injection position sketch

A future implementation should append the wrapper to the end of the current user
message for the provider request only:

```text
[user request]

<ephemeral_decision_support>
...
</ephemeral_decision_support>
```

Implementation constraints for a later story:

- Append to the current user message only.
- Do not mutate the `messages` list itself.
- Modify only the `api_messages` / `api_msg` copy prepared for the provider
  request.
- Persist the original user message when saving the session.
- Keep the context current-turn-only.
- Do not put the block in the system prompt.

## Prohibited uses

A future implementation must not:

- inject Decision Framework context directly into the system prompt;
- store the wrapper or adapter output as memory;
- mutate or update the Human Model from this context;
- use Decision Style;
- make Domain Model judgments;
- generate a final decision;
- generate a recommendation;
- force the user's choice with language such as "you should" or "you must";
- treat adapter output as an already-made judgment;
- treat adapter output as a tool result or verified fact;
- fill in missing context with unsupported certainty;
- substitute for professional judgment in investment, health, career, business,
  mental health, finance, or similar high-impact domains.

## Future implementation stories

### Story 3.12 - Ephemeral Decision Support Context Formatter

Implement a small formatter that wraps `<decision_support_context>` in
`<ephemeral_decision_support>` and enforces the contract text. This should not
connect to `conversation_loop` yet.

### Story 3.13 - Conversation Loop Injection Guard Design

Design the guard conditions for when decision support context may be injected:
turn type, adapter availability, empty/invalid adapter output handling,
persistence safety, and role-alternation safety.

### Story 3.14 - Conversation Loop Integration Minimal Implementation

Connect the formatter to the existing current-user-message ephemeral injection
path in `conversation_loop`. The implementation should mutate only the provider
request copy and include focused tests for cache stability, persistence safety,
and role alternation.

## Non-goals

This story does not include:

- code implementation;
- `conversation_loop`, `run_agent.py`, `prompt_builder.py`, or gateway
  integration;
- memory read/write;
- Human Model mutation;
- Decision Style implementation;
- Domain Model implementation;
- final decision generation;
- recommendation generation;
- runtime injection.
