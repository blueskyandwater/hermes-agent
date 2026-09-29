"""Verified role switching never updates configuration before completion."""
import json
from contextlib import contextmanager
from types import SimpleNamespace

import pytest
import yaml

from hermes_cli import role_model_switch as switch


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    path = tmp_path / "config.yaml"
    path.write_text(yaml.safe_dump({"model": {"provider": "openai-codex"}, "routing": {
        "enabled": True, "roles": {"normal": "old", "design": "large"},
        "normal_chat": {"role": "normal"}, "code_design": {"role": "design"}}}), encoding="utf-8")
    return path


def test_switch_success_changes_only_selected_role_and_backs_up(home, monkeypatch):
    before = yaml.safe_load(home.read_text())
    monkeypatch.setattr(switch, "resolve_codex_runtime_credentials", lambda: {"api_key": "secret", "base_url": "https://chatgpt.com/backend-api/codex"})
    monkeypatch.setattr(switch, "_fetch_models_from_api", lambda token: ["new"])
    monkeypatch.setattr(switch, "probe_codex_completion", lambda model, credentials: True)
    switch.switch_role_model("normal", "new")
    after = yaml.safe_load(home.read_text())
    assert after["routing"]["roles"] == {"normal": "new", "design": "large"}
    assert after["routing"]["normal_chat"] == before["routing"]["normal_chat"]
    assert yaml.safe_load((home.parent / "config.yaml.bak").read_text()) == before
    assert "secret" not in home.read_text()


@pytest.mark.parametrize("models,probe", [([], True), (["other"], True), (["new"], False)])
def test_failed_validation_never_writes_config(home, monkeypatch, models, probe):
    original = home.read_bytes()
    monkeypatch.setattr(switch, "resolve_codex_runtime_credentials", lambda: {"api_key": "secret"})
    monkeypatch.setattr(switch, "_fetch_models_from_api", lambda token: models)
    monkeypatch.setattr(switch, "probe_codex_completion", lambda model, credentials: probe)
    with pytest.raises(ValueError):
        switch.switch_role_model("normal", "new")
    assert home.read_bytes() == original
    assert not (home.parent / "config.yaml.bak").exists()


def test_role_removed_during_probe_does_not_overwrite(home, monkeypatch):
    monkeypatch.setattr(switch, "resolve_codex_runtime_credentials", lambda: {"api_key": "secret"})
    monkeypatch.setattr(switch, "_fetch_models_from_api", lambda token: ["new"])
    def concurrent_edit(model, credentials):
        config = yaml.safe_load(home.read_text())
        config["routing"]["roles"]["normal"] = "someone-else"
        home.write_text(yaml.safe_dump(config))
        return True
    monkeypatch.setattr(switch, "probe_codex_completion", concurrent_edit)
    with pytest.raises(ValueError):
        switch.switch_role_model("normal", "new")
    assert yaml.safe_load(home.read_text())["routing"]["roles"]["normal"] == "someone-else"


def test_probe_requires_completed_response_with_text(monkeypatch):
    seen = []
    class Stream:
        def __init__(self, frames):
            self.frames = frames
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def raise_for_status(self): pass
        def iter_lines(self): return iter(self.frames)
    class Client:
        def __init__(self, **kwargs):
            seen.append(kwargs)
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def stream(self, method, url, **kwargs):
            seen.append((method, url, kwargs))
            return Stream(frames)
    monkeypatch.setattr(switch.httpx, "Client", Client)
    credentials = {"api_key": "secret", "base_url": "https://chatgpt.com/backend-api/codex"}
    frames = ['data: '+json.dumps({"type": "response.completed", "response": {"status": "completed"}})]
    assert not switch.probe_codex_completion("new", credentials)
    frames[:] = ['data: '+json.dumps({"type": "response.output_text.delta", "delta": "ok"}), *frames]
    assert switch.probe_codex_completion("new", credentials)
    assert seen[-1][2]["json"]["tools"] == []
    assert seen[-1][2]["json"]["store"] is False
    assert seen[0]["timeout"].read <= 5
    frames[-1] = 'data: '+json.dumps({"type": "response.failed", "response": {"status": "failed"}})
    assert not switch.probe_codex_completion("new", credentials)
    frames[:] = ['data: '+json.dumps({"type": "response.output_text.delta", "delta": "ok"}), 'data: {bad json', 'data: '+json.dumps({"type": "response.completed", "response": {"status": "completed"}})]
    assert not switch.probe_codex_completion("new", credentials)
    frames[1] = 'data: '+json.dumps({"type": "response.completed", "response": {"status": "completed", "model": "wrong"}})
    assert not switch.probe_codex_completion("new", credentials)
    frames[1] = 'data: '+json.dumps({"type": "response.completed", "response": []})
    assert not switch.probe_codex_completion("new", credentials)


