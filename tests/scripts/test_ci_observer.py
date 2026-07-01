from __future__ import annotations

import importlib.util
import sys
from argparse import Namespace
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "ci_observer.py"
spec = importlib.util.spec_from_file_location("ci_observer", MODULE_PATH)
assert spec is not None
ci_observer = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = ci_observer
spec.loader.exec_module(ci_observer)


def test_extract_decisive_lines_limits_and_strips_gh_prefixes():
    log = "\n".join(
        [
            "nix\tstep\t2026-01-01T00:00:00Z error: hash mismatch in fixed-output derivation",
            "nix\tstep\t2026-01-01T00:00:01Z specified: sha256-old",
            "nix\tstep\t2026-01-01T00:00:02Z got:       sha256-new",
            "noise line",
            "nix\tstep\t2026-01-01T00:00:03Z ::error::Nix build failed due to stale npm lockfile hash. Run: nix run .#fix-lockfiles",
            "nix\tstep\t2026-01-01T00:00:04Z Process completed with exit code 1.",
        ]
    )

    lines = ci_observer.extract_decisive_lines(log, limit=4)

    assert lines == [
        "2026-01-01T00:00:00Z error: hash mismatch in fixed-output derivation",
        "2026-01-01T00:00:01Z specified: sha256-old",
        "2026-01-01T00:00:02Z got:       sha256-new",
        "2026-01-01T00:00:03Z ::error::Nix build failed due to stale npm lockfile hash. Run: nix run .#fix-lockfiles",
    ]


def test_classify_nix_stale_lockfile_hash():
    log = "error: hash mismatch\nspecified: sha256-old\ngot: sha256-new"
    decisive = ci_observer.extract_decisive_lines(log)

    assert ci_observer.classify_root_cause("Nix", log, decisive) == "stale_npm_lockfile_hash"


def test_classify_nix_diagnose_crash_takes_precedence():
    log = "REPORT_EOF\nUnable to process file command 'output' successfully.\nInvalid format 'got: sha256-new'"
    decisive = ci_observer.extract_decisive_lines(log)

    assert ci_observer.classify_root_cause("Nix", log, decisive) == "nix_hash_diagnose_crashed"


def test_overall_classification_green_running_and_mixed():
    green = ci_observer.WorkflowObservation("Tests", 1, "completed", "success", None, "green")
    running = ci_observer.WorkflowObservation("Nix", 2, "in_progress", None, None, "still_running")
    failed_nix = ci_observer.WorkflowObservation("Nix", 3, "completed", "failure", None, "failed_nix")
    failed_lint = ci_observer.WorkflowObservation("Lint", 4, "completed", "failure", None, "failed_lint")

    assert ci_observer.overall_classification([green]) == "all_green"
    assert ci_observer.overall_classification([green, running]) == "still_running"
    assert ci_observer.overall_classification([failed_nix]) == "failed_nix"
    assert ci_observer.overall_classification([failed_nix, failed_lint]) == "mixed"
    assert ci_observer.overall_classification([]) == "no_matching_runs"


def test_run_read_only_rejects_mutating_commands():
    assert ci_observer._is_allowed_command(["gh", "run", "list", "--json", "databaseId"])
    assert ci_observer._is_allowed_command(["gh", "run", "view", "123", "--log-failed"])
    assert ci_observer._is_allowed_command(["gh", "api", "repos/{owner}/{repo}/actions/runs?head_sha=abc"])
    assert ci_observer._is_allowed_command(["git", "status", "-sb"])
    assert ci_observer._is_allowed_command(["git", "config", "--get", "remote.origin.url"])

    assert not ci_observer._is_allowed_command(["gh", "run", "rerun", "123"])
    assert not ci_observer._is_allowed_command(["gh", "workflow", "run", "Nix"])
    assert not ci_observer._is_allowed_command(["gh", "api", "repos/{owner}/{repo}/dispatches", "--method", "POST"])
    assert not ci_observer._is_allowed_command(["git", "add", "."])
    assert not ci_observer._is_allowed_command(["git", "commit", "-m", "x"])
    assert not ci_observer._is_allowed_command(["git", "push", "origin", "main"])


def test_validate_args_rejects_run_id_with_branch_but_allows_run_id_alone():
    parser = ci_observer.build_parser()

    run_id_only = parser.parse_args(["--run-id", "123"])
    ci_observer.validate_args(parser, run_id_only)

    with pytest.raises(SystemExit):
        args = parser.parse_args(["--run-id", "123", "--branch", "main"])
        ci_observer.validate_args(parser, args)


