"""Tests for the kanban CLI surface (hermes_cli.kanban)."""

from __future__ import annotations

import argparse
import json
import os
import threading
from pathlib import Path

import pytest

from hermes_cli import kanban as kc
from hermes_cli import kanban_db as kb


@pytest.fixture
def kanban_home(tmp_path, monkeypatch):
    home = tmp_path / ".hermes"
    home.mkdir()
    monkeypatch.setenv("HERMES_HOME", str(home))
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    kb.init_db()
    return home


# ---------------------------------------------------------------------------
# Workspace flag parsing
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "value,expected",
    [
        ("scratch",              ("scratch", None)),
        ("worktree",              ("worktree", None)),
        ("worktree:/tmp/wt",       ("worktree", "/tmp/wt")),
        ("dir:/tmp/work",         ("dir", "/tmp/work")),
    ],
)
def test_parse_workspace_flag_valid(value, expected):
    assert kc._parse_workspace_flag(value) == expected


def test_parse_workspace_flag_expands_user():
    kind, path = kc._parse_workspace_flag("dir:~/vault")
    assert kind == "dir"
    assert path.endswith("/vault")
    assert not path.startswith("~")

    kind, path = kc._parse_workspace_flag("worktree:~/trees/t6-wire")
    assert kind == "worktree"
    assert path.endswith("/trees/t6-wire")
    assert not path.startswith("~")

@pytest.mark.parametrize("bad", ["cloud", "dir:", "worktree:", ""])
def test_parse_workspace_flag_rejects(bad):
    if not bad:
        # Empty -> defaults; not an error.
        assert kc._parse_workspace_flag(bad) == ("scratch", None)
        return
    with pytest.raises(argparse.ArgumentTypeError):
        kc._parse_workspace_flag(bad)


def test_parse_branch_flag_rejects_empty_and_option_like():
    assert kc._parse_branch_flag(None) is None
    assert kc._parse_branch_flag(" wt/t6-wire ") == "wt/t6-wire"
    with pytest.raises(argparse.ArgumentTypeError):
        kc._parse_branch_flag("   ")
    with pytest.raises(argparse.ArgumentTypeError):
        kc._parse_branch_flag("-bad")
    with pytest.raises(argparse.ArgumentTypeError):
        kc._parse_branch_flag("bad branch")


# ---------------------------------------------------------------------------
# run_slash smoke tests (end-to-end via the same entry both CLI and gateway use)
# ---------------------------------------------------------------------------

def test_run_slash_no_args_shows_usage(kanban_home):
    out = kc.run_slash("")
    assert "kanban" in out.lower()
    assert "create" in out.lower() or "subcommand" in out.lower() or "action" in out.lower()


def test_run_slash_create_and_list(kanban_home):
    out = kc.run_slash("create 'ship feature' --assignee alice")
    assert "Created" in out
    out = kc.run_slash("list")
    assert "ship feature" in out
    assert "alice" in out


def test_run_slash_create_worktree_path_and_branch(kanban_home, tmp_path):
    target = tmp_path / ".worktrees" / "t6-wire"
    target_arg = target.as_posix()
    out = kc.run_slash(
        f"create 'ship worktree' --workspace worktree:{target_arg} --branch wt/t6-wire"
    )
    assert "Created" in out

    with kb.connect() as conn:
        tasks = kb.list_tasks(conn)
    task = tasks[0]
    assert task.workspace_kind == "worktree"
    assert task.workspace_path == target_arg
    assert task.branch_name == "wt/t6-wire"


def test_run_slash_rejects_branch_without_worktree(kanban_home):
    out = kc.run_slash("create 'bad branch' --workspace scratch --branch wt/bad")
    assert "--branch is only valid with --workspace worktree" in out


def test_run_slash_create_with_parent_and_cascade(kanban_home):
    # Parent then child via --parent
    out1 = kc.run_slash("create 'parent' --assignee alice")
    # Extract the "t_xxxx" id from "Created t_xxxx (ready, ...)"
    import re
    m = re.search(r"(t_[a-f0-9]+)", out1)
    assert m
    p = m.group(1)
    out2 = kc.run_slash(f"create 'child' --assignee bob --parent {p}")
    assert "todo" in out2  # child starts as todo

    # Complete parent; list should promote child to ready
    kc.run_slash(f"complete {p}")
    # Explicit filter: child should now be ready (was todo before complete).
    ready_list = kc.run_slash("list --status ready")
    assert "child" in ready_list


def test_run_slash_show_includes_comments(kanban_home):
    out = kc.run_slash("create 'x'")
    import re
    tid = re.search(r"(t_[a-f0-9]+)", out).group(1)
    kc.run_slash(f"comment {tid} 'remember to include performance section'")
    show = kc.run_slash(f"show {tid}")
    assert "performance section" in show


def test_run_slash_comment_max_len_trims_long_body(kanban_home):
    out = kc.run_slash("create 'x'")
    import re
    tid = re.search(r"(t_[a-f0-9]+)", out).group(1)
    kc.run_slash(f"comment {tid} '{'x' * 30}' --max-len 20")
    show = kc.run_slash(f"show {tid}")
    assert "trimmed to 20 chars by --max-len" in show
    assert "x" * 30 not in show


def test_run_slash_block_unblock_cycle(kanban_home):
    out = kc.run_slash("create 'x' --assignee alice")
    import re
    tid = re.search(r"(t_[a-f0-9]+)", out).group(1)
    # Claim first so block() finds it running
    kc.run_slash(f"claim {tid}")
    assert "Blocked" in kc.run_slash(f"block {tid} 'need decision'")
    assert "Unblocked" in kc.run_slash(f"unblock {tid}")


