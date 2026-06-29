# Story 3.17 - Decision Support Entry Forwarding Design

## Goal

Story 3.16 made it possible to inject a Decision Support block into the
provider-facing `api_msg` copy assembled by `conversation_loop.py`.

Story 3.17 decides how far the new inputs should be forwarded in future work.
This is a design note only. It does not connect gateway/API/CLI entry points,
execute the Decision Framework, create Human Model snapshots, or implement any
runtime behavior.

## Scope

In scope:

- Document the current runtime entry shape after Story 3.16.
- Compare forwarding candidates for the Story 3.16 inputs.
- Recommend the next smallest safe implementation unit.
- Define test expectations for a future implementation story.

Out of scope:

- Code implementation.
- Runtime, gateway, API, or CLI integration.
- `run_agent.py`, gateway, CLI, or `prompt_builder.py` changes.
- Memory read/write integration.
- Decision Framework execution.
- Human Model snapshot creation.
- Domain Model or Decision Style implementation.
- Heuristic decision-turn detection.

## Read-only confirmation summary

The following repository state was confirmed before writing this note:

- `agent/conversation_loop.py` exists and now accepts the Story 3.16 inputs:
  - `decision_support_context: str | None = None`
  - `inject_decision_support: bool = False`
- `agent/agent.py` does not exist.
- `agent/init.py` does not exist.
- `agent/__init__.py` exists, but it is not the `AIAgent` forwarder location.
- The `AIAgent` class and its `run_conversation()` forwarder live in
  `run_agent.py`.
- `AIAgent.run_conversation()` has not yet been updated to forward the Story
  3.16 inputs.
- `gateway/` exists and contains the messaging/API gateway surfaces.
- `agent/prompt_builder.py` exists but is not the right place for turn-specific
  Decision Support forwarding.
- `docs/decision-framework/story-3.15-conversation-loop-integration-design.md`
  exists and recommends injecting Decision Support only into the current-user
  provider-bound `api_msg` copy, not into durable messages or the system prompt.
- Gateway/API/CLI surfaces do not expose a Decision Support-specific request
  field today.
- The worktree was clean and `origin/main..HEAD` was `0` before this design note
  was created.

### Current `conversation_loop.run_conversation()` boundary

`agent/conversation_loop.py` is now the terminal injection sink. Its
`run_conversation()` signature includes the Story 3.16 pair:

```python
def run_conversation(
    agent,
    user_message: str,
    system_message: str = None,
    conversation_history: List[Dict[str, Any]] = None,
    task_id: str = None,
    stream_callback: Optional[callable] = None,
    persist_user_message: Optional[str] = None,
    decision_support_context: str | None = None,
    inject_decision_support: bool = False,
) -> Dict[str, Any]:
    ...
```

The implementation applies Decision Support only while building provider-bound
messages. It appends the guarded block to the copied current-user `api_msg`, not
to the canonical `messages` list.

### Current `AIAgent.run_conversation()` boundary

`run_agent.py` contains the `AIAgent` class and the public forwarder that calls
`agent.conversation_loop.run_conversation()`.

At the time of this design note, that forwarder still accepts only the previous
parameters:

```python
def run_conversation(
    self,
    user_message: str,
    system_message: str = None,
    conversation_history: List[Dict[str, Any]] = None,
    task_id: str = None,
    stream_callback: Optional[callable] = None,
    persist_user_message: Optional[str] = None,
) -> Dict[str, Any]:
    """Forwarder — see ``agent.conversation_loop.run_conversation``."""
    from agent.conversation_loop import run_conversation
    return run_conversation(
        self,
        user_message,
        system_message,
        conversation_history,
        task_id,
        stream_callback,
        persist_user_message,
    )
```

Therefore, Story 3.16's injection sink exists, but normal callers cannot yet pass
Decision Support through the `AIAgent` forwarder.

### Gateway/API/CLI observations

Gateway and API entry points ultimately call `agent.run_conversation(...)` with
standard inputs such as:

- `user_message`
- `conversation_history`
- `task_id`
- `stream_callback`
- `persist_user_message`

The OpenAI-compatible API paths parse fields like `messages`, `stream`, `model`,
and session headers. They do not currently parse or expose
`decision_support_context` or `inject_decision_support` as external request
schema fields.

This is good for the current safety boundary: external clients cannot directly
set `inject_decision_support=True`.

## Connection candidate comparison

| Candidate | Description | Safety | External input surface | Testability | Implementation size | Compatibility | Mis-injection / Decision-delegation risk | Future extensibility |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A. Add only to `AIAgent.run_conversation()` forwarder | Extend the public Python forwarder with defaulted Story 3.16 inputs and pass them to `conversation_loop` | High | None | High | Small | High if defaults preserve behavior | Low | Good internal foundation |
| B. Add around broader `run_agent.py` runtime paths | Thread the pair through more `run_agent.py` helper paths or adjacent runtime wrappers | Medium-high | Usually none, but more internal paths can accidentally carry stale context | Medium | Medium | Medium | Medium | Moderate, but can overfit before trigger architecture exists |
| C. Add gateway/API fields | Let external API/gateway requests carry Decision Support inputs | Medium | High; new public/product contract | Medium | Large | Medium | High; users or clients could try to force support context or opt-in flags | Good only after auth, redaction, and disclosure design |
| D. Add CLI flags or commands | Let CLI users manually pass Decision Support inputs | Medium | High; user-facing manual control | Medium | Medium-large | Medium | High; risks prompt-like manual injection and confusing debug affordances with product behavior | Useful later for developer-only debugging if designed separately |
| E. Do not connect external entry points; keep an internal forwarder boundary | Allow only internal callers to opt in through a narrow per-turn path before exposing anything publicly | Highest | None | High | Small | High | Low | Best staged path |
| F. Do not implement further; keep design note only | Leave Story 3.16 injection sink unreachable from normal runtime callers for now | Highest immediate safety | None | High for docs, none for runtime | None | Highest | None | Limited; no runtime learning until a later story |

