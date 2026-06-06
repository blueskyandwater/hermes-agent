from __future__ import annotations

from agent.conversation_loop import IterationBudget, _apply_route_max_turns
from agent.route_classifier import classify_message, get_route_max_turns


class _Agent:
    def __init__(self) -> None:
        self._configured_max_iterations = 90
        self.max_iterations = 90
        self.iteration_budget = IterationBudget(90)
        self._routing_config = {
            "enabled": True,
            "surgical_code": {"max_turns": 120},
        }
        self._route_type = "normal_chat"
        self._route_max_turns = None


def _resolve_and_apply_route_budget(agent: _Agent, message: str) -> bool:
    route_type, _ = classify_message(message)
    agent._route_type = route_type
    route_max_turns = get_route_max_turns(route_type, agent._routing_config)
    return _apply_route_max_turns(
        agent,
        route_max_turns,
        agent._configured_max_iterations,
    )


def test_surgical_code_route_gets_route_local_turn_budget() -> None:
    agent = _Agent()

    changed = _resolve_and_apply_route_budget(
        agent,
        "surgical_code: apply the minimal safe diff",
    )

    assert changed is True
    assert agent.max_iterations == 120
    assert agent.iteration_budget.remaining == 120
    assert agent._configured_max_iterations == 90


def test_other_routes_keep_global_turn_budget() -> None:
    agent = _Agent()

    changed = _resolve_and_apply_route_budget(agent, "こんにちは")

    assert changed is False
    assert agent.max_iterations == 90
    assert agent.iteration_budget.remaining == 90
    assert agent._route_max_turns is None