def test_run_slash_json_output(kanban_home):
    out = kc.run_slash("create 'jsontask' --assignee alice --json")
    payload = json.loads(out)
    assert payload["title"] == "jsontask"
    assert payload["assignee"] == "alice"
    assert payload["status"] == "ready"


def test_run_slash_dispatch_dry_run_counts(kanban_home):
    kc.run_slash("create 'a' --assignee alice")
    kc.run_slash("create 'b' --assignee bob")
    out = kc.run_slash("dispatch --dry-run")
    assert "Spawned:" in out


def test_run_slash_context_output_format(kanban_home):
    out = kc.run_slash("create 'tech spec' --assignee alice --body 'write an RFC'")
    import re
    tid = re.search(r"(t_[a-f0-9]+)", out).group(1)
    kc.run_slash(f"comment {tid} 'remember to include performance section'")
    ctx = kc.run_slash(f"context {tid}")
    assert "tech spec" in ctx
    assert "write an RFC" in ctx
    assert "performance section" in ctx


def test_run_slash_tenant_filter(kanban_home):
    kc.run_slash("create 'biz-a task' --tenant biz-a --assignee alice")
    kc.run_slash("create 'biz-b task' --tenant biz-b --assignee alice")
    a = kc.run_slash("list --tenant biz-a")
    b = kc.run_slash("list --tenant biz-b")
    assert "biz-a task" in a and "biz-b task" not in a
    assert "biz-b task" in b and "biz-a task" not in b


def test_run_slash_session_filter(kanban_home):
    """`hermes kanban list --session <id>` filters by the originating
    chat session id stamped on tasks created from inside an ACP loop."""
    from hermes_cli import kanban_db as kb
    with kb.connect() as conn:
        kb.create_task(
            conn, title="from sess-1 a", assignee="alice", session_id="sess-1"
        )
        kb.create_task(
            conn, title="from sess-1 b", assignee="alice", session_id="sess-1"
        )
        kb.create_task(
            conn, title="from sess-2", assignee="alice", session_id="sess-2"
        )
        kb.create_task(conn, title="cli only", assignee="alice")
    out_1 = kc.run_slash("list --session sess-1")
    out_2 = kc.run_slash("list --session sess-2")
    assert "from sess-1 a" in out_1
    assert "from sess-1 b" in out_1
    assert "from sess-2" not in out_1
    assert "cli only" not in out_1
    assert "from sess-2" in out_2
    assert "from sess-1 a" not in out_2


def test_kanban_list_json_includes_session_id(kanban_home):
    """JSON output exposes `session_id` so external clients (Scarf, web
    dashboards) don't need a side query to filter by chat session."""
    from hermes_cli import kanban_db as kb
    with kb.connect() as conn:
        kb.create_task(
            conn, title="acp task", assignee="alice", session_id="acp-x"
        )
    raw = kc.run_slash("list --json")
    payload = json.loads(raw)
    assert any(
        row.get("title") == "acp task"
        and row.get("session_id") == "acp-x"
        for row in payload
    )


def test_run_slash_usage_error_returns_message(kanban_home):
    # Missing required argument for create
    out = kc.run_slash("create")
    assert "usage" in out.lower() or "error" in out.lower()


def test_run_slash_assign_reassigns(kanban_home):
    out = kc.run_slash("create 'x' --assignee alice")
    import re
    tid = re.search(r"(t_[a-f0-9]+)", out).group(1)
    assert "Assigned" in kc.run_slash(f"assign {tid} bob")
    show = kc.run_slash(f"show {tid}")
    assert "bob" in show


def test_run_slash_link_unlink(kanban_home):
    a = kc.run_slash("create 'a'")
    b = kc.run_slash("create 'b'")
    import re
    ta = re.search(r"(t_[a-f0-9]+)", a).group(1)
    tb = re.search(r"(t_[a-f0-9]+)", b).group(1)
    assert "Linked" in kc.run_slash(f"link {ta} {tb}")
    # After link, b is todo
    show = kc.run_slash(f"show {tb}")
    assert "todo" in show
    assert "Unlinked" in kc.run_slash(f"unlink {ta} {tb}")


def test_board_override_is_isolated_per_concurrent_call(kanban_home, monkeypatch):
    kb.create_board("alpha")
    kb.create_board("beta")

    parser = argparse.ArgumentParser(prog="hermes", add_help=False)
    sub = parser.add_subparsers(dest="command")
    kc.build_parser(sub)

    barrier = threading.Barrier(2)
    original_init_db = kb.init_db

    def slow_init_db(*args, **kwargs):
        try:
            barrier.wait(timeout=5)
        except threading.BrokenBarrierError:
            pass
        return original_init_db(*args, **kwargs)

    monkeypatch.setattr(kb, "init_db", slow_init_db)

    failures: list[str] = []

    def worker(board: str, title: str) -> None:
        args = parser.parse_args(["kanban", "--board", board, "create", title])
        rc = kc.kanban_command(args)
        if rc != 0:
            failures.append(f"{board}:{rc}")

    t1 = threading.Thread(target=worker, args=("alpha", "alpha-task"))
    t2 = threading.Thread(target=worker, args=("beta", "beta-task"))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert failures == []

    with kb.connect_closing(board="alpha") as conn:
        alpha_titles = [row.title for row in kb.list_tasks(conn, limit=100)]
    with kb.connect_closing(board="beta") as conn:
        beta_titles = [row.title for row in kb.list_tasks(conn, limit=100)]

    assert alpha_titles == ["alpha-task"]
    assert beta_titles == ["beta-task"]


# ---------------------------------------------------------------------------
# Integration with the COMMAND_REGISTRY
# ---------------------------------------------------------------------------