## Recommendation

Choose **E. Do not connect external entry points yet; keep an internal forwarder
boundary only**.

In practical terms, the next implementation should start with the smallest
version of A: add the two defaulted inputs to `AIAgent.run_conversation()` and
forward them into `agent.conversation_loop.run_conversation()`. Do not expose the
pair through gateway/API/CLI yet.

Reasons:

- It creates a stage where only internal callers can explicitly opt in before the
  feature becomes a public product surface.
- It does not increase the external request schema.
- It preserves Story 3.16's safety boundary: the block is still consumed only at
  the current-user `api_msg` copy injection sink.
- It keeps tests small and focused.
- It is unlikely to break existing behavior because both new inputs are defaulted
  to inert values.
- It avoids making `run_agent.py`, gateway, or CLI responsible for Decision
  Framework execution or Human Model snapshot generation.

## Input design

The forwarding pair should remain exactly the Story 3.16 pair:

```python
decision_support_context: str | None = None
inject_decision_support: bool = False
```

Boundary rules:

- `decision_support_context` is prebuilt context only.
- `inject_decision_support=True` must not be set directly from external user
  input.
- Gateway/API/CLI must not expose these fields in the next minimal story.
- `run_agent.py` and gateway must not execute the Decision Framework.
- `run_agent.py` and gateway must not create or normalize Human Model snapshots.
- `build_decision_support_context()` must not be called from `run_agent.py`,
  gateway, CLI, or `conversation_loop.py` as part of this forwarding step.
- The terminal consumption point remains `conversation_loop.py`, and only the
  current-user provider-facing `api_msg` copy may be modified.
- The durable `messages` list, system prompt, cached system prompt, session DB,
  memory stores, and user-visible transcript must not receive the assembled
  Decision Support block.

## Recommended next stories

### Story 3.18 - AIAgent.run_conversation() Decision Support Forwarder Minimal Implementation

Recommended implementation scope:

- Add the two defaulted parameters to `run_agent.py`'s
  `AIAgent.run_conversation()` signature:
  - `decision_support_context: str | None = None`
  - `inject_decision_support: bool = False`
- Forward those values to `agent.conversation_loop.run_conversation()`.
- Preserve all existing call compatibility.
- Do not change runtime entry points outside the `AIAgent` forwarder.
- Do not modify gateway/API/CLI.
- Do not modify `agent/prompt_builder.py`.
- Do not execute the Decision Framework.
- Do not create Human Model snapshots.

This story should be a minimal forwarder-only implementation.

### Story 3.19 - Internal caller design

Design which internal component is allowed to construct or select a prebuilt
`decision_support_context` and set `inject_decision_support=True` for one turn.
This story should decide ownership, trigger policy, authority labeling, and
privacy/redaction boundaries before any broad runtime connection.

### Story 3.20 - External API/gateway design

Only after the internal path is proven should a separate story decide whether
external surfaces need developer/debug access. That design must cover auth,
redaction, logging, abuse resistance, disclosure, and schema compatibility.

## Test plan for Story 3.18

A future Story 3.18 implementation should include focused tests, preferably in:

```text
tests/run_agent/test_decision_support_forwarder.py
```

Required assertions:

1. Existing calls remain compatible.
   - `agent.run_conversation("hello")` still works with no new arguments.
2. Default behavior does not inject Decision Support.
   - No context and `inject_decision_support=False` preserve current behavior.
3. The forwarder passes `decision_support_context` to `conversation_loop`.
4. The forwarder passes `inject_decision_support` to `conversation_loop`.
5. A valid context plus explicit opt-in injects only once into the current-user
   provider-facing `api_msg` copy.
6. A valid context with `inject_decision_support=False` does not inject.
7. The canonical `messages` list is not mutated with the Decision Support block.
8. The system prompt and cached system prompt are not modified.
9. Session DB persistence stores the raw user message, not the assembled
   provider-facing content.
10. Gateway/API/CLI and `prompt_builder.py` remain unchanged.
11. External request schemas remain unchanged.
12. Decision Framework execution is not triggered.
13. Human Model snapshot creation is not triggered.

Suggested targeted regression suite:

```bash
./.venv/bin/python -m pytest   tests/agent/test_ephemeral_decision_support.py   tests/agent/test_conversation_loop_decision_support.py   tests/agent/test_human_model_snapshot.py   tests/agent/test_decision_framework_adapter.py   tests/agent/test_decision_framework.py   -q -o 'addopts='
```

## Non-goals

This design explicitly does not include:

- Code implementation.
- Runtime connection.
- Gateway/API/CLI integration.
- `run_agent.py` modification.
- `agent/prompt_builder.py` modification.
- Memory reads or writes.
- Decision Framework execution.
- Human Model snapshot creation.
- Domain Model implementation.
- Decision Style implementation.
- Heuristic decision-turn detection.
- GitHub PR creation or upstream operations.

## Final decision

Story 3.17 recommends a staged internal-only path:

1. Keep external entry points closed.
2. Add only a default-off `AIAgent.run_conversation()` forwarder in the next
   implementation story.
3. Defer internal trigger ownership and external API/gateway design to separate
   stories.

This keeps Decision Support useful for future internal callers while preserving
the safety properties established in Story 3.16.
