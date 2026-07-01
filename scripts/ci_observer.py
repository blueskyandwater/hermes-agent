#!/usr/bin/env python3
"""Read-only GitHub Actions CI observer.

Collects workflow runs for a branch/commit or a single run id, classifies CI state,
extracts concise failed-log evidence, and recommends one minimal next action.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Sequence
from urllib.parse import quote

MODE = "read-only"
DEFAULT_BRANCH = "main"
MAX_DECISIVE_LINES = 8

CLASSIFICATIONS = {
    "all_green",
    "still_running",
    "failed_lint",
    "failed_tests",
    "failed_nix",
    "failed_unrelated",
    "mixed",
    "no_matching_runs",
}

ROOT_CAUSES = {
    "none",
    "stale_npm_lockfile_hash",
    "nix_hash_diagnose_crashed",
    "other_nix_build_failure",
    "lint_failure",
    "test_failure",
    "infra_transient",
    "workflow_not_triggered",
    "unknown",
}

MUTATING_TOKENS = {
    "add",
    "commit",
    "push",
    "rerun",
    "run",  # e.g. gh workflow run. gh run list/view is allowed below.
    "workflow",
    "pr",
    "merge",
    "create",
    "edit",
    "delete",
    "dispatch",
    "approve",
}

ALLOWED_COMMAND_PREFIXES: tuple[tuple[str, ...], ...] = (
    ("gh", "run", "list"),
    ("gh", "run", "view"),
    ("gh", "api"),
    ("git", "status"),
    ("git", "config"),
)

EXPECTED_OPTIONAL_WORKFLOWS = {"Docker Build and Publish"}


@dataclass
class WorkflowObservation:
    workflow_name: str
    run_id: int | None
    status: str | None
    conclusion: str | None
    url: str | None
    classification: str
    decisive_lines: list[str] = field(default_factory=list)
    root_cause_category: str = "none"
    next_minimal_action: str = "none"
    jobs: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ObserverResult:
    mode: str
    branch: str | None
    commit_sha: str | None
    workflow_filter: str | None
    run_id: int | None
    overall_classification: str
    summary: dict[str, int]
    workflows: list[WorkflowObservation]
    missing_expected_workflows: list[dict[str, str]]
    repo_status: str
    errors: list[str] = field(default_factory=list)


class ReadOnlyCommandError(RuntimeError):
    pass


def _is_allowed_command(argv: Sequence[str]) -> bool:
    if not argv:
        return False
    parts = tuple(argv[:3])
    if not any(parts[: len(prefix)] == prefix for prefix in ALLOWED_COMMAND_PREFIXES):
        return False

    if len(argv) >= 3 and argv[:3] == ["gh", "run", "list"]:
        return True
    if len(argv) >= 3 and argv[:3] == ["gh", "run", "view"]:
        return "--log-failed" in argv or "--json" in argv
    if len(argv) >= 2 and argv[:2] == ["gh", "api"]:
        # gh api is GET unless a method/body flag is supplied.
        forbidden_api_flags = {"--method", "-X", "--field", "-f", "--raw-field", "-F", "--input"}
        return not any(arg in forbidden_api_flags for arg in argv)
    if len(argv) >= 2 and argv[:2] == ["git", "status"]:
        return True
    if len(argv) >= 2 and argv[:2] == ["git", "config"]:
        return list(argv) == ["git", "config", "--get", "remote.origin.url"]
    return False


def run_read_only(argv: Sequence[str], *, timeout: int = 120) -> str:
    """Run a whitelisted read-only command and return stdout."""
    if not _is_allowed_command(argv):
        raise ReadOnlyCommandError(f"Refusing non-read-only command: {' '.join(argv)}")

    result = subprocess.run(
        list(argv),
        check=False,
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        stdout = result.stdout.strip()
        detail = stderr or stdout or f"exit code {result.returncode}"
        raise RuntimeError(f"Command failed ({' '.join(argv)}): {detail}")
    return result.stdout


def normalize_run(raw: dict[str, Any]) -> dict[str, Any]:
    run_id = raw.get("databaseId") or raw.get("id")
    name = raw.get("workflowName") or raw.get("name") or raw.get("workflow_name") or "unknown"
    return {
        "workflow_name": name,
        "run_id": int(run_id) if run_id is not None else None,
        "status": raw.get("status"),
        "conclusion": raw.get("conclusion"),
        "url": raw.get("url") or raw.get("html_url"),
        "head_sha": raw.get("headSha") or raw.get("head_sha"),
        "display_title": raw.get("displayTitle") or raw.get("display_title"),
        "jobs": raw.get("jobs") or [],
    }


def current_repo_slug() -> str:
    """Return owner/repo from origin without mutating git state."""
    origin = run_read_only(["git", "config", "--get", "remote.origin.url"]).strip()
    match = re.search(r"github\.com[:/]([^/]+)/([^/.]+)(?:\.git)?$", origin)
    if not match:
        raise RuntimeError(f"Could not parse GitHub origin remote: {origin}")
    return f"{match.group(1)}/{match.group(2)}"


def resolve_commit_sha(commit: str) -> str:
    """Resolve a full commit SHA from a full SHA or unique prefix using read-only GitHub REST API."""
    if len(commit) >= 40:
        return commit
    payload = json.loads(run_read_only(["gh", "api", f"repos/{current_repo_slug()}/commits/{quote(commit)}"]))
    resolved = payload.get("sha") if isinstance(payload, dict) else None
    return str(resolved or commit)


def fetch_runs_for_commit(branch: str, commit: str, workflow: str | None, *, max_pages: int = 10) -> list[dict[str, Any]]:
    """Fetch runs for a commit using read-only GitHub REST API pagination.

    GitHub's REST list-runs endpoint does not reliably honor head_sha in all gh/API
    versions, so this avoids the old fixed `gh run list --limit 50` window by
    paging branch-scoped runs in 100-run chunks and filtering by the resolved SHA.
    """
    resolved_commit = resolve_commit_sha(commit)
    matched: list[dict[str, Any]] = []
    for page in range(1, max_pages + 1):
        query = f"branch={quote(branch)}&per_page=100&page={page}"
        payload = json.loads(run_read_only(["gh", "api", f"repos/{current_repo_slug()}/actions/runs?{query}"]))
        raw_runs = payload.get("workflow_runs", []) if isinstance(payload, dict) else payload
        if not raw_runs:
            break
        normalized = [normalize_run(item) for item in raw_runs]
        matched.extend(run for run in normalized if str(run.get("head_sha") or "").startswith(resolved_commit))
        if matched:
            break
    if workflow:
        workflow_lower = workflow.lower()
        matched = [run for run in matched if workflow_lower in str(run.get("workflow_name") or "").lower()]
    return matched


def fetch_run_by_id(run_id: int) -> dict[str, Any]:
    fields = "databaseId,workflowName,headSha,status,conclusion,url,displayTitle,jobs"
    raw = json.loads(run_read_only(["gh", "run", "view", str(run_id), "--json", fields]))
    return normalize_run(raw)


def fetch_failed_log(run_id: int) -> str:
    return run_read_only(["gh", "run", "view", str(run_id), "--log-failed"], timeout=180)


def git_status() -> str:
    return run_read_only(["git", "status", "-sb"]).strip()


def workflow_kind(workflow_name: str) -> str:
    lower = workflow_name.lower()
    if "nix" in lower:
        return "nix"
    if "lint" in lower or "ruff" in lower or "ty" in lower:
        return "lint"
    if "test" in lower or "pytest" in lower:
        return "tests"
    return "other"


def extract_decisive_lines(log_text: str, *, limit: int = MAX_DECISIVE_LINES) -> list[str]:
    keywords = (
        "::error::",
        "error:",
        "failed",
        "failure",
        "hash mismatch",
        "specified:",
        "got:",
        "stale npm lockfile hash",
        "fix-lockfiles",
        "REPORT_EOF",
        "Invalid format",
        "file command",
        "Traceback",
        "AssertionError",
        "Process completed with exit code",
    )
    lines: list[str] = []
    seen: set[str] = set()
    for raw_line in log_text.splitlines():
        line = raw_line.strip().lstrip("\ufeff")
        # gh prefixes tab-separated job/step/timestamp columns; keep the useful tail.
        if "\t" in line:
            parts = [part for part in line.split("\t") if part]
            if parts:
                line = parts[-1].strip()
        if not line:
            continue
        lower = line.lower()
        if any(keyword.lower() in lower for keyword in keywords) and line not in seen:
            lines.append(line)
            seen.add(line)
        if len(lines) >= limit:
            break
    return lines


def classify_root_cause(workflow_name: str, log_text: str, decisive_lines: Sequence[str]) -> str:
    kind = workflow_kind(workflow_name)
    lower_log = log_text.lower()
    joined_decisive = "\n".join(decisive_lines).lower()
    combined = f"{lower_log}\n{joined_decisive}"

    infra_markers = ("rate limit", "timed out", "timeout", "connection reset", "network is unreachable")
    if any(marker in combined for marker in infra_markers):
        return "infra_transient"

    if kind == "nix":
        if "report_eof" in combined or "file command" in combined or "invalid format" in combined:
            return "nix_hash_diagnose_crashed"
        stale_markers = (
            "hash mismatch",
            "specified:",
            "got:",
            "stale npm lockfile hash",
            "fix-lockfiles",
        )
        if any(marker in combined for marker in stale_markers):
            return "stale_npm_lockfile_hash"
        if decisive_lines:
            return "other_nix_build_failure"
        return "unknown"

    if kind == "lint":
        return "lint_failure"
    if kind == "tests":
        return "test_failure"
    return "unknown"


def next_action(root_cause: str, classification: str) -> str:
    actions = {
        "none": "none",
        "stale_npm_lockfile_hash": "run nix run .#fix-lockfiles locally, inspect the diff, then commit only if intended",
        "nix_hash_diagnose_crashed": "inspect the Nix diagnostic step output and file-command formatting",
        "other_nix_build_failure": "inspect the failed Nix log around the decisive lines",
        "lint_failure": "run the matching lint command locally and fix the reported file(s)",
        "test_failure": "run the failed test target locally and inspect the first failing assertion",
        "infra_transient": "wait briefly and consider a manual rerun only after human approval",
        "workflow_not_triggered": "confirm workflow path filters and expected trigger conditions",
        "unknown": "inspect the failed log manually for the first actionable error",
    }
    if classification == "still_running":
        return "wait_for_running_jobs"
    return actions.get(root_cause, "inspect_failed_log")


def classify_workflow(run: dict[str, Any], log_text: str | None = None) -> WorkflowObservation:
    workflow_name = run["workflow_name"]
    status = run.get("status")
    conclusion = run.get("conclusion")
    if status in {"queued", "in_progress", "waiting", "requested", "pending"}:
        classification = "still_running"
        root_cause = "none"
        decisive_lines: list[str] = []
    elif status == "completed" and conclusion == "success":
        classification = "green"
        root_cause = "none"
        decisive_lines = []
    elif status == "completed" and conclusion in {"failure", "timed_out", "cancelled", "action_required", "startup_failure"}:
        kind = workflow_kind(workflow_name)
        classification = {
            "nix": "failed_nix",
            "lint": "failed_lint",
            "tests": "failed_tests",
        }.get(kind, "failed_unrelated")
        decisive_lines = extract_decisive_lines(log_text or "")
        root_cause = classify_root_cause(workflow_name, log_text or "", decisive_lines)
    else:
        classification = "failed_unrelated"
        decisive_lines = extract_decisive_lines(log_text or "")
        root_cause = classify_root_cause(workflow_name, log_text or "", decisive_lines)

    jobs = []
    for job in run.get("jobs") or []:
        jobs.append(
            {
                "job_name": job.get("name"),
                "status": job.get("status"),
                "conclusion": job.get("conclusion"),
            }
        )

    return WorkflowObservation(
        workflow_name=workflow_name,
        run_id=run.get("run_id"),
        status=status,
        conclusion=conclusion,
        url=run.get("url"),
        classification=classification,
        decisive_lines=decisive_lines,
        root_cause_category=root_cause,
        next_minimal_action=next_action(root_cause, classification),
        jobs=jobs,
    )


def overall_classification(workflows: Sequence[WorkflowObservation]) -> str:
    if not workflows:
        return "no_matching_runs"
    classes = [workflow.classification for workflow in workflows]
    if any(item == "still_running" for item in classes):
        return "still_running"
    failures = [item for item in classes if item.startswith("failed_")]
    if not failures and all(item == "green" for item in classes):
        return "all_green"
    unique_failures = sorted(set(failures))
    if len(unique_failures) == 1:
        return unique_failures[0]
    if failures:
        return "mixed"
    return "mixed"


def summarize(workflows: Sequence[WorkflowObservation], missing_expected: Sequence[dict[str, str]]) -> dict[str, int]:
    return {
        "total_runs": len(workflows),
        "completed_success": sum(1 for wf in workflows if wf.status == "completed" and wf.conclusion == "success"),
        "completed_failed": sum(1 for wf in workflows if wf.status == "completed" and wf.conclusion not in {"success", "skipped", None}),
        "running": sum(1 for wf in workflows if wf.status in {"queued", "in_progress", "waiting", "requested", "pending"}),
        "queued": sum(1 for wf in workflows if wf.status == "queued"),
        "not_applicable": len(missing_expected),
    }


def missing_optional_workflows(observed: Sequence[WorkflowObservation], workflow_filter: str | None) -> list[dict[str, str]]:
    if workflow_filter:
        return []
    observed_names = {wf.workflow_name for wf in observed}
    missing = []
    for name in sorted(EXPECTED_OPTIONAL_WORKFLOWS - observed_names):
        workflow_file_exists = Path(".github/workflows").exists()
        reason = "not observed for this commit; likely path filter or event constraints"
        if not workflow_file_exists:
            reason = "workflow directory not present in current working tree"
        missing.append(
            {
                "workflow_name": name,
                "classification": "not_applicable",
                "root_cause_category": "workflow_not_triggered",
                "reason": reason,
                "next_minimal_action": "none",
            }
        )
    return missing


def observe(args: argparse.Namespace) -> ObserverResult:
    errors: list[str] = []
    runs: list[dict[str, Any]]
    effective_branch: str | None = None

    if args.run_id is not None:
        run = fetch_run_by_id(args.run_id)
        runs = [run]
    else:
        effective_branch = str(args.branch or DEFAULT_BRANCH)
        commit = str(args.commit)
        runs = fetch_runs_for_commit(effective_branch, commit, args.workflow)

    observations: list[WorkflowObservation] = []
    for run in runs:
        log_text = None
        if run.get("status") == "completed" and run.get("conclusion") not in {"success", "skipped", None}:
            try:
                if run.get("run_id") is not None:
                    log_text = fetch_failed_log(int(run["run_id"]))
            except Exception as exc:  # keep observer read-only and useful on partial failures
                errors.append(str(exc))
                log_text = ""
        observations.append(classify_workflow(run, log_text))

    optional_workflow_filter = args.workflow or ("run-id" if args.run_id is not None else None)
    missing_expected = missing_optional_workflows(observations, optional_workflow_filter)
    overall = overall_classification(observations)
    status = ""
    try:
        status = git_status()
    except Exception as exc:
        errors.append(str(exc))

    return ObserverResult(
        mode=MODE,
        branch=effective_branch,
        commit_sha=args.commit or (runs[0].get("head_sha") if runs else None),
        workflow_filter=args.workflow,
        run_id=args.run_id,
        overall_classification=overall,
        summary=summarize(observations, missing_expected),
        workflows=observations,
        missing_expected_workflows=missing_expected,
        repo_status=status,
        errors=errors,
    )


def result_to_dict(result: ObserverResult) -> dict[str, Any]:
    return asdict(result)


def format_text(result: ObserverResult) -> str:
    lines = [
        f"mode: {result.mode}",
        f"classification: {result.overall_classification}",
    ]
    if result.branch:
        lines.append(f"branch: {result.branch}")
    if result.commit_sha:
        lines.append(f"commit: {result.commit_sha}")
    if result.workflow_filter:
        lines.append(f"workflow_filter: {result.workflow_filter}")
    if result.run_id is not None:
        lines.append(f"run_id: {result.run_id}")

    lines.append("")
    lines.append("summary:")
    for key, value in result.summary.items():
        lines.append(f"- {key}: {value}")

    lines.append("")
    lines.append("workflows:")
    if not result.workflows:
        lines.append("- no matching runs")
    for wf in result.workflows:
        run_part = f"#{wf.run_id}" if wf.run_id is not None else "#unknown"
        lines.append(f"- {wf.workflow_name} {run_part}: {wf.status}/{wf.conclusion} ({wf.classification})")
        lines.append(f"  root_cause: {wf.root_cause_category}")
        lines.append(f"  next: {wf.next_minimal_action}")
        if wf.url:
            lines.append(f"  url: {wf.url}")
        if wf.decisive_lines:
            lines.append("  decisive_lines:")
            for line in wf.decisive_lines:
                lines.append(f"  - {line}")

    if result.missing_expected_workflows:
        lines.append("")
        lines.append("not_applicable:")
        for item in result.missing_expected_workflows:
            lines.append(f"- {item['workflow_name']}: {item['reason']}")

    lines.append("")
    lines.append("repo_status:")
    lines.append(result.repo_status or "unknown")

    if result.errors:
        lines.append("")
        lines.append("errors:")
        for error in result.errors:
            lines.append(f"- {error}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only GitHub Actions CI observer")
    parser.add_argument("--branch", default=None, help=f"Branch to inspect, e.g. main (default: {DEFAULT_BRANCH} in commit mode)")
    parser.add_argument("--commit", help="Commit SHA or unique prefix to match")
    parser.add_argument("--workflow", help="Workflow name filter, e.g. Nix")
    parser.add_argument("--run-id", type=int, help="Inspect a single GitHub Actions run id")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format")
    return parser


def validate_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.run_id is None and not args.commit:
        parser.error("provide --run-id or --commit")
    if args.run_id is not None and (args.branch or args.commit or args.workflow):
        parser.error("--run-id cannot be combined with --branch, --commit, or --workflow")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    validate_args(parser, args)
    result = observe(args)
    if args.format == "json":
        print(json.dumps(result_to_dict(result), indent=2, ensure_ascii=False, sort_keys=True))
    else:
        print(format_text(result))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