def test_kanban_is_resolvable():
    from hermes_cli.commands import resolve_command

    cmd = resolve_command("kanban")
    assert cmd is not None
    assert cmd.name == "kanban"


def test_kanban_bypasses_active_session_guard():
    from hermes_cli.commands import should_bypass_active_session

    assert should_bypass_active_session("kanban")


def test_kanban_in_autocomplete_table():
    from hermes_cli.commands import COMMANDS, SUBCOMMANDS

    assert "/kanban" in COMMANDS
    subs = SUBCOMMANDS.get("/kanban") or []
    assert "create" in subs
    assert "dispatch" in subs


def test_kanban_autocomplete_includes_live_subcommands():
    from prompt_toolkit.document import Document

    from hermes_cli.commands import SlashCommandCompleter

    completer = SlashCommandCompleter()
    doc = Document("/kanban sp", cursor_position=len("/kanban sp"))
    texts = {c.text for c in completer.get_completions(doc, None)}

    assert "specify" in texts

    doc = Document("/kanban re", cursor_position=len("/kanban re"))
    texts = {c.text for c in completer.get_completions(doc, None)}

    assert "reclaim" in texts
    assert "reassign" in texts


def test_kanban_not_gateway_only():
    # kanban is available in BOTH CLI and gateway surfaces.
    from hermes_cli.commands import COMMAND_REGISTRY

    cmd = next(c for c in COMMAND_REGISTRY if c.name == "kanban")
    assert not cmd.cli_only
    assert not cmd.gateway_only


# ---------------------------------------------------------------------------
# reclaim + reassign CLI smoke tests
# ---------------------------------------------------------------------------

def test_run_slash_reclaim_running_task(kanban_home):
    import re
    import time
    import secrets
    from hermes_cli import kanban_db as kb

    out1 = kc.run_slash("create 'stuck worker task' --assignee broken-model")
    m = re.search(r"(t_[a-f0-9]+)", out1)
    assert m
    tid = m.group(1)

    # Simulate a running claim outside TTL.
    conn = kb.connect()
    try:
        lock = secrets.token_hex(4)
        conn.execute(
            "UPDATE tasks SET status='running', claim_lock=?, claim_expires=?, "
            "worker_pid=? WHERE id=?",
            (lock, int(time.time()) + 3600, 4242, tid),
        )
        conn.execute(
            "INSERT INTO task_runs (task_id, status, claim_lock, claim_expires, "
            "worker_pid, started_at) VALUES (?, 'running', ?, ?, ?, ?)",
            (tid, lock, int(time.time()) + 3600, 4242, int(time.time())),
        )
        rid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.execute("UPDATE tasks SET current_run_id=? WHERE id=?", (rid, tid))
        conn.commit()
    finally:
        conn.close()

    out = kc.run_slash(f"reclaim {tid} --reason 'test'")
    assert "Reclaimed" in out, out
    # Status back to ready.
    out2 = kc.run_slash(f"show {tid}")
    assert "ready" in out2.lower()


def test_run_slash_reassign_with_reclaim_flag(kanban_home):
    import re
    import time
    import secrets
    from hermes_cli import kanban_db as kb

    out1 = kc.run_slash("create 'switch model' --assignee orig")
    m = re.search(r"(t_[a-f0-9]+)", out1)
    tid = m.group(1)

    # Simulate a running claim.
    conn = kb.connect()
    try:
        lock = secrets.token_hex(4)
        conn.execute(
            "UPDATE tasks SET status='running', claim_lock=?, claim_expires=?, "
            "worker_pid=? WHERE id=?",
            (lock, int(time.time()) + 3600, 4242, tid),
        )
        conn.execute(
            "INSERT INTO task_runs (task_id, status, claim_lock, claim_expires, "
            "worker_pid, started_at) VALUES (?, 'running', ?, ?, ?, ?)",
            (tid, lock, int(time.time()) + 3600, 4242, int(time.time())),
        )
        rid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.execute("UPDATE tasks SET current_run_id=? WHERE id=?", (rid, tid))
        conn.commit()
    finally:
        conn.close()

    out = kc.run_slash(f"reassign {tid} newbie --reclaim --reason 'switch'")
    assert "Reassigned" in out, out
    out2 = kc.run_slash(f"show {tid}")
    assert "newbie" in out2


# ---------------------------------------------------------------------------
# /kanban specify — slash surface (same entry point CLI + gateway use)
# ---------------------------------------------------------------------------

def test_run_slash_specify_end_to_end(kanban_home, monkeypatch):
    """The /kanban specify slash command routes through run_slash, which
    both the interactive CLI and every gateway platform use. This test
    covers both surfaces."""
    from unittest.mock import MagicMock

    # Create a triage task via the same slash surface.
    create_out = kc.run_slash("create 'rough idea' --triage")
    import re
    m = re.search(r"(t_[a-f0-9]+)", create_out)
    assert m, f"no task id in: {create_out!r}"
    tid = m.group(1)

    # Mock the auxiliary client so we don't hit a real provider.
    resp = MagicMock()
    resp.choices = [MagicMock()]
    resp.choices[0].message.content = (
        '{"title": "Spec: rough idea", "body": "**Goal**\\nShip it."}'
    )
    fake_client = MagicMock()
    fake_client.chat.completions.create = MagicMock(return_value=resp)
    monkeypatch.setattr(
        "agent.auxiliary_client.get_text_auxiliary_client",
        lambda *a, **kw: (fake_client, "test-model"),
    )

    # Specify via slash.
    out = kc.run_slash(f"specify {tid}")
    assert "Specified" in out
    assert tid in out

    # Task is promoted and retitled.
    with kb.connect() as conn:
        task = kb.get_task(conn, tid)
    assert task.status in {"todo", "ready"}
    assert task.title == "Spec: rough idea"