def test_wrong_provider_and_malformed_config_do_not_fetch_or_write(home, monkeypatch):
    monkeypatch.setattr(switch, "resolve_codex_runtime_credentials", lambda: pytest.fail("must not read OAuth"))
    for document in ({"model": {"provider": "openrouter"}, "routing": {"roles": {"normal": "old"}}},
                     {"model": {"provider": "openai-codex"}, "routing": []}):
        home.write_text(yaml.safe_dump(document))
        previous = home.read_bytes()
        with pytest.raises(ValueError):
            switch.switch_role_model("normal", "new")
        assert home.read_bytes() == previous


def test_concurrent_unrelated_change_is_preserved(home, monkeypatch):
    monkeypatch.setattr(switch, "resolve_codex_runtime_credentials", lambda: {"api_key": "secret"})
    monkeypatch.setattr(switch, "_fetch_models_from_api", lambda token: ["new"])
    def concurrent_edit(model, credentials):
        config = yaml.safe_load(home.read_text())
        config["routing"]["enabled"] = False
        home.write_text(yaml.safe_dump(config))
        return True
    monkeypatch.setattr(switch, "probe_codex_completion", concurrent_edit)
    with pytest.raises(ValueError, match="changed"):
        switch.switch_role_model("normal", "new")
    assert yaml.safe_load(home.read_text())["routing"]["enabled"] is False
    assert not (home.parent / "config.yaml.bak").exists()


def test_existing_backup_symlink_never_followed(home, monkeypatch, tmp_path):
    outside = tmp_path / "outside"
    outside.write_text("preserve")
    (home.parent / "config.yaml.bak").symlink_to(outside)
    monkeypatch.setattr(switch, "resolve_codex_runtime_credentials", lambda: {"api_key": "secret"})
    monkeypatch.setattr(switch, "_fetch_models_from_api", lambda token: ["new"])
    monkeypatch.setattr(switch, "probe_codex_completion", lambda model, credentials: True)
    switch.switch_role_model("normal", "new")
    assert outside.read_text() == "preserve"
    assert not (home.parent / "config.yaml.bak").is_symlink()
    assert (home.parent / "config.yaml.bak").stat().st_mode & 0o777 == 0o600


def test_cli_parser_exposes_switch():
    # Help is available without performing OAuth or touching live configuration.
    import subprocess
    import sys
    result = subprocess.run([sys.executable, "-m", "hermes_cli.main", "role-model", "--help"],
                            capture_output=True, text=True, timeout=40)
    assert result.returncode == 0
    assert "--role" in result.stdout and "--model" in result.stdout
def test_cli_failure_returns_nonzero(home):
    import os
    import subprocess
    import sys
    env = {**os.environ, "HERMES_HOME": str(home.parent)}
    result = subprocess.run(
        [sys.executable, "-m", "hermes_cli.main", "role-model", "--role", "missing", "--model", "new"],
        env=env, capture_output=True, text=True, timeout=40,
    )
    assert "Role switch failed" in result.stdout
    assert result.returncode == 1

