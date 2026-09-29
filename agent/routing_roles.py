"""Pure role indirection for primary route models; never rewrite provider fallbacks."""
from copy import deepcopy


def resolve_model_entry(entry, roles):
    if not isinstance(entry, dict) or "role" not in entry:
        return entry
    role = entry["role"]
    if ("model" in entry or not isinstance(role, str) or not role
            or not isinstance(roles, dict) or not isinstance(roles.get(role), str)
            or not roles[role].strip()):
        raise ValueError(f"Invalid or ambiguous routing role: {role!r}")
    return {**{key: value for key, value in entry.items() if key != "role"}, "model": roles[role]}


def resolve_routing_roles(routing):
    """Materialize primary route roles in a copy for legacy model-only consumers."""
    resolved = deepcopy(routing)
    roles = resolved.get("roles", {})
    for key, entry in list(resolved.items()):
        if key in ("roles", "fallback_routes", "fallback_routing"):
            continue
        if key == "fallback" and isinstance(entry, dict):
            resolved[key] = resolve_model_entry(entry, roles).get("model", "")
        else:
            resolved[key] = resolve_model_entry(entry, roles)
    return resolved