def test_run_slash_specify_help_is_reachable(kanban_home):
    """`-h`/`--help` on a subcommand returns the actual help text — see
    issue #21794. argparse writes help to stdout and exits 0; run_slash
    must capture both streams and treat exit 0 as success, not error."""
    out = kc.run_slash("specify --help")
    assert "specify" in out.lower()
    # Help dump should NOT come back wrapped as a usage error.
    assert not out.startswith("⚠")


# ---------------------------------------------------------------------------
# /kanban help / no-args / unknown-action UX (issue #21794)
# ---------------------------------------------------------------------------

def test_run_slash_bare_returns_curated_help(kanban_home):
    """Bare `/kanban` returns the curated short-help block — not a 5KB
    argparse usage dump."""
    out = kc.run_slash("")
    assert "/kanban" in out
    assert "list" in out
    assert "show" in out
    # Sanity: should be a chat-friendly size, not the raw usage tree.
    assert len(out) < 2000
    # Shouldn't surface argparse's usage-error sentinel.
    assert "usage error" not in out.lower()


@pytest.mark.parametrize("alias", ["help", "--help", "-h", "?"])
def test_run_slash_help_aliases_match_bare(kanban_home, alias):
    """Every documented help alias produces the same curated output."""
    bare = kc.run_slash("")
    out = kc.run_slash(alias)
    assert out == bare


def test_run_slash_subcommand_help_returns_help_text(kanban_home):
    """`/kanban show -h` returns the actual subcommand help, not a
    fake `(usage error: 0)` sentinel."""
    out = kc.run_slash("show -h")
    assert "task_id" in out
    assert "/kanban show" in out
    assert not out.startswith("⚠")


def test_run_slash_unknown_action_friendly_error(kanban_home):
    """Unknown subcommand surfaces a single-line usage error prefixed
    with our marker — no `(usage error: 2)` wrapping, no doubled
    `kanban kanban` prog string."""
    out = kc.run_slash("frobnicate")
    assert "/kanban" in out
    assert "frobnicate" in out
    assert "/kanban-wrap" not in out
    assert "/kanban kanban" not in out
    assert "(usage error: " not in out


def test_run_slash_missing_required_arg_friendly_error(kanban_home):
    """Missing positional argument shows the subcommand-scoped usage
    line, not the top-level kanban tree."""
    out = kc.run_slash("show")
    assert "/kanban show" in out
    assert "task_id" in out


def test_run_slash_board_override_restores_prior_env(kanban_home, monkeypatch):
    kb.create_board("alpha")
    kb.create_board("beta")
    monkeypatch.setenv("HERMES_KANBAN_BOARD", "beta")

    kc.run_slash("--board alpha list")

    assert os.environ.get("HERMES_KANBAN_BOARD") == "beta"


def test_run_slash_board_override_does_not_change_boards_show_current(kanban_home):
    kb.create_board("alpha")
    kb.create_board("beta")
    kb.set_current_board("alpha")

    out = kc.run_slash("--board beta boards show")

    assert "Current board: alpha" in out


def _planner_task(
    title: str,
    *,
    status: str = "ready",
    body: str | None = None,
    task_id: str = "t_test",
) -> kb.Task:
    return kb.Task(
        id=task_id,
        title=title,
        body=body,
        assignee=None,
        status=status,
        priority=0,
        created_by="test",
        created_at=0,
        started_at=None,
        completed_at=None,
        workspace_kind="scratch",
        workspace_path=None,
        claim_lock=None,
        claim_expires=None,
        tenant=None,
    )


@pytest.mark.parametrize(
    "task,gate_open,expected",
    [
        (_planner_task("[Backlog] idea"), False, "backlog-never-run"),
        (_planner_task("[Planning] design doc"), False, "ready-for-design"),
        (_planner_task("[High-Risk] touch runtime"), False, "high-risk-needs-human"),
        (_planner_task("No prefix card"), False, "not-ready"),
        (
            _planner_task(
                "[Implementation] build planner",
                body="mode: implementation-no-commit",
            ),
            False,
            "blocked-by-gate",
        ),
    ],
)
def test_classify_planner_task_minimal_rules(task, gate_open, expected):
    row = kc._classify_planner_task(task, gate_open=gate_open)
    assert row["classification"] == expected


def test_planner_report_adds_ready_for_push_candidate_when_ahead():
    report = kc._planner_report(
        [],
        board="hermes-product",
        gate_open=False,
        git_summary={
            "workdir": "/repo",
            "branch": "main",
            "ahead_count": 2,
            "dirty_worktree": False,
            "status_summary": "clean",
            "errors": [],
        },
    )
    assert report["candidates"][0]["classification"] == "ready-for-push"
    assert report["candidates"][0]["required_mode"] == "push-only"


def test_planner_report_adds_ready_for_review_commit_candidate_when_dirty():
    report = kc._planner_report(
        [],
        board="hermes-product",
        gate_open=False,
        git_summary={
            "workdir": "/repo",
            "branch": "main",
            "ahead_count": 0,
            "dirty_worktree": True,
            "status_summary": "dirty (1 path)",
            "errors": [],
        },
    )
    assert report["candidates"][0]["classification"] == "ready-for-review-commit"
    assert report["candidates"][0]["risk_level"] == "medium"


def test_planner_report_returns_zero_candidates_without_ready_running_or_git_signal():
    report = kc._planner_report(
        [_planner_task("[Planning] draft", status="todo")],
        board="hermes-product",
        gate_open=False,
        git_summary={
            "workdir": "/repo",
            "branch": "main",
            "ahead_count": 0,
            "dirty_worktree": False,
            "status_summary": "clean",
            "errors": [],
        },
    )
    assert report["candidates"] == []


