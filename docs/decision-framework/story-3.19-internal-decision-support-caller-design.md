# Story 3.19 - Internal Decision Support Caller Design

## Goal

Story 3.18 made `AIAgent.run_conversation()` capable of forwarding a prebuilt
`decision_support_context` and `inject_decision_support` flag into
`agent.conversation_loop.run_conversation()`.

Story 3.19 decides who is allowed to build that prebuilt Decision Support
context and pass it to `AIAgent`.

This is a design note only. It does not implement runtime wiring, create new
entry points, expose gateway/API/CLI fields, create Human Model snapshots,
change `run_agent.py`, or execute the Decision Framework during normal runtime.

## Scope

In scope:

- Summarize the current Decision Support adapter and forwarding boundaries.
- Compare ownership candidates for prebuilt context construction.
- Recommend the smallest safe next implementation unit.
- Define authority and non-authority boundaries for future callers.
- Define test expectations for the next implementation story.

Out of scope:

- Code implementation.
- Runtime, gateway, API, or CLI integration.
- `run_agent.py`, `agent/conversation_loop.py`, or `agent/prompt_builder.py`
  changes.
- Memory read/write integration.
- Human Model mutation or auto-snapshot generation.
- Decision Style or Domain Model implementation.
- Heuristic decision-turn detection.
- Kanban mutations beyond the already-completed Story 3.19 lifecycle.

## Read-only confirmation summary

The following repository state was confirmed before writing this note:

- `agent/decision_framework_adapter.py` exposes
  `build_decision_support_context(human_model_snapshot, turn_context=None)`.
- `build_decision_support_context()` accepts an explicit
  `human_model_snapshot` and optional `turn_context`.
- The adapter returns fenced
  `<decision_support_context>...</decision_support_context>` text.
- The adapter calls `run_decision_framework()` but does not connect itself to
  memory, tools, conversation flow, gateway, or API surfaces.
- `agent/human_model_snapshot.py` is explicit-snapshot-only.
- Allowed Human Model snapshot fields are exactly:
  - `identity`
  - `energy`
  - `habit`
  - `growth`
  - `communication`
  - `coaching`
- `agent/human_model_snapshot.py` does not read memory, parse docs/profile,
  mutate Human Model state, or connect to runtime surfaces.
- `agent/decision_framework.py` is intentionally side-effect free and returns a
  minimal Decision Framework output structure without making the user's final
  decision.
- `agent/conversation_loop.py` accepts prebuilt
  `decision_support_context: str | None = None` and
  `inject_decision_support: bool = False`.
- `conversation_loop.py` is the terminal injection sink only; it does not build
  Decision Support context itself.
- `conversation_loop.py` injects only into the provider-bound current-user
  `api_msg` copy, not the canonical `messages` list, system prompt, or session
  DB.
- `run_agent.py` contains `AIAgent.run_conversation()`.
- After Story 3.18, `AIAgent.run_conversation()` forwards the Decision Support
  pair into `agent.conversation_loop.run_conversation()`.
- Gateway/API/CLI surfaces do not currently expose a Decision
  Support-specific request field.
- External user input does not currently have a supported path to set
  `inject_decision_support=True`.
- The worktree was clean and `origin/main..HEAD` was `0` before this design
  note was created.

### Current adapter boundary

`agent/decision_framework_adapter.py` currently defines:

```python
def build_decision_support_context(
    human_model_snapshot: Mapping[str, Any] | None,
    turn_context: Mapping[str, Any] | None = None,
) -> str:
```

Key observations:

- The adapter expects caller-provided input.
- `turn_context` is accepted but currently not used for policy logic.
- The adapter normalizes the Human Model snapshot through
  `normalize_human_model_snapshot()`.
- The adapter executes the pure `run_decision_framework()` runtime and formats
  its output into fenced Decision Support text.
- The adapter is not itself a runtime trigger owner.

### Current Human Model snapshot boundary

`agent/human_model_snapshot.py` intentionally accepts only explicit caller-
provided snapshot mappings and copies only the six allowed sections.

This means Story 3.19 should not assume any of the following:

- memory-backed Human Model lookup,
- docs/profile parsing,
- implicit snapshot generation,
- or any mutable Human Model source.

### Current `AIAgent` boundary

`run_agent.py` now forwards the Story 3.18 pair through
`AIAgent.run_conversation()` into `conversation_loop.run_conversation()`.

That means `AIAgent` can now carry a prebuilt Decision Support payload, but it
still does not own the responsibility to generate one.

### Current `conversation_loop` boundary

`agent/conversation_loop.py` remains the terminal injection sink.

Its role is limited to:

