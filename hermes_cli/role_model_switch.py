"""Switch a routing role only after a real, text-producing Codex completion."""

from __future__ import annotations

import json
import os
import stat
import tempfile
import time
from pathlib import Path

import httpx
import yaml

from hermes_cli.auth import resolve_codex_runtime_credentials
from hermes_cli.codex_models import _fetch_models_from_api
from hermes_cli.config import get_config_path
from agent.auxiliary_client import _codex_cloudflare_headers
from utils import atomic_yaml_write


def probe_codex_completion(model: str, credentials: dict) -> bool:
    """Use a bounded, tool-free Codex Responses stream; require terminal success AND text."""
    headers = _codex_cloudflare_headers(credentials["api_key"])
    headers["Authorization"] = f"Bearer {credentials['api_key']}"
    payload = {
        "model": model, "instructions": "Answer briefly.",
        "input": [{"role": "user", "content": "Reply with OK."}],
        "store": False, "stream": True, "tools": [],
    }
    text_seen = False
    completed = False
    deadline = time.monotonic() + 25
    try:
        with httpx.Client(timeout=httpx.Timeout(5.0, connect=5.0)) as client:
            with client.stream("POST", credentials["base_url"].rstrip("/") + "/responses",
                               headers=headers, json=payload) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if time.monotonic() >= deadline:
                        return False
                    if not line.startswith("data: "):
                        continue
                    if line[6:] == "[DONE]":
                        break
                    event = json.loads(line[6:])
                    if not isinstance(event, dict):
                        return False
                    kind = event.get("type")
                    if kind in ("error", "response.failed", "response.incomplete"):
                        return False
                    if kind == "response.output_text.delta":
                        delta = event.get("delta")
                        text_seen |= isinstance(delta, str) and bool(delta.strip())
                    if kind == "response.output_item.done":
                        item = event.get("item")
                        if isinstance(item, dict) and item.get("type") == "message":
                            content = item.get("content")
                            if not isinstance(content, list):
                                return False
                            text_seen |= any(isinstance(part, dict) and part.get("type") == "output_text"
                                             and isinstance(part.get("text"), str) and bool(part["text"].strip())
                                             for part in content)
                    if kind == "response.completed":
                        result = event.get("response")
                        if not isinstance(result, dict) or result.get("status") != "completed":
                            return False
                        if result.get("model") is not None and result["model"] != model:
                            return False
                        completed = True
                        break
    except (httpx.HTTPError, OSError, KeyError, ValueError, TypeError):
        return False  # Never expose credentials, URL query strings or response bodies.
    return completed and text_seen


def _validate_role(config: object, role: str) -> None:
    if not isinstance(config, dict) or not isinstance(config.get("model"), dict) or config["model"].get("provider") != "openai-codex":
        raise ValueError("The active model provider must be openai-codex.")
    routing = config.get("routing")
    roles = routing.get("roles") if isinstance(routing, dict) else None
    if not isinstance(roles, dict) or not isinstance(roles.get(role), str) or not roles[role].strip():
        raise ValueError("Role must already exist in routing.roles as a model string.")


def _private_backup(path: Path, data: bytes) -> None:
    """Atomically replace the backup without following an existing backup symlink."""
    fd, temp = tempfile.mkstemp(prefix=".config-backup-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as output:
            os.fchmod(output.fileno(), 0o600)
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temp, path.with_name(path.name + ".bak"))
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def switch_role_model(role: str, model: str) -> Path:
    """Validate live catalog + completion before atomically updating an existing role."""
    if not isinstance(role, str) or not role.strip() or role != role.strip() or not isinstance(model, str) or not model.strip() or model != model.strip():
        raise ValueError("Specify a non-empty role and model ID.")
    path = get_config_path()
    if path.is_symlink() or not path.is_file():
        raise ValueError("A regular profile config.yaml must exist.")
    initial_bytes = path.read_bytes()
    initial = yaml.safe_load(initial_bytes)
    _validate_role(initial, role)
    credentials = resolve_codex_runtime_credentials()
    token = credentials.get("api_key")
    if not isinstance(token, str) or not token.strip():
        raise ValueError("Codex OAuth credentials unavailable.")
    if model not in _fetch_models_from_api(token):
        raise ValueError("Model not present in the live Codex catalog.")
    if not probe_codex_completion(model, credentials):
        raise ValueError("Model did not produce a successful text completion.")

    # Lock a stable sidecar (not the file replaced by atomic_yaml_write).
    import fcntl
    lock_path = path.with_name(path.name + ".role-model.lock")
    if lock_path.is_symlink():
        raise ValueError("Unsafe role-model lock file.")
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0), 0o600)
    with os.fdopen(fd, "r+") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        if path.is_symlink() or not stat.S_ISREG(path.stat().st_mode) or path.read_bytes() != initial_bytes:
            raise ValueError("Config changed while validating; refusing to overwrite it.")
        current = yaml.safe_load(initial_bytes)
        _validate_role(current, role)
        current["routing"]["roles"][role] = model
        _private_backup(path, initial_bytes)
        atomic_yaml_write(path, current)
    return path


def cmd_role_model(args):
    try:
        path = switch_role_model(args.role, args.model)
    except Exception as exc:
        # OAuth/HTTP errors may include sensitive request headers; never print them.
        print("Role switch failed; configuration unchanged by this command. Check role, OAuth, live catalog and completion.")
        return 1
    print(f"Validated Codex completion; updated role {args.role!r} to {args.model!r} in {path} (backup: {path}.bak).")
    return 0