def test_classify_planner_task_done_uses_needs_close_evidence():
    row = kc._classify_planner_task(
        _planner_task("[Implementation] shipped", status="done", body="mode: implementation-no-commit"),
        gate_open=False,
    )
    assert row["classification"] == "needs-close-evidence"
    assert row["blocked_reason"] == "done state alone is not proof of artifact / commit / push evidence"


def test_run_slash_planner_output_contains_required_sections(kanban_home, monkeypatch):
    monkeypatch.setattr(
        kc,
        "_planner_git_summary",
        lambda **kwargs: {
            "workdir": kwargs["workdir"],
            "branch": "main",
            "ahead_count": 0,
            "dirty_worktree": False,
            "status_summary": "clean",
            "errors": [],
        },
    )
    out = kc.run_slash("planner")
    assert "board summary:" in out
    assert "candidate ranking:" in out
    assert "must-not-run list:" in out


def test_run_slash_planner_does_not_call_kanban_mutation_functions(kanban_home, monkeypatch):
    monkeypatch.setattr(
        kc,
        "_planner_git_summary",
        lambda **kwargs: {
            "workdir": kwargs["workdir"],
            "branch": "main",
            "ahead_count": 0,
            "dirty_worktree": False,
            "status_summary": "clean",
            "errors": [],
        },
    )

    def _boom(*args, **kwargs):
        raise AssertionError("mutation function should not be called")

    monkeypatch.setattr(kb, "create_task", _boom)
    monkeypatch.setattr(kb, "assign_task", _boom)
    monkeypatch.setattr(kb, "complete_task", _boom)
    monkeypatch.setattr(kb, "block_task", _boom)
    monkeypatch.setattr(kb, "unblock_task", _boom)

    out = kc.run_slash("planner")
    assert "mode: planner-read-only" in out


def test_run_slash_planner_json_schema_is_stable(kanban_home, monkeypatch):
    monkeypatch.setattr(
        kc,
        "_planner_git_summary",
        lambda **kwargs: {
            "workdir": kwargs["workdir"],
            "branch": "main",
            "ahead_count": 2,
            "dirty_worktree": True,
            "status_summary": "dirty (1 path)",
            "git_available": True,
            "errors": [],
        },
    )

    with kb.connect_closing() as conn:
        kb.create_task(
            conn,
            title="[Implementation] planner json",
            body="mode: implementation-no-commit",
            created_by="test",
        )

    raw = kc.run_slash("planner --json")
    data = json.loads(raw)

    assert data["schema_version"] == "planner.v1"
    assert data["mode"] == "planner-read-only"
    assert set(data.keys()) >= {
        "schema_version",
        "mode",
        "board_summary",
        "git_summary",
        "gate_assumption",
        "candidates",
        "classification",
        "must_not_run",
        "notes",
    }
    assert data["board_summary"]["board"] == kb.get_current_board()
    assert data["git_summary"]["ahead_count"] == 2
    assert data["git_summary"]["dirty_worktree"] is True
    assert [row["task_id"] for row in data["candidates"][:2]] == ["git:ahead", "git:dirty"]
    assert all(
        set(row.keys()) >= {
            "task_id",
            "title",
            "status",
            "classification",
            "required_mode",
            "risk_level",
            "reason",
            "blocked_reason",
            "next_human_approval",
        }
        for row in data["candidates"]
    )
    assert any(
        set(row.keys()) >= {
            "task_id",
            "title",
            "status",
            "prefix",
            "mode",
            "classification",
            "required_mode",
            "risk_level",
            "reason",
            "blocked_reason",
            "next_human_approval",
            "candidate",
        }
        for row in data["classification"]
    )
    assert "Planner is read-only: no Kanban mutation, no Git mutation, no file edits" in data["must_not_run"]


def test_planner_report_docstring_describes_planner_v1_contract():
    doc = kc._planner_report.__doc__ or ""
    assert 'schema_version is always "planner.v1"' in doc
    assert "canonical keys are mode, board_summary, git_summary, gate_assumption," in doc
    assert "candidates, classification, must_not_run, and notes" in doc
    assert "candidates is the ranked first-look list for dispatcher/watchdog readers" in doc
    assert "classification is the full-task audit list" in doc
    assert "git_summary contains read-only git signals only" in doc
    assert "gate_assumption is an operator assumption, not runtime truth" in doc
    assert "planner does not perform Kanban mutation, Git mutation, or dispatcher dispatch" in doc


def test_require_planner_v1_accepts_planner_v1_report():
    report = {"schema_version": "planner.v1", "mode": "planner-read-only"}
    assert kc._require_planner_v1(report) is report


@pytest.mark.parametrize("report", [{}, {"schema_version": None}, {"schema_version": "planner.v0"}, {"schema_version": "unexpected"}])
def test_require_planner_v1_rejects_missing_or_unknown_schema(report):
    with pytest.raises(ValueError, match="planner report schema mismatch"):
        kc._require_planner_v1(report)



def test_planner_git_summary_uses_read_only_git_commands_only(monkeypatch, tmp_path):
    seen: list[list[str]] = []

    class _CP:
        def __init__(self, args, stdout="", stderr="", returncode=0):
            self.args = args
            self.stdout = stdout
            self.stderr = stderr
            self.returncode = returncode

    def fake_run(cmd, **kwargs):
        seen.append(list(cmd))
        assert cmd[:2] in (
            ["git", "status"],
            ["git", "branch"],
            ["git", "rev-list"],
        )
        assert all(part not in {"add", "commit", "push", "reset", "checkout", "merge", "rebase"} for part in cmd)
        if cmd[:2] == ["git", "status"]:
            return _CP(cmd, stdout="")
        if cmd[:2] == ["git", "branch"]:
            return _CP(cmd, stdout="main\n")
        return _CP(cmd, stdout="0\n")

    monkeypatch.setattr(kc.subprocess, "run", fake_run)
    summary = kc._planner_git_summary(workdir=str(tmp_path))
    assert summary["branch"] == "main"
    assert summary["ahead_count"] == 0
    assert summary["dirty_worktree"] is False
    assert len(seen) == 3