- receiving a prebuilt `decision_support_context`,
- checking the explicit `inject_decision_support` guard,
- appending the block only to the copied provider-facing current-user `api_msg`,
- leaving canonical `messages`, system prompt, and durable storage unchanged.

### Gateway/API/CLI observations

Gateway/API/CLI entry points ultimately call `agent.run_conversation(...)`, but
no supported external schema currently carries:

- `decision_support_context`
- `inject_decision_support`

This is an important safety boundary. Public callers cannot directly force
Decision Support injection today.

## Candidate comparison

| Candidate | Description | Safety | Responsibility separation | External input surface | Human Model mutation risk | Decision-delegation risk | Testability | Implementation size | Future extensibility |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A. Explicit caller builds context and passes it to `AIAgent` | A trusted internal caller invokes `build_decision_support_context()` and passes the result into `AIAgent.run_conversation()` | High | High | None | Low | Low | High | Small | High |
| B. `AIAgent` owns a Decision Support builder helper | `AIAgent` grows a helper to normalize inputs and build context internally | Medium | Medium-Low | None | Medium | Medium | Medium | Medium | Medium |
| C. `run_agent.py` owns context generation more broadly | Broader runtime wrapper logic constructs context around `AIAgent` calls | Medium-Low | Low | None | Medium | Medium | Medium-Low | Medium | Medium |
| D. Gateway/API/CLI accepts or builds context | Public surfaces expose Decision Support request fields or trigger logic | Low for current stage | Low | High | High | High | Medium | Large | Potentially high later, but unsafe now |
| E. Only Kanban/internal worker is trusted to generate and inject | Restrict generation to a specific worker or worker lane | Medium-High | Medium | None | Low | Low | Medium | Medium | Medium |
| F. No new generation path yet; allow only manual prebuilt context | Keep the forwarder capability but do not add automatic builders yet | Highest immediate safety | High | None | Low | Low | High | None | Medium |

### A. Explicit caller builds context and passes it to `AIAgent`

Recommended as the primary direction.

Benefits:

- Clear ownership.
- Keeps `AIAgent` and `conversation_loop` small.
- Maintains the internal-only boundary.
- Makes tests straightforward because caller intent is explicit.
- Avoids conflating context generation with transport or injection.

### B. `AIAgent` owns a Decision Support builder helper

Not recommended for the next step.

This would make `AIAgent` responsible for more than forwarding and risks
blurring boundaries between:

- transport,
- Human Model normalization,
- and Decision Framework invocation.

### C. `run_agent.py` owns context generation more broadly

Not recommended.

`run_agent.py` is already a broad runtime surface. Adding Decision Support
construction there would make ownership less precise and increase the chance of
future overreach.

### D. Gateway/API/CLI accepts or builds context

Explicitly not recommended at this stage.

This would enlarge the public input surface too early and create a path for
external clients or users to force Decision Support behavior before authority,
redaction, and disclosure policies are settled.

### E. Only Kanban/internal worker is trusted to generate and inject

Useful as a possible future subset, but too narrow as the main design.

The safer abstraction is not “worker only,” but “trusted internal caller.”
That allows future internal integration without prematurely tying the design to
one worker lane or board system.

A future shared helper such as `TurnDecisionSupportPreparer` is a reasonable
candidate, but only as an internal trusted helper, not a public surface.

### F. No new generation path yet; allow only manual prebuilt context

Recommended in combination with A for the current stage.

This preserves the newly-created forwarder boundary without automatically
spreading context generation into runtime flows before ownership and tests are
made explicit.

## Recommendation

Choose **A + F**.

Practical meaning:

1. A trusted internal caller may explicitly construct a prebuilt
   `decision_support_context`.
2. That caller may then pass the context into
   `AIAgent.run_conversation(..., decision_support_context=..., inject_decision_support=True)`.
3. No automatic generation path is added yet.
4. No gateway/API/CLI request field is added yet.
5. No heuristic turn detection is added yet.
6. No Human Model lookup/mutation path is added yet.

This keeps the capability internal, explicit, and testable.

## Responsibility separation

### Trusted internal caller / internal helper

This is the allowed owner of Decision Support context construction.

Responsibilities:

- Receive or assemble explicit `human_model_snapshot` input.
- Receive or assemble `turn_context`.
- Call `build_decision_support_context()`.
- Pass the prebuilt context and explicit injection flag into
  `AIAgent.run_conversation()`.
- Decide per-turn whether Decision Support should be requested.

Non-responsibilities:

- Do not update memory.
- Do not mutate Human Model state.
- Do not expose public gateway/API/CLI fields.
- Do not persist Decision Support context to durable stores.

