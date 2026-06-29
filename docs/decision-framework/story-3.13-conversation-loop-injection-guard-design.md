# Story 3.13 - Conversation Loop Injection Guard Design

## Goal

Design the guard contract that must be satisfied before a future
`conversation_loop.py` integration injects `<ephemeral_decision_support>` into
provider-bound messages.

This story is design-only. It does not implement runtime wiring, connect the
formatter to `conversation_loop`, or change gateway/API behavior.

The future injection must preserve these invariants:

- Do not break system prompt cache stability.
- Do not place decision support context in the system prompt.
- Do not mutate the persistent `messages` list.
- Do not persist the injected block to the session DB.
- Limit the block to the current turn only.
- Do not add a new message role or break role alternation.
- Do not increase the risk that Hermes appears to make the user's decision.

## Read-only investigation summary

Files reviewed for this design:

- `agent/conversation_loop.py`
- `agent/system_prompt.py`
- `agent/ephemeral_decision_support.py`
- `agent/decision_framework_adapter.py`
- `docs/decision-framework/story-3.11-ephemeral-context-injection-design.md`

`run_agent.py` persistence flow was also considered because session DB
non-persistence is one of the required invariants.

### Current user message construction

`agent/conversation_loop.py` creates the current user message inside the
turn-local `messages` list:

```python
user_msg = {"role": "user", "content": user_message}
messages.append(user_msg)
current_turn_user_idx = len(messages) - 1
agent._persist_user_message_idx = current_turn_user_idx
```

A future decision-support injection should target this current turn only, and
only after the provider-bound request copy is being built.

### System prompt caching

`agent/system_prompt.py` states that the system prompt is built once per session
and reused across turns, with rebuilds limited to compression/cache-invalidation
paths. `conversation_loop.py` restores or builds `agent._cached_system_prompt`
before the tool loop.

Decision support context is turn-specific advisory material, so it must not be
mixed into the system prompt. Putting it in the system prompt would make a
current-turn block look like session-wide instruction and can disrupt provider
prefix-cache stability.

### Existing ephemeral user-message injection pattern

`conversation_loop.py` already has an API-call-time pattern for ephemeral
current-turn context:

- plugin `pre_llm_call` context is collected once per turn;
- external memory provider prefetch context is collected once per turn;
- provider-bound `api_messages` are created from `messages` using `msg.copy()`;
- memory/plugin context is appended only to the `api_msg` copy for
  `current_turn_user_idx` when that message role is `user`.

The relevant invariant is:

```python
api_msg = msg.copy()
# mutate api_msg["content"] only, not msg["content"]
```

This makes injected context visible to the provider request while keeping the
original `messages` list unchanged.

### Role alternation repair

`conversation_loop.py` repairs malformed message role alternation before building
`api_messages`. A future decision-support integration should therefore not add a
new `system`, `assistant`, `tool`, or synthetic `user` message. It should append
to the existing current user message in the `api_msg` copy only.

### Session persistence

Session persistence writes the canonical `messages` list, not the provider-bound
`api_messages` copy. Therefore, if future injection mutates only `api_msg`, the
`<ephemeral_decision_support>` block should not be written to the session DB or
JSON transcript.

### Story 3.11 alignment

Story 3.11 recommended current user message ephemeral injection later. It also
established these placement constraints:

- append to the current user message only;
- do not mutate the `messages` list itself;
- modify only `api_messages` / `api_msg` copy;
- persist the original user message;
- do not put the block in the system prompt.

Story 3.13 adds the guard conditions that decide whether that future injection
is allowed at all.

## Injection candidate comparison

| Candidate | Description | Safety | Smallness | Mis-injection risk | Decision takeover risk | Testability | Future extensibility |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A. Always inject | Always append an ephemeral decision-support wrapper | Low | Medium | High | High | Medium | Low |
| B. Context-present-only | Inject when `decision_support_context` exists | Medium-High | High | Medium | Medium | High | Medium |
| C. Heuristic decision-like turn detection | Infer decision turns from message text | Low-Medium | Low | High | High | Low | Medium |
| D. Explicit opt-in flag | Inject only when the caller explicitly opts in | High | Medium | Low | Low | High | High |
| E. No injection yet | Document the guard contract only | Highest for this story | Highest | None | None | High | Medium |

### A. Always inject

Not recommended. Most turns do not need decision support context. Always
injecting would add irrelevant instructions to ordinary chat, coding, research,
and tool loops, increasing both confusion and decision-takeover risk.

### B. Context-present-only guard

Useful as a lower-level requirement, but not sufficient alone. A context string
can exist for reasons other than a caller explicitly requesting decision-support
injection. Without an explicit caller signal, ownership of the injection decision
is ambiguous.

### C. Heuristic decision-turn detection

Not recommended now. Heuristics can misclassify ordinary conversation or
implementation tasks as decision turns. That would increase accidental injection
and make tests brittle.

### D. Explicit opt-in injection guard

Recommended. The runtime caller must explicitly request injection, and the guard
then validates the presence, shape, safety envelope, and target-message
constraints. This keeps the runtime behavior intentional, testable, and narrow.

### E. No injection yet

Correct for Story 3.13 scope. This story only documents the guard contract. For a
future runtime story, the intended direction is D, with B as one of D's required
conditions.

## Recommendation

**Recommend explicit opt-in injection guard.**

A future integration should inject decision support context only when all of the
following are true:

