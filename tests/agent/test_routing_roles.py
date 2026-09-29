"""Role indirection must not change classification, inheritance or budgets."""
from copy import deepcopy

import pytest

from agent.route_classifier import get_route_model, get_route_max_turns, get_fallback_route_model


def test_roles_propagate_without_mutating_config():
    routing = {"roles": {"ordinary": "model-a", "complex": "model-b"},
               "normal_chat": {"role": "ordinary", "max_turns": 35},
               "code_or_debug": {"role": "ordinary", "max_turns": 90},
               "long_context": {"role": "complex"},
               "vision": {"role": "complex"},
               "fallback": {"role": "ordinary"},
               "fallback_routes": {"normal_chat": {"model": "other/provider"}}}
    original = deepcopy(routing)
    assert get_route_model("normal_chat", routing) == "model-a"
    assert get_route_model("code_debug", routing) == "model-a"
    assert get_route_model("unknown", routing) == "model-a"
    assert get_route_max_turns("normal_chat", routing) == 35
    assert get_route_max_turns("code_debug", routing) is None
    assert get_fallback_route_model("normal_chat", routing) == "other/provider"
    assert get_fallback_route_model("vision", routing) == ""
    assert routing == original
    routing["roles"]["complex"] = "candidate"
    assert get_route_model("vision", routing) == "candidate"
    assert get_route_model("long_context", routing) == "candidate"
    assert get_route_model("normal_chat", routing) == "model-a"


@pytest.mark.parametrize("entry,roles", [
    ({"role": "missing"}, {}), ({"role": "x"}, {"x": ""}),
    ({"role": "x"}, {"x": None}), ({"role": []}, {}),
    ({"role": "x", "model": "ambiguous"}, {"x": "ok"}),
])
def test_invalid_roles_fail_closed(entry, roles):
    with pytest.raises(ValueError):
        get_route_model("normal_chat", {"normal_chat": entry, "roles": roles, "fallback": "legacy"})


def test_legacy_routing_unchanged():
    routing = {"code_or_debug": {"model": "legacy", "max_turns": 90}, "fallback": "default"}
    assert get_route_model("code_debug", routing) == "legacy"
    assert get_route_model("normal_chat", routing) == "default"
    assert get_route_max_turns("code_debug", routing) is None


def test_resolution_for_background_review():
    from agent.routing_roles import resolve_routing_roles
    routing = {"roles": {"complex": "large"}, "long_context": {"role": "complex", "max_turns": 80}}
    resolved = resolve_routing_roles(routing)
    assert resolved["long_context"] == {"model": "large", "max_turns": 80}
    assert routing["long_context"]["role"] == "complex"


def test_conversation_uses_role_model():
    from tests.run_agent.test_actual_model_used import _make_agent, _mock_response
    agent = _make_agent()
    agent._routing_config = {"enabled": True, "roles": {"ordinary": "role-target"},
                             "normal_chat": {"role": "ordinary"}}
    agent.client.chat.completions.create.return_value = _mock_response()
    agent.run_conversation("Hello there")
    assert agent.client.chat.completions.create.call_args.kwargs["model"] == "role-target"
