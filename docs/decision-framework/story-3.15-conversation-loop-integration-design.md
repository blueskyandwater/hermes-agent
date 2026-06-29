# Story 3.15 - Conversation Loop Integration Minimal Implementation Design

## Goal

Design how Decision Support should be connected to `conversation_loop.py` in a
future implementation story with the smallest safe runtime surface.

This story defines the intended connection point, inputs, guard use,
non-persistence invariants, and test plan for future injection of
`<ephemeral_decision_support>` into the current user message.

This story does **not** implement runtime connection. It does not edit
`conversation_loop.py`, connect gateway/API paths, change prompt builders, or
modify Decision Framework runtime behavior.

## Read-only investigation summary

Files reviewed for this design:

- `agent/conversation_loop.py`
- `agent/ephemeral_decision_support.py`
- `agent/decision_framework_adapter.py`
- `agent/human_model_snapshot.py`
- `agent/system_prompt.py`
- `run_agent.py`

### Current user message construction

`agent/conversation_loop.py` creates the current user message inside the
turn-local `messages` list. The current turn is then tracked with
`current_turn_user_idx`:

```python
user_msg = {"role": "user", "content": user_message}
messages.append(user_msg)
current_turn_user_idx = len(messages) - 1
```

A future Decision Support integration should target this current turn only. It
should not rewrite previous user messages or add synthetic messages.

### Provider-bound `api_messages` construction

`api_messages` are built from `messages` by copying each message before the
provider request is sent:

```python
api_msg = msg.copy()
```

This copy boundary is the key safety boundary. Runtime-only context can be added
to the provider-bound `api_msg` without mutating the canonical `messages` list.

### Existing external memory / plugin context injection

`conversation_loop.py` already has a current-turn ephemeral context pattern:

- external memory provider prefetch context is collected for the turn;
- plugin `pre_llm_call` context is collected for the turn;
- each provider-bound message is copied into `api_msg`;
- memory/plugin context is appended only when the copied message is the current
  user message and the role is `user`.

The existing shape is approximately:

```python
if idx == current_turn_user_idx and msg.get("role") == "user":
    _injections = []
    if _ext_prefetch_cache:
        ...
    if _plugin_user_context:
        ...
    if _injections:
        _base = api_msg.get("content", "")
        if isinstance(_base, str):
            api_msg["content"] = _base + "\n\n" + "\n\n".join(_injections)
```

Decision Support is most similar to this existing pattern: current-turn support
material that should be visible to the LLM request, but should not become stored
conversation history.

### System prompt cache handling

`agent/system_prompt.py` owns system prompt assembly, and
`conversation_loop.py` restores or builds `agent._cached_system_prompt` for the
session. The system prompt is session-scoped and cache-sensitive.

Decision Support context is turn-specific. It must therefore not be appended to
the system prompt, not invalidate the cached system prompt, and not become a
session-wide instruction.

### Session DB persistence flow

`run_agent.py` persists the canonical `messages` list through the session DB
persistence path. Provider-bound `api_messages` are request-local copies and are
not the canonical persistence source.

Therefore, if future injection modifies only the copied `api_msg`, the
`<ephemeral_decision_support>` block should not be persisted into the session DB
or durable transcripts.

### Role alternation repair

`conversation_loop.py` performs message role alternation repair before
`api_messages` are built. A future Decision Support integration should not add a
new `system`, `assistant`, `tool`, or synthetic `user` message after that repair.

The safe approach is to append support text to the existing current user
`api_msg` copy only. This keeps the provider-facing role sequence unchanged.

## Connection position candidate comparison

| Candidate | Description | Side effects | System prompt cache safety | Session DB persistence safety | Role alternation safety | Testability | Implementation size | Existing structure fit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A. Put it alongside the existing external memory / plugin injection block | Add Decision Support as another item in the existing current-user `_injections` flow | Low | High | High if only `api_msg` is changed | High | Medium | Small | High |
| B. Build the decision support block immediately before the existing injection block | Prepare the block first, then let the existing block append it | Low to medium | High | High if only `api_msg` is changed | High | Medium | Small | Medium-high |
| C. Append it immediately after the existing injection block | Let memory/plugin injection finish, then append Decision Support to the same copied message | Low | High | High if only `api_msg` is changed | High | Medium | Small | Medium |
| D. Extract a helper and apply it only to the `api_msg` copy | Keep injection mechanics in a small helper that receives the copied message and current-turn flags | Lowest | Highest | Highest | High | High | Small to medium | Highest |
| E. Do not connect yet; keep a design note only | Leave runtime unchanged and document the future connection | None | Highest | Highest | Highest | High | None | Correct only for design-only scope |

### A. Existing injection block

A is workable because it reuses the already-safe current-user-message injection
pattern. The risk is that the `conversation_loop.py` block can grow more complex
and harder to test if Decision Support logic is mixed directly into the loop.

### B. Build immediately before the injection block

B keeps the block preparation close to the existing injection site, but it still
places Decision Support-specific decisions inside the loop body. That makes the
loop slightly less focused and can blur the boundary between building a block and
applying a block.

### C. Append immediately after the injection block

C is small and safe if it still targets only `api_msg`. However, it duplicates the
content-append mechanics and creates a second mutation point for the same current
user message copy.

### D. Helper applied only to `api_msg` copy

D is recommended. A helper keeps the future code path narrow, explicit, and easy
to unit test. It also preserves the most important runtime boundary: the helper
receives and returns a provider-bound message copy, not the canonical `messages`
entry.

Reasons to prefer D:

- It does not touch the `messages` list itself.
- It does not persist the block to the session DB.
- It does not touch the system prompt or `agent._cached_system_prompt`.
- It can be limited to the current user message only.
- It aligns with the existing external memory / plugin current-user injection
  pattern.