### `AIAgent`

Responsibilities:

- Accept a prebuilt `decision_support_context`.
- Accept `inject_decision_support`.
- Forward both values into `conversation_loop.run_conversation()`.

Non-responsibilities:

- Do not build Decision Support context.
- Do not normalize or source Human Model snapshots beyond receiving caller
  inputs.
- Do not decide when Decision Framework should run.

### `conversation_loop`

Responsibilities:

- Act as the injection sink only.
- Append the prebuilt block only to the current-user provider-bound `api_msg`
  copy.
- Keep canonical `messages`, system prompt, and session DB unchanged.

Non-responsibilities:

- Do not call `build_decision_support_context()`.
- Do not run Decision Framework directly.
- Do not infer injection from heuristics.

### Gateway / API / CLI

Responsibilities in this stage:

- None beyond existing normal call transport.

Non-responsibilities:

- Do not expose `decision_support_context` or
  `inject_decision_support` as public request schema.
- Do not trigger Decision Framework execution.
- Do not create or mutate Human Model snapshots.

## Input design

Minimum future caller-owned inputs:

- `human_model_snapshot`
- `turn_context`
- `user_message`
- `task_id`

Illustrative `turn_context` shape:

```python
{
    "user_message": user_message,
    "task_id": task_id,
    "source": "internal",
}
```

Boundary rules:

- `human_model_snapshot` must be explicit caller-provided input.
- Only the six allowed Human Model sections are carried onward.
- `turn_context` may be caller-constructed and may remain minimal.
- `decision_support_context` must be prebuilt before reaching
  `AIAgent.run_conversation()`.
- `inject_decision_support=True` is an authority signal, not a user-facing
  request field.

## Authority to set `inject_decision_support=True`

Allowed:

- Trusted internal caller.
- Tests.
- Explicitly approved internal worker/integration in a future story.

Not allowed:

- Gateway/API/CLI request payloads.
- Raw external user input.
- Heuristic decision-turn detection.
- Prompt-level instructions from the user.
- `conversation_loop` deciding on its own.

## Future internal helper candidate

A future helper such as `TurnDecisionSupportPreparer` is reasonable if it stays
strictly internal and narrow.

If introduced later, it should:

- accept explicit snapshot and turn context,
- call `build_decision_support_context()`,
- return only prebuilt context or a no-op result,
- avoid memory/Human Model mutation,
- avoid public schema exposure,
- and remain outside `AIAgent` and `conversation_loop`.

It should not be introduced in this story's implementation scope.

## Recommended next story

### Story 3.20 - Internal Decision Support Caller Minimal Implementation

Recommended scope:

- Add a small internal helper or caller-side preparation path.
- Accept explicit `human_model_snapshot` and `turn_context`.
- Call `build_decision_support_context()`.
- Pass the result into
  `AIAgent.run_conversation(..., decision_support_context=..., inject_decision_support=True)`.
- Preserve all existing runtime behavior by default.
- Do not modify gateway/API/CLI.
- Do not modify memory or Human Model state.
- Do not add heuristic decision-turn detection.

## Test plan for future implementation

A future implementation should prove all of the following:

1. By default, Decision Support does not run.
2. Without explicit snapshot input, no automatic snapshot generation occurs.
3. Only trusted internal caller paths can set
   `inject_decision_support=True`.
4. The call sites for `build_decision_support_context()` are intentionally
   limited.
5. `conversation_loop.py` does not execute Decision Framework directly.
6. `AIAgent.run_conversation()` remains a forwarder, not a generator.
7. Gateway/API/CLI request schemas remain unchanged.
8. Memory and Human Model state are not updated.
9. Valid context is injected only into the current-user provider-bound
   `api_msg` copy.
10. Invalid or empty context is not injected.
11. Canonical messages, system prompt, and session DB remain clean.
12. The external/public product surface remains unchanged.

## Non-goals

This story does not include:

- code implementation,
- runtime/gateway/API/CLI integration,
- memory read/write,
- Human Model mutation,
- Decision Style or Domain Model implementation,
- heuristic detection,
- external schema changes,
- or public user control of Decision Support injection.

## Final decision

Story 3.19 recommends a staged internal-only path:

1. Keep context generation owned by a trusted internal caller.
2. Keep `AIAgent` as a forwarder only.
3. Keep `conversation_loop` as an injection sink only.
4. Keep gateway/API/CLI closed to Decision Support-specific inputs.
5. Defer any automatic generation helper to a later minimal internal story.

This preserves the safety properties established in Stories 3.15 through 3.18
while making the next implementation unit small and explicit.