def _planner_git_summary_stub(*, ahead_count=0, dirty_worktree=False):
    return {
        "workdir": "/repo",
        "branch": "main",
        "ahead_count": ahead_count,
        "dirty_worktree": dirty_worktree,
        "status_summary": "dirty" if dirty_worktree else "clean",
        "git_available": True,
        "errors": [],
    }


def test_planner_consumer_preview_reads_planner_v1_first_candidate():
    report = kc._planner_report(
        [_planner_task("[Planning] draft", status="ready", task_id="t_preview")],
        board="hermes-product",
        gate_open=True,
        git_summary=_planner_git_summary_stub(),
    )
    preview = kc._planner_consumer_preview(report)

    assert preview["source_schema_version"] == "planner.v1"
    assert preview["mode"] == "planner-consumer-preview-read-only"
    assert preview["dispatch_allowed"] is False
    assert preview["selected_candidate"] == {
        "task_id": "t_preview",
        "title": "[Planning] draft",
        "classification": "ready-for-design",
        "required_mode": "N/A",
        "risk_level": "low",
        "blocked_reason": "N/A",
        "next_human_approval": "Approve the exact design/doc scope before mutation",
    }
    assert "Planner is read-only: no Kanban mutation, no Git mutation, no file edits" in preview["must_not_run"]


@pytest.mark.parametrize("report", [{}, {"schema_version": "planner.v0"}, {"schema_version": "unexpected"}])
def test_planner_consumer_preview_rejects_unknown_schema(report):
    with pytest.raises(ValueError, match="planner report schema mismatch"):
        kc._planner_consumer_preview(report)


def test_planner_consumer_preview_empty_candidates_is_safe_noop():
    report = kc._planner_report(
        [],
        board="hermes-product",
        gate_open=True,
        git_summary=_planner_git_summary_stub(),
    )
    preview = kc._planner_consumer_preview(report)

    assert preview["safe_noop"] is True
    assert preview["selected_candidate"] is None
    assert preview["dispatch_allowed"] is False
    assert preview["dispatch_blocked_reason"] == "no candidates; safe no-op preview"


def test_planner_consumer_preview_gate_closed_blocks_dispatch():
    report = kc._planner_report(
        [_planner_task("[Planning] draft", status="ready")],
        board="hermes-product",
        gate_open=False,
        git_summary=_planner_git_summary_stub(),
    )
    preview = kc._planner_consumer_preview(report)
    text = kc._format_planner_consumer_preview(preview)

    assert preview["gate_assumption"] == "closed"
    assert preview["dispatch_allowed"] is False
    assert preview["dispatch_blocked_reason"] == "gate_assumption is closed; read-only preview cannot dispatch"
    assert "dispatch allowed: no" in text
    assert "gate_assumption is closed" in text


def test_run_slash_planner_preview_does_not_call_kanban_mutation_functions(kanban_home, monkeypatch):
    monkeypatch.setattr(kc, "_planner_git_summary", lambda **kwargs: _planner_git_summary_stub())

    def _boom(*args, **kwargs):
        raise AssertionError("mutation function should not be called")

    monkeypatch.setattr(kb, "create_task", _boom)
    monkeypatch.setattr(kb, "assign_task", _boom)
    monkeypatch.setattr(kb, "complete_task", _boom)
    monkeypatch.setattr(kb, "block_task", _boom)
    monkeypatch.setattr(kb, "unblock_task", _boom)

    out = kc.run_slash("planner-preview")
    assert "mode: planner-consumer-preview-read-only" in out
    assert "dispatch allowed: no" in out


def test_run_slash_planner_preview_json_shape(kanban_home, monkeypatch):
    monkeypatch.setattr(kc, "_planner_git_summary", lambda **kwargs: _planner_git_summary_stub(dirty_worktree=True))
    raw = kc.run_slash("planner-preview --json")
    data = json.loads(raw)

    assert data["schema_version"] == "planner-consumer-preview.v1"
    assert data["source_schema_version"] == "planner.v1"
    assert data["selected_candidate"]["task_id"] == "git:dirty"
    assert set(data["selected_candidate"].keys()) == {
        "task_id",
        "title",
        "classification",
        "required_mode",
        "risk_level",
        "blocked_reason",
        "next_human_approval",
    }


def _planner_dispatch_report(*, gate_open=True, tasks=None, git_summary=None):
    return kc._planner_report(
        tasks or [],
        board="hermes-product",
        gate_open=gate_open,
        git_summary=git_summary or _planner_git_summary_stub(),
    )


def test_require_planner_dispatch_input_accepts_planner_v1_report():
    report = _planner_dispatch_report()
    assert kc._require_planner_dispatch_input(report) is report


@pytest.mark.parametrize(
    "report,match",
    [
        ({"schema_version": "planner-consumer-preview.v1"}, "planner dispatch input schema mismatch"),
        ({"schema_version": "planner.v0"}, "planner dispatch input schema mismatch"),
        ({"schema_version": "planner.v1"}, "missing required planner dispatch keys"),
    ],
)
def test_require_planner_dispatch_input_rejects_preview_schema_mismatch_and_missing_keys(report, match):
    with pytest.raises(ValueError, match=match):
        kc._require_planner_dispatch_input(report)