1. The caller explicitly opts in to decision-support injection for this turn.
2. A non-empty `decision_support_context` is present.
3. The context is fenced as `<decision_support_context>...</decision_support_context>`.
4. The formatted block is wrapped as
   `<ephemeral_decision_support>...</ephemeral_decision_support>`.
5. The target is the provider-bound `api_msg` copy of the current user message.
6. The original `messages` list and cached system prompt remain unchanged.

Additional conclusions:

- B is a subcondition of D, not the top-level policy.
- C should not be adopted now.
- E is the correct current-story scope, but D is the future runtime policy.

## Injection Guard responsibilities

The guard decides whether injection is allowed for a single turn. It should check:

- whether this turn has explicit opt-in;
- whether formatter output is non-empty;
- whether `decision_support_context` is a valid fenced block;
- whether the formatted output is wrapped in `<ephemeral_decision_support>`;
- whether the injection target is the current user message only;
- whether the path writes only to `api_msg` copy, not `messages`;
- whether the block avoids system prompt placement;
- whether the block avoids session DB persistence;
- whether the block avoids domain judgment, recommendations, or final decisions.

The guard does not decide what the user should do.

## Guard allow conditions

Injection may proceed only if all of these are true:

- explicit opt-in is present;
- `decision_support_context` exists;
- context is not empty or whitespace-only;
- context is fenced with `<decision_support_context>` and
  `</decision_support_context>`;
- formatter output is wrapped with `<ephemeral_decision_support>` and
  `</ephemeral_decision_support>`;
- `current_turn_user_idx` is known;
- the target message role is `user`;
- the target message content is a string;
- only the provider-bound `api_msg` copy is modified;
- the canonical `messages` list is not modified;
- the cached system prompt is not modified;
- the block is not saved to memory;
- the block is not treated as a Human Model update;
- the block is not treated as a Decision Style update;
- the block does not make domain-specific judgments;
- the block does not prompt a final decision or recommendation;
- the block states that the user remains responsible for the decision;
- the block states that it must not be stored as memory.

## Guard deny conditions

Injection must not happen if any of these are true:

- no explicit opt-in;
- no `decision_support_context`;
- context is empty or whitespace-only;
- context is not fenced as `<decision_support_context>`;
- formatter output is not wrapped as `<ephemeral_decision_support>`;
- `current_turn_user_idx` is unavailable;
- the target message role is not `user`;
- target content is not a string;
- injection would require changing the system prompt;
- injection would require changing the canonical `messages` list;
- injection would create a new message role;
- injection would be persisted to session DB;
- the block includes domain judgment, recommendation, or final decision language;
- the block suggests updating Human Model, Decision Style, memory, or Domain Model.

## Guard non-goals

The guard must not perform these actions:

- run the Decision Framework;
- generate a Human Model snapshot;
- perform Domain Model judgment;
- call an LLM;
- read or write memory;
- connect to `conversation_loop` runtime;
- edit gateway/API behavior;
- generate a recommendation;
- generate a final decision;
- infer decision-like turns heuristically.

## Test Plan

### Guard unit tests

Future guard tests should cover:

- opt-in absent returns false;
- context absent returns false;
- empty or whitespace-only context returns false;
- malformed `<decision_support_context>` fence returns false;
- malformed `<ephemeral_decision_support>` wrapper returns false;
- valid opt-in plus valid fenced context returns true;
- formatted output includes `The user remains responsible for the decision.`;
- formatted output includes `Do not store as memory.`;
- formatted output says it is not a final decision or recommendation;
- formatted output says not to treat it as a Human Model update;
- formatted output says not to treat it as a Decision Style update;
- formatted output says not to make domain-specific judgments.

### Future conversation loop integration tests

A later runtime-integration story should test that:

- the cached system prompt is unchanged before and after injection;
- the canonical `messages` list is unchanged;
- the session DB does not contain `<ephemeral_decision_support>`;
- only `api_messages[current_turn_user_idx]["content"]` contains the wrapper;
- previous user messages are not modified;
- assistant, tool, and system messages are not modified;
- no new message role is inserted;
- role alternation remains valid;
- empty context is not injected;
- opt-in absent means no injection;
- invalid fence means no injection;
- invalid wrapper means no injection;
- output does not encourage a final decision or recommendation.

Suggested future test file names:

- `tests/agent/test_ephemeral_decision_support_injection_guard.py`
- `tests/agent/test_ephemeral_decision_support_conversation_injection.py`

Suggested regression set for future implementation work:

```bash
./.venv/bin/python -m pytest \
  tests/agent/test_ephemeral_decision_support.py \
  tests/agent/test_human_model_snapshot.py \
  tests/agent/test_decision_framework_adapter.py \
  tests/agent/test_decision_framework.py \
  -q -o 'addopts='
```

## Non-goals for Story 3.13

This story does not include:

- code implementation;
- `conversation_loop.py` changes;
- `run_agent.py` changes;
- `prompt_builder.py` changes;
- gateway/API integration;
- memory read/write;
- Human Model mutation;
- Decision Style implementation;
- Domain Model implementation;
- final decision generation;
- recommendation generation;
- runtime injection;
- heuristic decision-turn detection.

## Future implementation note

If implemented later, prefer a small pure helper that validates the explicit
opt-in flag, fenced context, wrapper shape, and target-message invariants before
`conversation_loop.py` appends the formatted block to the current user
`api_msg` copy. The helper should be deterministic, side-effect free, and easy to
unit test without constructing a full runtime agent.
