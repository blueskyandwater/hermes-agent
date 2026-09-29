"""Planner commands survive the Kanban parser/handler extraction."""

import json
from pathlib import Path

import pytest

from hermes_cli import kanban as kc
from hermes_cli import kanban_db as kb
from hermes_cli import kanban_db_connect as kbc


@pytest.mark.parametrize("command,expected", [
    ("planner --json", "planner.v1"),
    ("planner-preview --json", "planner-consumer-preview.v1"),
    ("pre-gate-preview --runtime-mode design-no-commit --json", "pre-gate-preview.v1"),
    ("watchdog-preview --runtime-mode design-no-commit --json", None),
])
def test_planner_slash_commands_still_run_read_only(tmp_path, monkeypatch, command, expected):
    home = tmp_path / ".hermes"
    home.mkdir()
    monkeypatch.setenv("HERMES_HOME", str(home))
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    with kbc.connect_closing() as conn:
        task_id = kb.create_task(
            conn, title="[Implementation] planner merge", body="mode: implementation-no-commit",
        )

    output = kc.run_slash(command)
    data = json.loads(output)
    if expected is not None:
        assert data["schema_version"] == expected
    else:
        assert data["safe_noop"] is True
    if expected == "planner.v1":
        assert any(row["task_id"] == task_id for row in data["classification"])
    assert data.get("dispatch_allowed", False) is False
    with kbc.connect_closing() as conn:
        assert kb.get_task(conn, task_id).status == "ready"