@pytest.mark.parametrize(
    "candidate,gate_assumption,runtime_mode,human_approval,expected_decision,expected_allowed,expected_reason",
    [
        (
            {"task_id": "design", "classification": "ready-for-design", "required_mode": "N/A", "risk_level": "low"},
            "closed",
            "design-no-commit",
            False,
            "allow",
            True,
            "ready-for-design-allowed",
        ),
        (
            {
                "task_id": "doc",
                "classification": "ready-for-design-doc",
                "required_mode": "design-doc-commit-only",
                "risk_level": "low",
            },
            "closed",
            "design-doc-commit-only",
            False,
            "allow",
            True,
            "ready-for-design-doc-allowed",
        ),
        (
            {
                "task_id": "impl",
                "classification": "ready-for-implementation-no-commit",
                "required_mode": "implementation-no-commit",
                "risk_level": "low",
            },
            "open",
            "implementation-no-commit",
            False,
            "allow",
            True,
            "ready-for-implementation-no-commit-allowed",
        ),
        (
            {
                "task_id": "impl",
                "classification": "ready-for-implementation-no-commit",
                "required_mode": "implementation-no-commit",
                "risk_level": "low",
            },
            "closed",
            "implementation-no-commit",
            False,
            "reject",
            False,
            "gate-closed",
        ),
        (
            {
                "task_id": "impl",
                "classification": "ready-for-implementation-no-commit",
                "required_mode": "implementation-no-commit",
                "risk_level": "low",
            },
            "open",
            "implementation-review-commit",
            False,
            "reject",
            False,
            "mode-mismatch",
        ),
        (
            {
                "task_id": "sync",
                "classification": "ready-for-kanban-sync",
                "required_mode": "kanban-sync-only",
                "risk_level": "low",
            },
            "open",
            "kanban-sync-only",
            True,
            "reject",
            False,
            "kanban-sync-unsupported",
        ),
        (
            {
                "task_id": "review",
                "classification": "ready-for-review-commit",
                "required_mode": "implementation-review-commit",
                "risk_level": "medium",
            },
            "open",
            "implementation-review-commit",
            False,
            "needs-human",
            False,
            "human-approval-required",
        ),
        (
            {
                "task_id": "review",
                "classification": "ready-for-review-commit",
                "required_mode": "implementation-review-commit",
                "risk_level": "medium",
            },
            "closed",
            "implementation-review-commit",
            True,
            "reject",
            False,
            "gate-closed",
        ),
        (
            {
                "task_id": "push",
                "classification": "ready-for-push",
                "required_mode": "push-only",
                "risk_level": "medium",
            },
            "open",
            "push-only",
            True,
            "allow",
            True,
            "ready-for-push-allowed",
        ),
        (
            {
                "task_id": "danger",
                "classification": "high-risk-needs-human",
                "required_mode": "N/A",
                "risk_level": "high",
            },
            "open",
            "implementation-no-commit",
            True,
            "reject",
            False,
            "high-risk-never-auto-allow",
        ),
    ],
)
def test_pre_gate_decision_for_candidate_table(
    candidate,
    gate_assumption,
    runtime_mode,
    human_approval,
    expected_decision,
    expected_allowed,
    expected_reason,
):
    decision = kc._pre_gate_decision_for_candidate(
        candidate,
        gate_assumption=gate_assumption,
        runtime_mode=runtime_mode,
        human_approval=human_approval,
    )

    assert decision["decision"] == expected_decision
    assert decision["allowed"] is expected_allowed
    assert decision["reason_code"] == expected_reason
    assert decision["candidate_task_id"] == candidate["task_id"]
    assert decision["runtime_mode"] == runtime_mode
    assert decision["required_mode"] == candidate["required_mode"]
    assert decision["classification"] == candidate["classification"]
    assert decision["risk_level"] == candidate["risk_level"]


def test_select_dispatchable_candidate_returns_first_allowed_candidate():
    report = _planner_dispatch_report(
        gate_open=True,
        tasks=[
            _planner_task("[High-Risk] dangerous", task_id="t_high"),
            _planner_task("[Planning] design", task_id="t_design"),
        ],
    )

    decision = kc._select_dispatchable_candidate(
        report,
        runtime_mode="design-no-commit",
        human_approval=False,
    )

    assert decision["decision"] == "allow"
    assert decision["allowed"] is True
    assert decision["candidate_task_id"] == "t_design"


def test_select_dispatchable_candidate_returns_needs_human_before_later_allowed_candidate():
    report = _planner_dispatch_report(
        gate_open=True,
        tasks=[
            _planner_task("[Implementation] review", body="mode: implementation-review-commit", task_id="t_review"),
            _planner_task("[Planning] design", task_id="t_design"),
        ],
    )

    decision = kc._select_dispatchable_candidate(
        report,
        runtime_mode="implementation-review-commit",
        human_approval=False,
    )

    assert decision["decision"] == "needs-human"
    assert decision["allowed"] is False
    assert decision["candidate_task_id"] == "t_review"


def test_select_dispatchable_candidate_empty_candidates_is_safe_noop():
    report = _planner_dispatch_report()

    decision = kc._select_dispatchable_candidate(
        report,
        runtime_mode="design-no-commit",
        human_approval=False,
    )

    assert decision["decision"] == "reject"
    assert decision["allowed"] is False
    assert decision["reason_code"] == "safe-noop-no-candidates"
    assert decision["candidate_task_id"] == "N/A"