def test_commit_search_defaults_effective_branch_to_main_and_uses_commit_api(monkeypatch):
    calls: list[tuple[str, ...]] = []

    def fake_run(argv, *, timeout=120):
        calls.append(tuple(argv))
        if argv == ["git", "config", "--get", "remote.origin.url"]:
            return "https://github.com/blueskyandwater/hermes-agent.git\n"
        if argv[:2] == ["gh", "api"] and "/commits/" in argv[2]:
            return '{"sha": "abc123full"}'
        if argv[:2] == ["gh", "api"] and "/actions/runs?" in argv[2]:
            return """
            {
              "workflow_runs": [
                {"id": 10, "name": "Tests", "head_sha": "abc123full", "status": "completed", "conclusion": "success", "html_url": "https://example.test/10"}
              ]
            }
            """
        if argv[:2] == ["git", "status"]:
            return "## main...origin/main\n"
        raise AssertionError(f"unexpected command: {argv}")

    monkeypatch.setattr(ci_observer, "run_read_only", fake_run)
    result = ci_observer.observe(Namespace(branch=None, commit="abc123", workflow=None, run_id=None, format="text"))

    assert result.branch == "main"
    assert result.overall_classification == "all_green"
    api_calls = [call for call in calls if call[:2] == ("gh", "api")]
    assert len(api_calls) == 2
    assert "/commits/abc123" in api_calls[0][2]
    assert "branch=main" in api_calls[1][2]
    assert "per_page=100" in api_calls[1][2]
    assert "page=1" in api_calls[1][2]
    assert not any(call[:3] == ("gh", "run", "list") for call in calls)
    assert not any("--limit" in call for call in api_calls)


def test_workflow_filter_filters_commit_api_results(monkeypatch):
    def fake_run(argv, *, timeout=120):
        if argv == ["git", "config", "--get", "remote.origin.url"]:
            return "https://github.com/blueskyandwater/hermes-agent.git\n"
        if argv[:2] == ["gh", "api"] and "/commits/" in argv[2]:
            return '{"sha": "abc123full"}'
        if argv[:2] == ["gh", "api"] and "/actions/runs?" in argv[2]:
            return """
            {
              "workflow_runs": [
                {"id": 10, "name": "Tests", "head_sha": "abc123full", "status": "completed", "conclusion": "success"},
                {"id": 11, "name": "Nix", "head_sha": "abc123full", "status": "completed", "conclusion": "success"}
              ]
            }
            """
        if argv[:2] == ["git", "status"]:
            return "## main...origin/main\n"
        raise AssertionError(f"unexpected command: {argv}")

    monkeypatch.setattr(ci_observer, "run_read_only", fake_run)
    result = ci_observer.observe(Namespace(branch="main", commit="abc123", workflow="Nix", run_id=None, format="text"))

    assert [workflow.workflow_name for workflow in result.workflows] == ["Nix"]
    assert result.missing_expected_workflows == []


def test_observe_uses_failed_logs_only_for_failed_runs_and_includes_git_status(monkeypatch):
    calls: list[tuple[str, ...]] = []

    def fake_run(argv, *, timeout=120):
        calls.append(tuple(argv))
        if argv == ["git", "config", "--get", "remote.origin.url"]:
            return "https://github.com/blueskyandwater/hermes-agent.git\n"
        if argv[:2] == ["gh", "api"] and "/commits/" in argv[2]:
            return '{"sha": "abc123full"}'
        if argv[:2] == ["gh", "api"] and "/actions/runs?" in argv[2]:
            return """
            {
              "workflow_runs": [
                {"id": 10, "name": "Tests", "head_sha": "abc123full", "status": "completed", "conclusion": "success", "html_url": "https://example.test/10"},
                {"id": 11, "name": "Nix", "head_sha": "abc123full", "status": "completed", "conclusion": "failure", "html_url": "https://example.test/11"}
              ]
            }
            """
        if argv[:3] == ["gh", "run", "view"] and "--log-failed" in argv:
            return "error: hash mismatch\nspecified: sha256-old\ngot: sha256-new"
        if argv[:2] == ["git", "status"]:
            return "## main...origin/main\n"
        raise AssertionError(f"unexpected command: {argv}")

    monkeypatch.setattr(ci_observer, "run_read_only", fake_run)
    result = ci_observer.observe(Namespace(branch="main", commit="abc123", workflow=None, run_id=None, format="text"))

    assert result.mode == "read-only"
    assert result.overall_classification == "failed_nix"
    assert result.repo_status == "## main...origin/main"
    assert result.workflows[1].root_cause_category == "stale_npm_lockfile_hash"
    assert ("gh", "run", "view", "11", "--log-failed") in calls
    assert ("git", "status", "-sb") in calls
    assert not any(call[:2] == ("git", "add") for call in calls)
    assert not any(call[:2] == ("git", "commit") for call in calls)
    assert not any(call[:2] == ("git", "push") for call in calls)