- It is testable as a helper without requiring a full provider turn.
- It keeps the future `conversation_loop.py` diff small.

### E. Design note only

E is the correct scope for Story 3.15 itself. It is not sufficient for a future
runtime implementation story because no provider-bound context will be injected.

## Recommendation

Use **D. Extract a helper and apply it only to the `api_msg` copy** in the future
implementation story.

The future integration should append `<ephemeral_decision_support>` only to the
provider-bound copy of the current user message, after the canonical `messages`
list is established and after role alternation repair, while building
`api_messages` for the provider request.

## Helper, input, and Guard design

### Recommended helper shape

```python
def _with_ephemeral_decision_support_for_api_msg(
    api_msg: dict[str, Any],
    *,
    is_current_turn_user: bool,
    decision_support_context: str | None,
    inject_decision_support: bool = False,
) -> dict[str, Any]:
    ...
```

The preferred helper should return a copied message rather than mutating the
input dictionary in place. `conversation_loop.py` already builds `api_msg` with
`msg.copy()`, but a non-mutating helper makes the helper-level contract clearer
and easier to test.

### Minimal future inputs

The minimal future `conversation_loop` inputs should be:

```python
decision_support_context: str | None = None
inject_decision_support: bool = False
```

These inputs are intentionally narrow:

- `decision_support_context` is prebuilt advisory context.
- `inject_decision_support` is the explicit opt-in flag from Story 3.14.

### Important runtime boundary

The future `conversation_loop` integration must remain an injection layer only:

- `conversation_loop` must not run the Decision Framework directly.
- `conversation_loop` must not create or normalize a Human Model snapshot.
- `conversation_loop` must not call `build_decision_support_context()`.
- `conversation_loop` must only receive a prebuilt `decision_support_context` and
  pass it through the guard before injection.

This boundary keeps decision-context construction separate from provider-message
construction.

### Guard API

Use the Story 3.14 guard API:

```python
build_ephemeral_decision_support_if_allowed(
    decision_support_context,
    inject_decision_support=inject_decision_support,
)
```

Expected behavior:

- If the guard returns `None`, inject nothing.
- If the guard returns a string, append that string only to the current user
  `api_msg` copy.

### Injection rules

A future implementation must preserve these rules:

- Do not put Decision Support in the system prompt.
- Do not mutate the canonical `messages` list.
- Modify only the provider-bound `api_msg` copy.
- Target only `current_turn_user_idx` when the message role is `user`.
- Do not persist the block to the session DB.
- Do not add a new message role.
- Do not inject without explicit opt-in.
- Do not inject empty, malformed, or unfenced context.

### Suggested append order

If applied through the same current-user injection area as memory/plugin context,
the suggested final message layout is:

```text
[user request]

[external memory context, if any]

[plugin user context, if any]

<ephemeral_decision_support>
...
</ephemeral_decision_support>
```

The exact order is less important than the invariants that the block remains
current-turn-only, non-persistent, and user-message-scoped.

## Test Plan

### Helper unit tests

Future helper-level tests should verify:

- A non-current-turn message is unchanged.
- A message whose role is not `user` is unchanged.
- `inject_decision_support=False` leaves the message unchanged.
- A present context without explicit opt-in leaves the message unchanged.
- Malformed or invalidly fenced context leaves the message unchanged.
- Correctly fenced context with explicit opt-in appends the wrapper.
- The original user content is preserved before the appended block.
- The returned content contains `<ephemeral_decision_support>` exactly when the
  guard allows it.
- The input dictionary is not mutated if the helper is implemented as a
  copy-returning helper.

### Conversation loop integration tests

Future integration tests should verify:

- The system prompt does not change.
- `agent._cached_system_prompt` does not change.
- The canonical `messages` list does not change.
- The session DB does not persist `<ephemeral_decision_support>`.
- The provider-bound `api_messages` current user message receives the block when
  opt-in and valid context are present.
- Previous user messages do not receive the block.
- `assistant`, `tool`, and `system` messages do not receive the block.
- Role alternation repair remains valid and no new message role is introduced.
- No injection happens without opt-in.
- No injection happens when context exists but opt-in is false.
- No injection happens for malformed or invalidly fenced context.
- Injection happens only for valid context plus explicit opt-in.

### Suggested test placement

Recommended future test files:

- `tests/agent/test_ephemeral_decision_support.py` for guard/helper behavior.
- `tests/run_agent/test_decision_support_conversation_loop_injection.py` for
  provider-bound message integration and persistence boundaries.

Useful assertions for future implementation:

```python
assert "<ephemeral_decision_support>" not in messages[current_turn_user_idx]["content"]
assert "<ephemeral_decision_support>" not in persisted_user_message
assert agent._cached_system_prompt == before_cached_system_prompt
assert api_messages[current_user_api_idx]["content"].count("<ephemeral_decision_support>") == 1
```

## Non-goals

Story 3.15 does not include:

- code implementation;
- runtime injection;
- edits to `conversation_loop.py`, `run_agent.py`, `prompt_builder.py`, or gateway
  code;
- gateway/API path integration;
- memory read/write behavior;
- Human Model mutation;
- Decision Style implementation;
- Domain Model implementation;
- final decision or recommendation generation;
- GitHub PR creation;
- push or release work.

## Future approval checkpoint

Before Story 3.16 or any runtime implementation begins, a human should explicitly
approve the narrow connection contract:

```text
Apply the Story 3.15 D approach.
Only append a guard-approved <ephemeral_decision_support> block to the
provider-bound api_msg copy for current_turn_user_idx when the role is user.
Do not mutate messages, system prompt, session DB persistence, gateway paths, or
Decision Framework construction.
```