def test_pre_gate_preview_reads_planner_v1_report_and_allows_matching_runtime():
    report = _planner_dispatch_report(
        gate_open=True,
        tasks=[
            _planner_task(
                "[Implementation] build planner",
                body="mode: implementation-no-commit",
                task_id="t_impl",
            )
        ],
    )

    preview = kc._pre_gate_preview(
        report,
        runtime_mode="implementation-no-commit",
        human_approval=False,
    )

    assert preview["schema_version"] == "pre-gate-preview.v1"
    assert preview["source_schema_version"] == "planner.v1"
    assert preview["runtime_mode"] == "implementation-no-commit"
    assert preview["human_approval"] is False
    assert preview["decision"] == "allow"
    assert preview["allowed"] is True
    assert preview["reason_code"] == "ready-for-implementation-no-commit-allowed"
    assert preview["candidate_task_id"] == "t_impl"
    assert preview["classification"] == "ready-for-implementation-no-commit"
    assert preview["required_mode"] == "implementation-no-commit"
    assert preview["risk_level"] == "low"


def test_pre_gate_preview_runtime_mode_mismatch_rejects():
    report = _planner_dispatch_report(
        gate_open=True,
        tasks=[
            _planner_task(
                "[Implementation] build planner",
                body="mode: implementation-no-commit",
                task_id="t_impl",
            )
        ],
    )

    preview = kc._pre_gate_preview(
        report,
        runtime_mode="implementation-review-commit",
        human_approval=False,
    )

    assert preview["decision"] == "reject"
    assert preview["allowed"] is False
    assert preview["reason_code"] == "mode-mismatch"
    assert preview["candidate_task_id"] == "t_impl"


def test_pre_gate_preview_review_commit_requires_human_approval():
    report = _planner_dispatch_report(
        gate_open=True,
        tasks=[
            _planner_task(
                "[Implementation] review",
                body="mode: implementation-review-commit",
                task_id="t_review",
            )
        ],
    )

    preview = kc._pre_gate_preview(
        report,
        runtime_mode="implementation-review-commit",
        human_approval=False,
    )

    assert preview["decision"] == "needs-human"
    assert preview["allowed"] is False
    assert preview["reason_code"] == "human-approval-required"
    assert preview["classification"] == "ready-for-review-commit"


def test_pre_gate_preview_empty_candidates_is_safe_noop():
    report = _planner_dispatch_report()

    preview = kc._pre_gate_preview(
        report,
        runtime_mode="design-no-commit",
        human_approval=False,
    )

    assert preview["decision"] == "reject"
    assert preview["allowed"] is False
    assert preview["reason_code"] == "safe-noop-no-candidates"
    assert preview["candidate_task_id"] == "N/A"


def test_run_slash_pre_gate_preview_json_shape(kanban_home, monkeypatch):
    monkeypatch.setattr(kc, "_planner_git_summary", lambda **kwargs: _planner_git_summary_stub())

    with kb.connect_closing() as conn:
        kb.create_task(
            conn,
            title="[Implementation] build planner",
            body="mode: implementation-no-commit",
            created_by="test",
            initial_status="running",
        )

    raw = kc.run_slash("pre-gate-preview --runtime-mode implementation-no-commit --gate-assumption open --json")
    data = json.loads(raw)

    assert set(data.keys()) == {
        "schema_version",
        "source_schema_version",
        "runtime_mode",
        "human_approval",
        "gate_assumption",
        "decision",
        "allowed",
        "reason_code",
        "reason_text",
        "candidate_task_id",
        "classification",
        "required_mode",
        "risk_level",
        "evaluated_candidates",
        "must_not_run",
    }
    assert data["schema_version"] == "pre-gate-preview.v1"
    assert data["source_schema_version"] == "planner.v1"
    assert data["runtime_mode"] == "implementation-no-commit"
    assert data["human_approval"] is False
    assert data["gate_assumption"] == "open"
    assert data["classification"] == "ready-for-implementation-no-commit"
    assert data["required_mode"] == "implementation-no-commit"
    assert data["risk_level"] == "low"
    assert isinstance(data["evaluated_candidates"], list)


def test_run_slash_pre_gate_preview_does_not_call_kanban_mutation_functions(kanban_home, monkeypatch):
    monkeypatch.setattr(kc, "_planner_git_summary", lambda **kwargs: _planner_git_summary_stub())

    with kb.connect_closing() as conn:
        kb.create_task(
            conn,
            title="[Implementation] build planner",
            body="mode: implementation-no-commit",
            created_by="test",
            initial_status="running",
        )

    def _boom(*args, **kwargs):
        raise AssertionError("mutation function should not be called")

    monkeypatch.setattr(kb, "assign_task", _boom)
    monkeypatch.setattr(kb, "complete_task", _boom)
    monkeypatch.setattr(kb, "block_task", _boom)
    monkeypatch.setattr(kb, "unblock_task", _boom)

    out = kc.run_slash("pre-gate-preview --runtime-mode implementation-no-commit --gate-assumption open")
    assert "schema_version: pre-gate-preview.v1" in out
    assert "decision: allow" in out
    assert "allowed: true" in out


def test_pre_gate_helpers_do_not_call_mutation_functions(monkeypatch):
    report = _planner_dispatch_report(tasks=[_planner_task("[Planning] design", task_id="t_design")])

    def _boom(*args, **kwargs):
        raise AssertionError("mutation function should not be called")

    monkeypatch.setattr(kb, "create_task", _boom)
    monkeypatch.setattr(kb, "assign_task", _boom)
    monkeypatch.setattr(kb, "complete_task", _boom)
    monkeypatch.setattr(kb, "block_task", _boom)
    monkeypatch.setattr(kb, "unblock_task", _boom)

    decision = kc._select_dispatchable_candidate(
        report,
        runtime_mode="design-no-commit",
        human_approval=False,
    )
    assert decision["decision"] == "allow"
