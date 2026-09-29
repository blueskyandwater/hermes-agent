"""``hermes kanban …`` — dispatch (``kanban_command``), task-verb handlers, ``run_slash`` for ``/kanban``.
DB work lives in ``kanban_db``; siblings: ``kanban_parser`` (argparse, re-exported ``build_parser``),
``kanban_output`` (text/--json), ``kanban_boards`` (``boards …``), ``kanban_ops`` (dispatch/daemon/
tail/watch/gc/repair).
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import shlex
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Optional

from hermes_cli import kanban_db as kb
from hermes_cli import kanban_db_connect as kbc
from hermes_cli import kanban_db_dispatch as kbd
from hermes_cli import kanban_db_workspace as kbw
from hermes_cli import kanban_db_notify as kbn
from hermes_cli import kanban_swarm as ks
from hermes_cli.kanban_output import (
    _ATTACHMENT_FIELDS, _RUNS_RUN_FIELDS, _SHOW_RUN_FIELDS, _bulk_apply, _err,
    _fmt_counts, _fmt_task_line, _fmt_ts, _json_out, _obj_dict, _print_json,
    _task_to_dict,
)
from hermes_cli.kanban_boards import _dispatch_boards
from hermes_cli.kanban_ops import (
    _cmd_daemon, _kanban_config, _cmd_dispatch, _cmd_gc, _cmd_repair, _cmd_tail, _cmd_watch,
)
from hermes_cli.kanban_parser import build_parser as _build_parser


def build_parser(parent_subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    """Extend the upstream Kanban parser with the local read-only planner verbs."""
    parser = _build_parser(parent_subparsers)
    sub = next(a for a in parser._actions if isinstance(a, argparse._SubParsersAction))
    for name, description in (
        ("planner", "Read-only board/git planner"),
        ("planner-preview", "Read-only planner candidate preview"),
        ("pre-gate-preview", "Read-only dispatcher pre-gate preview"),
        ("watchdog-preview", "Read-only watchdog observer preview"),
    ):
        command = sub.add_parser(name, help=description)
        command.add_argument("--json", action="store_true")
        command.add_argument("--gate-assumption", choices=("closed", "open"), default="closed")
        command.add_argument("--limit", type=int, default=3)
        if name in {"pre-gate-preview", "watchdog-preview"}:
            command.add_argument("--runtime-mode", required=True)
            command.add_argument("--human-approval", action="store_true")
    return parser


# --- Flag parsing helpers ---

def _none_profile(value: str) -> Optional[str]:
    """``none`` / ``-`` / ``null`` mean "unassign"."""
    return None if value.lower() in {"none", "-", "null"} else value


def _parse_metadata_flag(raw: Optional[str]) -> tuple[Optional[dict], int]:
    """Parse ``--metadata`` JSON; returns ``(dict|None, rc)`` with rc=2 on error."""
    if not raw:
        return None, 0
    try:
        metadata = json.loads(raw)
        if not isinstance(metadata, dict):
            raise ValueError("must be a JSON object")
    except (ValueError, json.JSONDecodeError) as exc:
        return None, _err(f"kanban: --metadata: {exc}", 2)
    return metadata, 0


def _run_state_kwargs(args: argparse.Namespace, cmd: str) -> tuple[Optional[dict[str, str]], int]:
    """``--state-type``/``--state-name`` must be given together: ``(kwargs, 0)`` or ``(None, 2)``."""
    st = getattr(args, "state_type", None)
    sn = getattr(args, "state_name", None)
    if (st is None) != (sn is None):
        return None, _err(f"kanban {cmd}: pass both --state-type and --state-name, or omit both", 2)
    return ({} if st is None else {"state_type": st, "state_name": sn}), 0


def _planner_title_prefix(title: str) -> Optional[str]:
    match = re.match(r"^\s*\[([^\]]+)\]", title or "")
    if not match:
        return None
    return match.group(1).strip().lower()


def _planner_extract_mode(text: Optional[str]) -> Optional[str]:
    if not text:
        return None
    match = re.search(r"(?mi)^\s*mode\s*:\s*([a-z0-9._-]+)\s*$", text)
    if not match:
        return None
    return match.group(1).strip()


def _planner_risk_level(classification: str) -> str:
    if classification == "high-risk-needs-human":
        return "high"
    if classification in {"blocked-by-gate", "ready-for-push", "ready-for-review-commit"}:
        return "medium"
    return "low"


def _planner_candidate_view(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": row["task_id"],
        "title": row["title"],
        "status": row["status"],
        "classification": row["classification"],
        "required_mode": row["required_mode"],
        "risk_level": row["risk_level"],
        "reason": row["reason"],
        "blocked_reason": row["blocked_reason"],
        "next_human_approval": row["next_human_approval"],
    }


def _classify_planner_task(task: kb.Task, *, gate_open: bool) -> dict[str, Any]:
    prefix = _planner_title_prefix(task.title)
    mode = _planner_extract_mode(task.body)
    status = task.status
    blocked_reason = "N/A"
    next_human_approval = "N/A"
    reason = f"status={status}"

    if prefix == "backlog":
        classification = "backlog-never-run"
        blocked_reason = "[Backlog] cards are inventory and must never auto-run"
        next_human_approval = "Human must explicitly rewrite this into a scoped non-backlog task"
    elif prefix == "high-risk":
        classification = "high-risk-needs-human"
        blocked_reason = "[High-Risk] work requires explicit human approval before any mutation"
        next_human_approval = "Approve the exact allowed files, mode, and risk boundary"
    elif status == "done":
        classification = "needs-close-evidence"
        blocked_reason = "done state alone is not proof of artifact / commit / push evidence"
        next_human_approval = "Verify artifact, tests, commit, and push evidence before close"
    elif prefix is None:
        classification = "not-ready"
        blocked_reason = "missing title prefix; no-prefix cards are not automatic execution targets"
        next_human_approval = "Assign a prefix and explicit mode before execution"
    elif prefix == "planning":
        if mode == "design-doc-commit-only":
            classification = "ready-for-design-doc"
            reason = "[Planning] with explicit docs-only mode is design-doc scoped"
        else:
            classification = "ready-for-design"
            reason = "[Planning] cards are limited to read-only / design work"
        next_human_approval = "Approve the exact design/doc scope before mutation"
    else:
        mode_map = {
            "design-doc-commit-only": "ready-for-design-doc",
            "implementation-no-commit": "ready-for-implementation-no-commit",
            "implementation-review-commit": "ready-for-review-commit",
            "push-only": "ready-for-push",
            "kanban-sync-only": "ready-for-kanban-sync",
        }
        if not mode:
            classification = "not-ready"
            blocked_reason = "implementation-style work needs an explicit mode"
            next_human_approval = "Add an explicit mode before execution"
        elif not gate_open and mode.startswith("implementation"):
            classification = "blocked-by-gate"
            blocked_reason = "Planning Gate assumption is closed for implementation work"
            next_human_approval = "Open the gate or keep this in planning"
        else:
            classification = mode_map.get(mode, "not-ready")
            if classification == "not-ready":
                blocked_reason = f"unknown or unsupported mode: {mode}"
                next_human_approval = "Clarify the intended mode before execution"
            else:
                reason = f"explicit mode={mode}"
                if classification == "ready-for-push":
                    next_human_approval = "Approve `git push origin main` after scope review"
                elif classification == "ready-for-review-commit":
                    next_human_approval = "Review the diff before any staging or commit"
                elif classification == "ready-for-kanban-sync":
                    next_human_approval = "Verify artifact / git / push reality before sync"
                else:
                    next_human_approval = "Approve the bounded execution scope"

    candidate = status in {"ready", "running"} and classification in {
        "ready-for-design",
        "ready-for-design-doc",
        "ready-for-implementation-no-commit",
        "ready-for-review-commit",
        "ready-for-push",
        "ready-for-kanban-sync",
    }
    if status not in {"ready", "running"}:
        candidate = False
        if blocked_reason == "N/A":
            blocked_reason = f"status={status} is not a ready/running candidate"

    return {
        "task_id": task.id,
        "title": task.title,
        "status": status,
        "prefix": prefix,
        "mode": mode,
        "classification": classification,
        "required_mode": mode or "N/A",
        "risk_level": _planner_risk_level(classification),
        "reason": reason,
        "blocked_reason": blocked_reason,
        "next_human_approval": next_human_approval,
        "candidate": candidate,
    }


def _planner_git_summary(*, workdir: str) -> dict[str, Any]:
    def _run_git(args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=workdir,
            capture_output=True,
            text=True,
            check=False,
        )

    summary: dict[str, Any] = {
        "workdir": workdir,
        "branch": "N/A",
        "ahead_count": 0,
        "dirty_worktree": False,
        "status_summary": "unknown",
        "git_available": False,
        "errors": [],
    }
    try:
        status = _run_git(["status", "--short"])
        branch = _run_git(["branch", "--show-current"])
        ahead = _run_git(["rev-list", "--count", "origin/main..HEAD"])
    except OSError as exc:
        summary["errors"].append(str(exc))
        summary["status_summary"] = f"git unavailable: {exc}"
        return summary

    summary["git_available"] = True
    dirty_lines = [line for line in status.stdout.splitlines() if line.strip()]
    summary["dirty_worktree"] = bool(dirty_lines)
    summary["status_summary"] = "clean" if not dirty_lines else f"dirty ({len(dirty_lines)} path(s))"
    if status.returncode != 0 and status.stderr.strip():
        summary["errors"].append(status.stderr.strip())
        summary["status_summary"] = status.stderr.strip()

    if branch.returncode == 0 and branch.stdout.strip():
        summary["branch"] = branch.stdout.strip()
    elif branch.stderr.strip():
        summary["errors"].append(branch.stderr.strip())

    if ahead.returncode == 0:
        try:
            summary["ahead_count"] = int((ahead.stdout or "0").strip() or "0")
        except ValueError:
            summary["errors"].append(f"unexpected ahead count: {ahead.stdout!r}")
    elif ahead.stderr.strip():
        summary["errors"].append(ahead.stderr.strip())

    return summary


def _planner_report(
    tasks: list[kb.Task],
    *,
    board: str,
    gate_open: bool,
    git_summary: dict[str, Any],
    candidate_limit: int = 3,
) -> dict[str, Any]:
    """Build the canonical planner.v1 report for read-only consumers.

    Contract source of truth:
    - schema_version is always "planner.v1"
    - canonical keys are mode, board_summary, git_summary, gate_assumption,
      candidates, classification, must_not_run, and notes
    - candidates is the ranked first-look list for dispatcher/watchdog readers
    - classification is the full-task audit list
    - git_summary contains read-only git signals only
    - gate_assumption is an operator assumption, not runtime truth
    - planner does not perform Kanban mutation, Git mutation, or dispatcher dispatch
    """
    counts = Counter(task.status for task in tasks)
    classified = [_classify_planner_task(task, gate_open=gate_open) for task in tasks]
    no_prefix = sum(1 for row in classified if row["prefix"] is None)

    candidates: list[dict[str, Any]] = []
    ahead_count = int(git_summary.get("ahead_count") or 0)
    if ahead_count > 0:
        candidates.append({
            "task_id": "git:ahead",
            "title": "Git ahead of origin/main",
            "status": "N/A",
            "classification": "ready-for-push",
            "required_mode": "push-only",
            "risk_level": "medium",
            "reason": f"origin/main..HEAD = {ahead_count}",
            "blocked_reason": "N/A",
            "next_human_approval": "Approve `git push origin main` after reviewing HEAD scope",
        })
    if git_summary.get("dirty_worktree"):
        candidates.append({
            "task_id": "git:dirty",
            "title": "Git dirty worktree",
            "status": "N/A",
            "classification": "ready-for-review-commit",
            "required_mode": "implementation-review-commit",
            "risk_level": "medium",
            "reason": "worktree has uncommitted changes",
            "blocked_reason": "diff inspection is required before staging or commit",
            "next_human_approval": "Review the dirty diff and approve the exact commit scope",
        })
    for row in classified:
        if row["candidate"]:
            candidates.append(_planner_candidate_view(row))

    must_not_run = [
        "[Backlog] cards are backlog-never-run",
        "[High-Risk] cards require explicit human approval",
        "No-prefix cards are not automatic execution targets",
        "Planner is read-only: no Kanban mutation, no Git mutation, no file edits",
    ]
    if not gate_open:
        must_not_run.append("Implementation work is blocked while the Planning Gate assumption is closed")

    notes = []
    if no_prefix:
        notes.append(f"no-prefix cards: {no_prefix}")
    done_without_evidence = sum(1 for row in classified if row["classification"] == "needs-close-evidence")
    if done_without_evidence:
        notes.append(f"done-but-unverified cards: {done_without_evidence}")
    if git_summary.get("errors"):
        notes.append("git notes: " + " | ".join(str(x) for x in git_summary["errors"]))
    if not candidates:
        notes.append("safe candidate count is zero; returning N/A is valid")

    limited_candidates = candidates[:candidate_limit]
    return {
        "schema_version": "planner.v1",
        "mode": "planner-read-only",
        "board_summary": {
            "board": board,
            "total_cards": len(tasks),
            "by_status": dict(sorted(counts.items())),
            "ready_count": counts.get("ready", 0),
            "running_count": counts.get("running", 0),
            "blocked_count": counts.get("blocked", 0),
            "no_prefix_count": no_prefix,
        },
        "git_summary": git_summary,
        "gate_assumption": "open" if gate_open else "closed",
        "candidates": limited_candidates,
        "classification": classified,
        "must_not_run": must_not_run,
        "notes": notes,
        # Back-compat aliases for current human-readable formatter / external callers.
        "git_status": git_summary,
        "candidate_ranking": limited_candidates,
        "must_not_run_list": must_not_run,
    }


def _require_planner_v1(report: dict[str, Any]) -> dict[str, Any]:
    """Reject planner reports that do not match the canonical planner.v1 schema."""
    schema_version = report.get("schema_version")
    if schema_version != "planner.v1":
        raise ValueError(
            "planner report schema mismatch: expected schema_version='planner.v1' "
            f"but got {schema_version!r}"
        )
    return report


def _require_planner_dispatch_input(report: dict[str, Any]) -> dict[str, Any]:
    """Require canonical planner.v1 input for dispatcher pre-gate checks.

    This is intentionally stricter than preview consumption: dispatcher pre-gate
    decisions must read planner.v1 as the source of truth and fail closed for
    preview or unknown schemas.
    """
    required_keys = {
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
    schema_version = report.get("schema_version")
    if schema_version != "planner.v1":
        raise ValueError(
            "planner dispatch input schema mismatch: expected schema_version='planner.v1' "
            f"but got {schema_version!r}"
        )
    missing = sorted(required_keys - set(report.keys()))
    if missing:
        raise ValueError(f"missing required planner dispatch keys: {', '.join(missing)}")
    return report


def _pre_gate_decision(
    *,
    allowed: bool,
    decision: str,
    reason_code: str,
    reason_text: str,
    candidate_task_id: str,
    runtime_mode: str,
    required_mode: str,
    classification: str,
    risk_level: str,
) -> dict[str, Any]:
    return {
        "allowed": allowed,
        "decision": decision,
        "reason_code": reason_code,
        "reason_text": reason_text,
        "candidate_task_id": candidate_task_id,
        "runtime_mode": runtime_mode,
        "required_mode": required_mode,
        "classification": classification,
        "risk_level": risk_level,
    }


def _pre_gate_decision_for_candidate(
    candidate: dict[str, Any],
    *,
    gate_assumption: str,
    runtime_mode: str,
    human_approval: bool,
) -> dict[str, Any]:
    """Pure dispatcher pre-gate decision for one planner.v1 candidate.

    `allowed=True` means only that the candidate passes the pre-gate. This
    helper never dispatches work, starts workers, mutates Kanban, or mutates Git.
    """
    candidate_task_id = str(candidate.get("task_id", "N/A"))
    classification = str(candidate.get("classification", "N/A"))
    required_mode = str(candidate.get("required_mode", "N/A"))
    risk_level = str(candidate.get("risk_level", "N/A"))

    def result(
        allowed: bool,
        decision: str,
        reason_code: str,
        reason_text: str,
    ) -> dict[str, Any]:
        return _pre_gate_decision(
            allowed=allowed,
            decision=decision,
            reason_code=reason_code,
            reason_text=reason_text,
            candidate_task_id=candidate_task_id,
            runtime_mode=runtime_mode,
            required_mode=required_mode,
            classification=classification,
            risk_level=risk_level,
        )

    if risk_level == "high" or classification == "high-risk-needs-human":
        return result(
            False,
            "reject",
            "high-risk-never-auto-allow",
            "high risk candidates require a narrower human-approved contract",
        )

    if classification in {"backlog-never-run", "not-ready", "blocked-by-gate", "needs-close-evidence"}:
        return result(
            False,
            "reject",
            f"classification-{classification}",
            f"classification {classification} is not dispatchable",
        )

    mutation_like = classification in {
        "ready-for-implementation-no-commit",
        "ready-for-review-commit",
        "ready-for-push",
        "ready-for-kanban-sync",
    }
    if gate_assumption == "closed" and mutation_like:
        return result(
            False,
            "reject",
            "gate-closed",
            "gate_assumption is closed for review/commit/push/implementation work",
        )

    if classification == "ready-for-design":
        if runtime_mode.startswith("design-"):
            return result(True, "allow", "ready-for-design-allowed", "design candidate matches a design runtime mode")
        return result(False, "reject", "mode-mismatch", "ready-for-design requires a design runtime mode")

    if classification == "ready-for-design-doc":
        if runtime_mode == "design-doc-commit-only" and required_mode == runtime_mode:
            return result(
                True,
                "allow",
                "ready-for-design-doc-allowed",
                "design-doc candidate matches design-doc-commit-only",
            )
        return result(False, "reject", "mode-mismatch", "ready-for-design-doc requires design-doc-commit-only")

    if required_mode != "N/A" and runtime_mode != required_mode:
        return result(False, "reject", "mode-mismatch", "runtime_mode must exactly match required_mode")

    if classification == "ready-for-implementation-no-commit":
        if runtime_mode == "implementation-no-commit" and required_mode == runtime_mode:
            return result(
                True,
                "allow",
                "ready-for-implementation-no-commit-allowed",
                "implementation candidate matches implementation-no-commit with gate open",
            )
        return result(
            False,
            "reject",
            "mode-mismatch",
            "ready-for-implementation-no-commit requires implementation-no-commit runtime_mode",
        )

    if classification == "ready-for-kanban-sync":
        return result(
            False,
            "reject",
            "kanban-sync-unsupported",
            "ready-for-kanban-sync execution semantics are not defined for pre-gate v1",
        )

    if classification == "ready-for-review-commit":
        if not human_approval:
            return result(
                False,
                "needs-human",
                "human-approval-required",
                "ready-for-review-commit requires explicit human approval",
            )
        return result(
            True,
            "allow",
            "ready-for-review-commit-allowed",
            "review/commit candidate passed pre-gate with human approval",
        )

    if classification == "ready-for-push":
        if runtime_mode != "push-only":
            return result(False, "reject", "mode-mismatch", "ready-for-push requires push-only runtime_mode")
        if not human_approval:
            return result(
                False,
                "needs-human",
                "human-approval-required",
                "ready-for-push requires explicit human approval",
            )
        return result(True, "allow", "ready-for-push-allowed", "push candidate passed pre-gate with human approval")

    return result(
        False,
        "reject",
        "unsupported-classification",
        f"unsupported pre-gate classification: {classification}",
    )


def _select_dispatchable_candidate(
    report: dict[str, Any],
    *,
    runtime_mode: str,
    human_approval: bool,
) -> dict[str, Any]:
    """Return the first planner.v1 candidate that passes dispatcher pre-gate.

    A needs-human result is returned immediately so automation stops before any
    later lower-risk candidate. If no candidate can pass, return a safe no-op.
    """
    report = _require_planner_dispatch_input(report)
    candidates = report.get("candidates") or []
    gate_assumption = str(report.get("gate_assumption", "unknown"))
    evaluated: list[dict[str, Any]] = []
    for candidate in candidates:
        decision = _pre_gate_decision_for_candidate(
            candidate,
            gate_assumption=gate_assumption,
            runtime_mode=runtime_mode,
            human_approval=human_approval,
        )
        evaluated.append(decision)
        if decision["decision"] in {"allow", "needs-human"}:
            decision["evaluated_candidates"] = evaluated
            return decision

    noop = _pre_gate_decision(
        allowed=False,
        decision="reject",
        reason_code="safe-noop-no-candidates",
        reason_text="no dispatchable candidate passed pre-gate; safe no-op",
        candidate_task_id="N/A",
        runtime_mode=runtime_mode,
        required_mode="N/A",
        classification="N/A",
        risk_level="N/A",
    )
    noop["evaluated_candidates"] = evaluated
    return noop


def _planner_preview_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": candidate.get("task_id", "N/A"),
        "title": candidate.get("title", "N/A"),
        "classification": candidate.get("classification", "N/A"),
        "required_mode": candidate.get("required_mode", "N/A"),
        "risk_level": candidate.get("risk_level", "N/A"),
        "blocked_reason": candidate.get("blocked_reason", "N/A"),
        "next_human_approval": candidate.get("next_human_approval", "N/A"),
    }


def _planner_consumer_preview(report: dict[str, Any]) -> dict[str, Any]:
    """Read-only dispatcher/watchdog preview of a planner.v1 report.

    This consumes planner JSON only for display. It never claims tasks, mutates
    Kanban, mutates Git, starts workers, or dispatches work.
    """
    report = _require_planner_v1(report)
    candidates = report.get("candidates") or []
    gate_assumption = report.get("gate_assumption", "unknown")
    selected = _planner_preview_candidate(candidates[0]) if candidates else None
    safe_noop = selected is None
    dispatch_allowed = False
    if gate_assumption == "closed":
        blocked_reason = "gate_assumption is closed; read-only preview cannot dispatch"
    elif safe_noop:
        blocked_reason = "no candidates; safe no-op preview"
    else:
        blocked_reason = "read-only preview only; dispatcher dispatch is not connected"

    return {
        "schema_version": "planner-consumer-preview.v1",
        "source_schema_version": report["schema_version"],
        "mode": "planner-consumer-preview-read-only",
        "gate_assumption": gate_assumption,
        "dispatch_allowed": dispatch_allowed,
        "dispatch_blocked_reason": blocked_reason,
        "safe_noop": safe_noop,
        "selected_candidate": selected,
        "must_not_run": list(report.get("must_not_run") or []),
    }


def _pre_gate_preview(
    report: dict[str, Any],
    *,
    runtime_mode: str,
    human_approval: bool,
) -> dict[str, Any]:
    """Read-only preview of dispatcher pre-gate selection for planner.v1.

    This only evaluates planner candidates. It never mutates Kanban, mutates
    Git, dispatches work, starts workers, or changes task status.
    """
    report = _require_planner_dispatch_input(report)
    decision = _select_dispatchable_candidate(
        report,
        runtime_mode=runtime_mode,
        human_approval=human_approval,
    )
    display_decision = decision
    evaluated = [
        {k: v for k, v in item.items() if k != "evaluated_candidates"}
        for item in (decision.get("evaluated_candidates") or [])
    ]
    if decision.get("reason_code") == "safe-noop-no-candidates" and evaluated:
        display_decision = evaluated[0]
    return {
        "schema_version": "pre-gate-preview.v1",
        "source_schema_version": report["schema_version"],
        "runtime_mode": runtime_mode,
        "human_approval": human_approval,
        "gate_assumption": report.get("gate_assumption", "unknown"),
        "decision": display_decision["decision"],
        "allowed": display_decision["allowed"],
        "reason_code": display_decision["reason_code"],
        "reason_text": display_decision["reason_text"],
        "candidate_task_id": display_decision["candidate_task_id"],
        "classification": display_decision["classification"],
        "required_mode": display_decision["required_mode"],
        "risk_level": display_decision["risk_level"],
        "evaluated_candidates": evaluated,
        "must_not_run": list(report.get("must_not_run") or []),
    }


def _watchdog_repo_state_hint(git_summary: dict[str, Any]) -> str:
    dirty = bool(git_summary.get("dirty_worktree"))
    ahead_count = int(git_summary.get("ahead_count") or 0)
    hints: list[str] = []
    if dirty:
        hints.append("dirty")
    if ahead_count > 0:
        hints.append(f"ahead:{ahead_count}")
    if not hints:
        return "clean"
    return ", ".join(hints)


def _watchdog_observer_summary(
    report: dict[str, Any],
    *,
    runtime_mode: str,
    human_approval: bool,
) -> dict[str, Any]:
    """Read-only watchdog observer summary for one planner-selected candidate.

    This is a pure preview aggregator. It consumes planner.v1 and pre-gate-style
    candidate evaluation only to help a human approve or reject the next step.
    It never dispatches work, starts workers, mutates Kanban, mutates Git, or
    changes task status.
    """
    report = _require_planner_v1(report)
    planner_preview = _planner_consumer_preview(report)
    selected = planner_preview.get("selected_candidate")
    selected_candidate = dict(selected) if isinstance(selected, dict) else None
    repo_state_hint = _watchdog_repo_state_hint(dict(report.get("git_summary") or {}))
    gate_assumption = str(report.get("gate_assumption", "unknown"))

    if selected_candidate is None:
        decision = _pre_gate_decision(
            allowed=False,
            decision="reject",
            reason_code="safe-noop-no-candidates",
            reason_text="no planner candidate selected; safe no-op",
            candidate_task_id="N/A",
            runtime_mode=runtime_mode,
            required_mode="N/A",
            classification="N/A",
            risk_level="N/A",
        )
        next_human_approval = "N/A"
    else:
        decision = _pre_gate_decision_for_candidate(
            selected_candidate,
            gate_assumption=gate_assumption,
            runtime_mode=runtime_mode,
            human_approval=human_approval,
        )
        next_human_approval = str(selected_candidate.get("next_human_approval", "N/A"))

    return {
        "selected_candidate": selected_candidate,
        "runtime_mode": runtime_mode,
        "decision": decision["decision"],
        "reason_code": decision["reason_code"],
        "required_mode": decision["required_mode"],
        "risk_level": decision["risk_level"],
        "next_human_approval": next_human_approval,
        "safe_noop": decision["decision"] != "allow",
        "repo_state_hint": repo_state_hint,
    }


def _format_planner_consumer_preview(preview: dict[str, Any]) -> str:
    lines = [
        f"mode: {preview['mode']}",
        f"source schema: {preview['source_schema_version']}",
        f"gate assumption: {preview['gate_assumption']}",
        f"dispatch allowed: {'yes' if preview['dispatch_allowed'] else 'no'}",
        f"dispatch blocked reason: {preview['dispatch_blocked_reason']}",
        "",
        "selected candidate:",
    ]
    candidate = preview.get("selected_candidate")
    if candidate is None:
        lines.append("N/A (safe no-op preview)")
    else:
        lines.extend([
            f"- task_id: {candidate['task_id']}",
            f"- title: {candidate['title']}",
            f"- classification: {candidate['classification']}",
            f"- required_mode: {candidate['required_mode']}",
            f"- risk_level: {candidate['risk_level']}",
            f"- blocked_reason: {candidate['blocked_reason']}",
            f"- next_human_approval: {candidate['next_human_approval']}",
        ])
    lines.extend(["", "must-not-run list:"])
    for item in preview.get("must_not_run") or ["N/A"]:
        lines.append(f"- {item}")
    return "\n".join(lines)


def _format_pre_gate_preview(preview: dict[str, Any]) -> str:
    lines = [
        f"schema_version: {preview['schema_version']}",
        f"source_schema_version: {preview['source_schema_version']}",
        f"runtime_mode: {preview['runtime_mode']}",
        f"human_approval: {'true' if preview['human_approval'] else 'false'}",
        f"gate_assumption: {preview['gate_assumption']}",
        f"decision: {preview['decision']}",
        f"allowed: {'true' if preview['allowed'] else 'false'}",
        f"reason_code: {preview['reason_code']}",
        f"reason_text: {preview['reason_text']}",
        f"candidate_task_id: {preview['candidate_task_id']}",
        f"classification: {preview['classification']}",
        f"required_mode: {preview['required_mode']}",
        f"risk_level: {preview['risk_level']}",
        f"evaluated_candidates: {len(preview.get('evaluated_candidates') or [])}",
        "",
        "must-not-run list:",
    ]
    for item in preview.get("must_not_run") or ["N/A"]:
        lines.append(f"- {item}")
    return "\n".join(lines)


def _format_watchdog_observer_summary(summary: dict[str, Any]) -> str:
    lines = ["watchdog preview:"]
    candidate = summary.get("selected_candidate")
    if candidate is None:
        lines.append("selected_candidate: N/A")
    else:
        lines.extend([
            "selected_candidate:",
            f"- task_id: {candidate.get('task_id', 'N/A')}",
            f"- title: {candidate.get('title', 'N/A')}",
            f"- classification: {candidate.get('classification', 'N/A')}",
        ])
    lines.extend([
        f"runtime_mode: {summary['runtime_mode']}",
        f"decision: {summary['decision']}",
        f"reason_code: {summary['reason_code']}",
        f"required_mode: {summary['required_mode']}",
        f"risk_level: {summary['risk_level']}",
        f"next_human_approval: {summary['next_human_approval']}",
        f"safe_noop: {'true' if summary['safe_noop'] else 'false'}",
        f"repo_state_hint: {summary['repo_state_hint']}",
    ])
    return "\n".join(lines)


def _format_planner_report(report: dict[str, Any]) -> str:
    report = _require_planner_v1(report)
    board = report["board_summary"]
    git = report.get("git_summary") or report["git_status"]
    lines = [
        f"mode: {report['mode']}",
        "",
        "board summary:",
        f"- board: {board['board']}",
        f"- total cards: {board['total_cards']}",
        f"- by status: {board['by_status'] or 'N/A'}",
        f"- ready/running/review: ready={board['ready_count']}, running={board['running_count']}, reviewable_git={'yes' if git.get('dirty_worktree') else 'no'}",
        f"- blocked: {board['blocked_count']}",
        f"- no-prefix: {board['no_prefix_count']}",
        "",
        "git status:",
        f"- workdir: {git.get('workdir', 'N/A')}",
        f"- branch: {git.get('branch', 'N/A')}",
        f"- ahead count: {git.get('ahead_count', 'N/A')}",
        f"- dirty worktree: {'yes' if git.get('dirty_worktree') else 'no'}",
        f"- status summary: {git.get('status_summary', 'N/A')}",
        "",
        "gate assumption:",
        f"- {report['gate_assumption']} (conservative unless explicitly overridden)",
        "",
        "candidate ranking:",
    ]
    candidates = report.get("candidates") or report.get("candidate_ranking") or []
    if not candidates:
        lines.append("N/A")
    else:
        for idx, candidate in enumerate(candidates, start=1):
            lines.extend([
                f"{idx}. {candidate['task_id']} - {candidate['title']}",
                f"   - classification: {candidate['classification']}",
                f"   - required mode: {candidate['required_mode']}",
                f"   - risk level: {candidate['risk_level']}",
                f"   - reason: {candidate['reason']}",
                f"   - blocked reason: {candidate['blocked_reason']}",
                f"   - next human approval: {candidate['next_human_approval']}",
            ])
    lines.extend(["", "must-not-run list:"])
    for item in report.get("must_not_run") or report.get("must_not_run_list") or ["N/A"]:
        lines.append(f"- {item}")
    lines.extend(["", "notes:"])
    for item in report.get("notes") or ["N/A"]:
        lines.append(f"- {item}")
    return "\n".join(lines)


def _parse_workspace_flag(value: Optional[str]) -> tuple[Optional[str], Optional[str]]:
    """``--workspace`` -> ``(kind, path|None)``: ``scratch``, ``worktree``, ``worktree:<p>``, ``dir:<p>``.
    Omitted -> ``(None, None)`` so ``create_task`` can tell "default" from an explicit scratch."""
    if not value:
        return (None, None)
    v = value.strip()
    if v in {"scratch", "worktree"}:
        return (v, None)
    for prefix, kind in (("dir:", "dir"), ("worktree:", "worktree")):
        if not v.startswith(prefix):
            continue
        path = v[len(prefix):].strip()
        if not path:
            raise argparse.ArgumentTypeError(f"--workspace {prefix} requires a path after the colon")
        return (kind, os.path.expanduser(path))
    raise argparse.ArgumentTypeError(f"unknown --workspace value {value!r}: use scratch, worktree, "
                                     "worktree:<path>, or dir:<path>")


def _parse_branch_flag(value: Optional[str]) -> Optional[str]:
    """Normalize an optional branch name from ``kanban create --branch``."""
    if value is None:
        return None
    branch = value.strip()
    if not branch:
        raise argparse.ArgumentTypeError("--branch requires a non-empty name")
    if branch.startswith("-"):
        raise argparse.ArgumentTypeError("--branch must not start with '-'")
    if any(ch.isspace() for ch in branch):
        raise argparse.ArgumentTypeError("--branch must not contain whitespace")
    return branch


def _check_dispatcher_presence(hermes_home: Optional[Path] = None) -> tuple[bool, str]:
    """``(running, message)`` for the "will anything dispatch this?" warning: True when a gateway is
    alive for this HERMES_HOME with ``kanban.dispatch_in_gateway`` on, else False + human guidance.
    Fails OPEN (probe/config errors -> ``(True, "")``) — a missed warning beats crying wolf.
    ``hermes_home`` scopes the probe to a profile dir (dashboard backend); CLI callers pass None.

    The dashboard plugin API passes it because the dashboard backend process can be running under a
    different HERMES_HOME than the profile the request targets, which otherwise produced a "no gateway is
    running" warning against a perfectly healthy profile gateway (#71211). CLI callers leave it ``None`` and
    keep the existing process-level behavior.
    """
    try:
        from gateway.status import resolve_gateway_liveness  # type: ignore

        # Same ladder as the dashboard status endpoints so PID-file-less / cross-container gateways
        # aren't misreported; use_cache=False because this one-shot probe must see the state now.
        liveness = resolve_gateway_liveness(profile_dir=hermes_home, use_cache=False)
    except Exception:
        return (True, "")  # can't probe — silent
    if liveness.probe_error:  # resolver swallows per-rung failures; "can't tell" != "no gateway"
        return (True, "")
    pid = liveness.pid
    # Even if the gateway is up, dispatch_in_gateway may be off (can't tell -> assume default).
    if pid and bool(_kanban_config().get("dispatch_in_gateway", True)):
        return (True, f"gateway pid={pid}, dispatch enabled")
    if pid:
        return (False, "Gateway is running but kanban.dispatch_in_gateway=false in "
                "config.yaml — the task will sit in 'ready' until you flip it "
                "back on and restart the gateway, OR run the legacy "
                "standalone daemon (`hermes kanban daemon --force`).")
    return (False, "No gateway is running — the task will sit in 'ready' until you "
            "start it. Run:\n    hermes gateway start\n"
            "The gateway hosts an embedded dispatcher (tick interval 60s by "
            "default); your task will be picked up on the next tick after "
            "the gateway comes up.")


# --- Command dispatch ---

def kanban_command(args: argparse.Namespace) -> int:
    """Entry point from ``hermes kanban …``; returns a shell-style exit code."""
    action = getattr(args, "kanban_action", None)
    if not action:
        parser = getattr(args, "_kanban_parser", None)
        if parser is not None:
            parser.print_help()
        else:
            print("usage: hermes kanban <action> [options]\n"
                  "Run 'hermes kanban --help' for the full list of actions.", file=sys.stderr)
        return 0

    # Fast-fail for UX only; the durable trust boundary is in kanban_db, since children can
    # import DB mutators directly.
    if _is_delegated_child_cli_mutation(args):
        return _err("kanban: delegate_task child contexts cannot mutate Kanban tasks via the CLI")

    # `boards …` manages board metadata and the current-board pointer itself, so it must ignore
    # the `--board` routing override (else `--board beta boards show` reports beta).
    if action == "boards":
        return _dispatch_boards(args)

    # `--board <slug>` pins HERMES_KANBAN_BOARD for the duration of this call so it inherits the
    # exact resolution the dispatcher uses for workers.
    board_override = getattr(args, "board", None)
    board_scope = contextlib.nullcontext()
    if board_override:
        try:
            normed = kb._normalize_board_slug(board_override)
        except ValueError as exc:
            return _err(f"kanban: {exc}", 2)
        if not normed:
            return _err("kanban: --board requires a slug", 2)
        # Boards other than 'default' must already exist — typoed slugs would otherwise silently
        # create an empty board.
        if normed != kb.DEFAULT_BOARD and not kb.board_exists(normed):
            return _err(f"kanban: board {normed!r} does not exist. "
                        f"Create it with `hermes kanban boards create {normed}`.")
        board_scope = kb.scoped_current_board(normed)

    with board_scope:
        # `repair` dispatches BEFORE auto-init: on a corrupt DB init_db() itself raises
        # KanbanDbCorruptError, which would turn every repair into "could not initialize database".
        if action == "repair":
            return _cmd_repair(args)
        # init_db is idempotent (one sqlite_master SELECT when tables exist) and prevents
        # "no such table: tasks" on first use from a fresh HERMES_HOME.
        try:
            kb.init_db()
        except Exception as exc:
            return _err(f"kanban: could not initialize database: {exc}")

        handler = _PLANNER_HANDLERS.get(action) or _HANDLERS.get(action)
        if not handler:
            return _err(f"kanban: unknown action {action!r}", 2)
        try:
            return int(handler(args) or 0)
        except (ValueError, RuntimeError, PermissionError) as exc:
            return _err(f"kanban: {exc}")


# --- Handlers ---

def _profile_author() -> str:
    """Best-effort author name for an interactive CLI call."""
    from hermes_cli.profiles import current_profile_name
    return current_profile_name("user") or "user"


_DELEGATED_CHILD_DENIED_ACTIONS: frozenset[str] = frozenset({
    "init", "create", "swarm", "assign", "reclaim", "reassign", "link", "unlink",
    "claim", "comment", "attach", "attach-rm", "complete", "edit", "block",
    "schedule", "unblock", "promote", "archive", "dispatch", "daemon", "repair",
    "heartbeat", "notify-subscribe", "notify-unsubscribe", "specify", "decompose",
    "request-review", "request-changes", "reopen-review",
    "gc",
})

_DELEGATED_CHILD_DENIED_BOARD_ACTIONS: frozenset[str] = frozenset({
    "create", "new", "rm", "remove", "delete", "switch", "use", "rename",
    "set-default-workdir", "import",
})


def _is_delegated_child_cli_mutation(args: argparse.Namespace) -> bool:
    action = getattr(args, "kanban_action", None)
    if action == "boards":
        if (getattr(args, "boards_action", None) or "list") not in _DELEGATED_CHILD_DENIED_BOARD_ACTIONS:
            return False
    elif action not in _DELEGATED_CHILD_DENIED_ACTIONS:
        return False
    from agent.delegation_context import kanban_path_is_fenced

    return kanban_path_is_fenced(kb.kanban_home()) or kanban_path_is_fenced(kb.kanban_db_path())


def _joined_words(words) -> Optional[str]:
    """Free-text positional ``nargs="*"`` words -> stripped string, or None when absent."""
    return " ".join(words).strip() if words else None


def _stripped_or_none(value: Optional[str]) -> Optional[str]:
    """``None`` stays ``None``; otherwise strip, and treat the empty string as ``None``."""
    return None if value is None else (value.strip() or None)


def _ok_or_err(ok, fail: str, done: str) -> int:
    """Single-mutation handlers: print ``done`` (rc 0) or ``fail`` to stderr (rc 1)."""
    if not ok:
        return _err(fail)
    print(done)
    return 0


def _bulk_ids(args: argparse.Namespace) -> list[str]:
    """Positional ``task_id`` plus ``--ids`` extras (bulk verbs)."""
    return [args.task_id] + list(getattr(args, "ids", None) or [])


def _require_ids(args: argparse.Namespace) -> tuple[list[str], int]:
    """``args.task_ids`` -> ``(ids, 0)`` or ``([], 1)`` after printing the standard error."""
    ids = list(args.task_ids or [])
    if not ids:
        return ids, _err("at least one task_id is required")
    return ids, 0


def _parse_duration(val) -> Optional[int]:
    """``30s`` / ``5m`` / ``2h`` / ``1d`` or a raw integer → seconds; None for empty input;
    ValueError on malformed input."""
    if val is None or val == "":
        return None
    s = str(val).strip().lower()
    try:
        return int(s)  # bare integer → seconds
    except ValueError:
        pass
    units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    if not (s and s[-1] in units):
        raise ValueError(f"malformed duration {val!r} (expected 30s, 5m, 2h, 1d, or a number)")
    try:
        n = float(s[:-1])
    except ValueError as exc:
        raise ValueError(f"malformed duration {val!r}") from exc
    return int(n * units[s[-1]])


def _cmd_init(args: argparse.Namespace) -> int:
    path = kb.init_db()
    print(f"Kanban DB initialized at {path}")
    print()
    # Profiles on disk == assignees already addressable.
    try:
        profiles = kb.list_profiles_on_disk()
    except Exception:
        profiles = []
    if profiles:
        print(f"Discovered {len(profiles)} profile(s) on disk; any of these can be an --assignee:")
        for name in profiles:
            print(f"  {name}")
    else:
        print("No profiles found under ~/.hermes/profiles/.\n"
              "Create one with `hermes -p <name> setup` before assigning tasks.")
    print(
        "\nNext step: start the gateway so ready tasks actually get picked up.\n"
        "  hermes gateway start\n\n"
        "The gateway hosts an embedded dispatcher that ticks every 60 seconds\n"
        "by default (config: kanban.dispatch_interval_seconds). Without a\n"
        "running gateway, tasks stay in 'ready' forever."
    )
    return 0


def _cmd_heartbeat(args: argparse.Namespace) -> int:
    with kbc.connect_closing() as conn:
        ok = kbd.heartbeat_worker(conn, args.task_id, note=getattr(args, "note", None),
                                 expected_run_id=_worker_run_id_for(args.task_id))
    return _ok_or_err(ok, f"cannot heartbeat {args.task_id} (not running?)",
                      f"Heartbeat recorded for {args.task_id}")


def _cmd_assignees(args: argparse.Namespace) -> int:
    with kbc.connect_closing() as conn:
        data = kb.known_assignees(conn)
    if _json_out(args, data):
        return 0
    if not data:
        print("(no assignees — create a profile with `hermes -p <name> setup`)")
        return 0
    print(f"{'NAME':20s}  {'ON DISK':8s}  COUNTS")
    for entry in data:
        on_disk = "yes" if entry["on_disk"] else "no"
        print(f"{entry['name']:20s}  {on_disk:8s}  {_fmt_counts(entry['counts'] or {}, '(idle)')}")
    return 0


def _cmd_create(args: argparse.Namespace) -> int:
    from agent.delegation_context import is_dispatcher_owned_worker_context

    body = args.body
    body_file = getattr(args, "body_file", None)
    if body is not None and body_file is not None:
        return _err("kanban: --body and --body-file are mutually exclusive", 2)
    if body_file is not None:
        try:
            body = sys.stdin.read() if body_file == "-" else Path(body_file).read_text(encoding="utf-8-sig")
        except OSError as exc:
            return _err(f"kanban: --body-file: {exc}", 2)

    try:
        ws_kind, ws_path = _parse_workspace_flag(args.workspace)
        branch_name = _parse_branch_flag(getattr(args, "branch", None))
    except argparse.ArgumentTypeError as exc:
        return _err(f"kanban: {exc}", 2)
    if branch_name and ws_kind != "worktree":
        return _err("kanban: --branch is only valid with --workspace worktree", 2)
    try:
        max_runtime = _parse_duration(getattr(args, "max_runtime", None))
    except ValueError as exc:
        return _err(f"kanban: --max-runtime: {exc}", 2)
    max_retries = getattr(args, "max_retries", None)
    if max_retries is not None and max_retries < 1:
        return _err(f"kanban: --max-retries must be >= 1 (got {max_retries}); "
                    "use 1 to trip on the first failure.", 2)
    with kbc.connect_closing() as conn:
        task_id = kb.create_task(
            conn, title=args.title, body=body, assignee=args.assignee,
            created_by=args.created_by or _profile_author(),
            workspace_kind=ws_kind, workspace_path=ws_path, branch_name=branch_name,
            project_id=getattr(args, "project", None), tenant=args.tenant, priority=args.priority,
            parents=tuple(args.parent or ()), triage=bool(getattr(args, "triage", False)),
            idempotency_key=getattr(args, "idempotency_key", None),
            max_runtime_seconds=max_runtime, skills=getattr(args, "skills", None) or None,
            max_retries=max_retries, model_override=getattr(args, "model_override", None),
            provider_override=getattr(args, "provider_override", None),
            goal_mode=bool(getattr(args, "goal_mode", False)),
            goal_max_turns=getattr(args, "goal_max_turns", None),
            completion_contract=getattr(args, "completion_contract", None),
            initial_status=getattr(args, "initial_status", "running"),
            creator_task_id=(os.environ.get("HERMES_KANBAN_TASK")
                             if is_dispatcher_owned_worker_context() else None),
        )
        task = kb.get_task(conn, task_id)
    if getattr(args, "json", False):
        _print_json(_task_to_dict(task))
    else:
        print(f"Created {task_id}  ({task.status}, assignee={task.assignee or '-'})")
        # Warn only for ready+assigned tasks that would sit without a dispatcher (triage/todo idle
        # by design, unassigned can't dispatch); skipped under --json so stdout stays parseable.
        if task.status == "ready" and task.assignee:
            running, message = _check_dispatcher_presence()
            if not running and message:
                print(f"\n⚠  {message}", file=sys.stderr)
    return 0


def _cmd_swarm(args: argparse.Namespace) -> int:
    try:
        workers = [ks.parse_worker_arg(raw) for raw in (args.worker or [])]
    except ValueError as exc:
        return _err(f"kanban swarm: {exc}", 2)
    if not workers:
        return _err("kanban swarm: at least one --worker is required", 2)
    with kbc.connect_closing() as conn:
        created = ks.create_swarm(
            conn, goal=args.goal, workers=workers, verifier_assignee=args.verifier,
            synthesizer_assignee=args.synthesizer, tenant=args.tenant,
            created_by=args.created_by or _profile_author(), priority=args.priority,
            idempotency_key=getattr(args, "idempotency_key", None),
        )
    if getattr(args, "json", False):
        _print_json(created.as_dict())
    else:
        print(f"Swarm root: {created.root_id}\n"
              "Workers: " + ", ".join(created.worker_ids) + "\n"
              f"Verifier: {created.verifier_id}\n"
              f"Synthesizer: {created.synthesizer_id}")
    return 0


def _planner_report_from_current_board(*, gate_open: bool, limit: int) -> dict[str, Any]:
    board = kb.get_current_board()
    meta = kb.read_board_metadata(board)
    workdir = meta.get("default_workdir") or os.getcwd()
    with kbc.connect_closing() as conn:
        tasks = kb.list_tasks(conn, include_archived=False, limit=1000)
    return _planner_report(
        tasks, board=board, gate_open=gate_open,
        git_summary=_planner_git_summary(workdir=workdir), candidate_limit=limit,
    )


def _cmd_planner(args: argparse.Namespace) -> int:
    report = _planner_report_from_current_board(
        gate_open=args.gate_assumption == "open", limit=max(0, args.limit),
    )
    print(json.dumps(report, indent=2, ensure_ascii=False) if args.json else _format_planner_report(report))
    return 0


def _cmd_planner_preview(args: argparse.Namespace) -> int:
    report = _planner_report_from_current_board(
        gate_open=args.gate_assumption == "open", limit=max(0, args.limit),
    )
    preview = _planner_consumer_preview(report)
    print(json.dumps(preview, indent=2, ensure_ascii=False) if args.json else _format_planner_consumer_preview(preview))
    return 0


def _cmd_pre_gate_preview(args: argparse.Namespace) -> int:
    report = _planner_report_from_current_board(
        gate_open=args.gate_assumption == "open", limit=max(0, args.limit),
    )
    preview = _pre_gate_preview(report, runtime_mode=args.runtime_mode, human_approval=args.human_approval)
    print(json.dumps(preview, indent=2, ensure_ascii=False) if args.json else _format_pre_gate_preview(preview))
    return 0


def _cmd_watchdog_preview(args: argparse.Namespace) -> int:
    report = _planner_report_from_current_board(
        gate_open=args.gate_assumption == "open", limit=max(0, args.limit),
    )
    preview = _watchdog_observer_summary(report, runtime_mode=args.runtime_mode, human_approval=args.human_approval)
    print(json.dumps(preview, indent=2, ensure_ascii=False) if args.json else _format_watchdog_observer_summary(preview))
    return 0


def _cmd_list(args: argparse.Namespace) -> int:
    assignee = args.assignee
    if args.mine and not assignee:
        assignee = _profile_author()
    with kbc.connect_closing() as conn:
        # Cheap mini-dispatch so list reflects dependencies cleared since the last tick.
        kb.recompute_ready(conn)
        tasks = kb.list_tasks(
            conn, assignee=assignee, status=args.status, tenant=args.tenant, session_id=args.session,
            include_archived=args.archived, order_by=getattr(args, "sort", None),
            workflow_template_id=args.workflow_template_id, current_step_key=args.current_step_key,
        )
    if _json_out(args, [_task_to_dict(t) for t in tasks]):
        return 0
    # Passive discoverability: only multi-board users see which board this is.
    try:
        all_boards = kb.list_boards(include_archived=False)
    except Exception:
        all_boards = []
    if len(all_boards) > 1:
        other_count = len(all_boards) - 1
        print(f"Board: {kb.get_current_board()} ({other_count} other board{'s' if other_count != 1 else ''} — "
              f"`hermes kanban boards list`)\n")
    if not tasks:
        print("(no matching tasks)")
        return 0
    for t in tasks:
        print(_fmt_task_line(t))
    return 0


def _print_diagnostics(diags, indent: str, *, with_kind: bool) -> None:
    """Shared human rendering for ``show`` and ``diagnostics`` (suggested actions only)."""
    sev_marker = {"warning": "⚠", "error": "!!", "critical": "!!!"}
    for d in diags:
        head = f"{d.kind}: {d.title}" if with_kind else d.title
        print(f"{indent}{sev_marker.get(d.severity, '?')} [{d.severity}] {head}")
        if d.data:
            bits = [f"{k}={','.join(str(x) for x in v)}" if isinstance(v, list) else f"{k}={v}"
                    for k, v in d.data.items()]
            if bits:
                print(f"{indent}   data: {' | '.join(bits)}")
        for a in d.actions:
            if a.suggested:
                print(f"{indent}   → {a.label}")


def _print_section(title: str, lines) -> None:
    """Blank line, ``title``, then each line (``show`` body sections)."""
    print()
    print(title)
    for line in lines:
        print(line)


def _cmd_show(args: argparse.Namespace) -> int:
    rsk, rc = _run_state_kwargs(args, "show")
    if rc:
        return rc
    graph = None
    want_json = getattr(args, "json", False)
    with kbc.connect_closing() as conn:
        task = kb.get_task(conn, args.task_id)
        if not task:
            return _err(f"no such task: {args.task_id}")
        comments = kb.list_comments(conn, args.task_id)
        events = kb.list_events(conn, args.task_id)
        parents = kb.parent_ids(conn, args.task_id)
        children = kb.child_ids(conn, args.task_id)
        runs = kb.list_runs(conn, args.task_id, **rsk)
        # Workers hand off via task_runs.summary; tasks.result stays NULL unless set.
        latest_summary = kb.latest_summary(conn, args.task_id)
        if not want_json:
            graph = kb.task_graph_context(conn, task.id)

    if want_json:
        _print_json({
            "task": _task_to_dict(task), "latest_summary": latest_summary, "parents": parents, "children": children,
            "comments": [_obj_dict(c, ("author", "body", "created_at")) for c in comments],
            "events": [_obj_dict(e, ("kind", "payload", "created_at", "run_id")) for e in events],
            "runs": [_obj_dict(r, _SHOW_RUN_FIELDS) for r in runs],
        })
        return 0

    def field(label: str, value) -> None:
        print(f"  {label + ':':<11}{value}")

    print(f"Task {task.id}: {task.title}")
    field("status", task.status)
    field("assignee", task.assignee or "-")
    if task.tenant:
        field("tenant", task.tenant)
    field("workspace", f"{task.workspace_kind}" + (f" @ {task.workspace_path}" if task.workspace_path else ""))
    if task.branch_name:
        field("branch", task.branch_name)
    if task.skills:
        field("skills", ", ".join(task.skills))
    if task.model_override:
        _prov = f" (provider: {task.provider_override})" if task.provider_override else ""
        field("model", f"{task.model_override}{_prov}")
    # Effective retry threshold (task > config > default) explains auto-blocks.
    if task.max_retries is not None:
        print(f"  max-retries: {task.max_retries} (task)")
    else:
        cfg_val = _kanban_config().get("failure_limit")
        if cfg_val is not None and int(cfg_val) != kb.DEFAULT_FAILURE_LIMIT:
            print(f"  max-retries: {int(cfg_val)} (config kanban.failure_limit)")
        else:
            print(f"  max-retries: {kb.DEFAULT_FAILURE_LIMIT} (default)")
    field("created", f"{_fmt_ts(task.created_at)} by {task.created_by or '-'}")

    # Diagnostics up top so CLI users see distress signals before scrolling.
    from hermes_cli import kanban_diagnostics as kd
    diags = kd.compute_task_diagnostics(task, events, runs, graph=graph)
    if diags:
        print(f"\n  Diagnostics ({len(diags)}):")
        _print_diagnostics(diags, "    ", with_kind=False)
    if task.started_at:
        field("started", _fmt_ts(task.started_at))
    if task.completed_at:
        field("completed", _fmt_ts(task.completed_at))
    if parents:
        field("parents", ", ".join(parents))
    if children:
        field("children", ", ".join(children))
    if task.body:
        _print_section("Body:", [task.body])
    if task.result:
        _print_section("Result:", [task.result])
    elif latest_summary:
        _print_section("Latest summary:", [latest_summary])
    if comments:
        _print_section(f"Comments ({len(comments)}):",
                       (f"  [{_fmt_ts(c.created_at)}] {c.author}: {c.body}" for c in comments))
    if events:
        _print_section(f"Events ({len(events)}):", (
            f"  [{_fmt_ts(e.created_at)}]{f' [run {e.run_id}]' if e.run_id else ''} {e.kind}"
            f"{f' {e.payload}' if e.payload else ''}" for e in events[-20:]))
    if runs:
        print()
        print(f"Runs ({len(runs)}):")
        for r in runs:
            # Clamp to 0 so NTP backward-jumps don't print negative seconds.
            elapsed = max(0, r.ended_at - r.started_at) if r.ended_at else None
            el = f"{elapsed}s" if elapsed is not None else "active"
            outcome = r.outcome or r.status or "active"
            print(f"  #{r.id:<3} {outcome:<12} @{r.profile or '-'}  {el}  {_fmt_ts(r.started_at)}")
            if r.summary:
                print(f"        → {r.summary.splitlines()[0][:160]}")
            if r.error:
                print(f"        ! {r.error.splitlines()[0][:160]}")
    return 0


def _cmd_assign(args: argparse.Namespace) -> int:
    profile = _none_profile(args.profile)
    with kbc.connect_closing() as conn:
        ok = kb.assign_task(conn, args.task_id, profile)
    return _ok_or_err(ok, f"no such task: {args.task_id}",
                      f"Assigned {args.task_id} to {profile or '(unassigned)'}")


def _cmd_set_model(args: argparse.Namespace) -> int:
    model = args.model
    if model is not None and model.lower() in {"none", "-", "null", ""}:
        model = None
    provider = getattr(args, "provider", None)
    try:
        with kbc.connect_closing() as conn:
            ok = kb.set_model_override(conn, args.task_id, model, provider=provider)
    except (ValueError, RuntimeError) as exc:
        return _err(f"kanban: {exc}", 2)
    if not ok:
        return _err(f"no such task: {args.task_id}")
    if model:
        label = f"{provider}:{model}" if provider else model
        print(f"Set model override on {args.task_id}: {label} (applies on next dispatch)")
    else:
        print(f"Cleared model override on {args.task_id} (worker uses its profile default)")
    return 0


def _cmd_reclaim(args: argparse.Namespace) -> int:
    with kbc.connect_closing() as conn:
        ok = kb.reclaim_task(conn, args.task_id, reason=getattr(args, "reason", None))
    return _ok_or_err(ok, f"cannot reclaim {args.task_id} (not running or unknown id)",
                      f"Reclaimed {args.task_id}")


def _cmd_reassign(args: argparse.Namespace) -> int:
    profile = _none_profile(args.profile)
    reclaim = bool(getattr(args, "reclaim", False))
    with kbc.connect_closing() as conn:
        ok = kb.reassign_task(conn, args.task_id, profile, reclaim_first=reclaim, reason=getattr(args, "reason", None))
    return _ok_or_err(
        ok,
        f"cannot reassign {args.task_id} (unknown id, or still running — pass --reclaim to release first)",
        f"Reassigned {args.task_id} to {profile or '(unassigned)'}" + (" (claim reclaimed)" if reclaim else ""),
    )


def _rows_by_task(conn, table: str, ids: list[str]) -> dict[str, list]:
    """``{task_id: [rows ordered by id]}`` for every id (empty list when none)."""
    by = {i: [] for i in ids}
    placeholders = ",".join(["?"] * len(ids))
    for row in conn.execute(f"SELECT * FROM {table} WHERE task_id IN ({placeholders}) ORDER BY id", tuple(ids)):
        by.setdefault(row["task_id"], []).append(row)
    return by


def _cmd_diagnostics(args: argparse.Namespace) -> int:
    """List active diagnostics on the board via the same rule engine the dashboard uses."""
    from hermes_cli import kanban_diagnostics as kd
    # Honour kanban.default_assignee as the fallback for unassigned ready tasks (#27145),
    # kanban.max_in_progress as the global concurrency cap (#33488), kanban.max_in_progress_per_profile as
    # the per-profile cap (#21582), and kanban.max_spawn as the per-tick spawn limit (#28805). Same
    # semantics as the gateway dispatch path so behavior matches whether the user runs the CLI directly or
    # relies on the gateway-embedded dispatcher.
    from hermes_cli.config import load_config

    diag_config = kd.config_from_runtime_config(load_config())

    with kbc.connect_closing() as conn:
        # Either one-task mode or fleet mode.
        if getattr(args, "task", None):
            task = kb.get_task(conn, args.task)
            if task is None:
                return _err(f"no such task: {args.task}")
            diags_by_task = {args.task: kd.compute_task_diagnostics(
                task, kb.list_events(conn, args.task), kb.list_runs(conn, args.task),
                graph=kb.task_graph_context(conn, args.task), config=diag_config)}
        else:
            # Fleet mode: pull all non-archived tasks + their events/runs.
            rows = list(conn.execute("SELECT * FROM tasks WHERE status != 'archived'").fetchall())
            ids = [r["id"] for r in rows]
            diags_by_task = {}
            if ids:
                ev_by = _rows_by_task(conn, "task_events", ids)
                run_by = _rows_by_task(conn, "task_runs", ids)
                graph_by = kb.task_graph_contexts(conn, ids)
                for r in rows:
                    tid = r["id"]
                    dl = kd.compute_task_diagnostics(r, ev_by.get(tid, []), run_by.get(tid, []),
                                                     graph=graph_by.get(tid), config=diag_config)
                    if dl:
                        diags_by_task[tid] = dl

        sev = getattr(args, "severity", None)
        if sev:
            floor = kd.SEVERITY_ORDER.index(sev)
            diags_by_task = {tid: kept for tid, dl in diags_by_task.items()
                             if (kept := [d for d in dl if kd.SEVERITY_ORDER.index(d.severity) >= floor])}

        # Map task_id → title/status/assignee for the table output.
        meta: dict[str, dict] = {}
        if diags_by_task:
            placeholders = ",".join(["?"] * len(diags_by_task))
            for r in conn.execute(f"SELECT id, title, status, assignee FROM tasks WHERE id IN ({placeholders})",
                                  tuple(diags_by_task.keys())):
                meta[r["id"]] = {k: r[k] for k in ("title", "status", "assignee")}

    # What this home believes it may claim on a shared board (#113620).
    allowlist = kbd.dispatch_profile_allowlist_summary()

    if getattr(args, "json", False):
        # Per-task rows unchanged; the home-scope allowlist rides as a trailing row
        # (task_id null) so existing `payload[0]["diagnostics"]` consumers keep working.
        _print_json([{"task_id": tid, **meta.get(tid, {}), "diagnostics": [d.to_dict() for d in dl]}
                     for tid, dl in diags_by_task.items()]
                    + [{"task_id": None, "dispatch_profiles": allowlist, "diagnostics": []}])
        return 0

    print(f"kanban.dispatch_profiles: {allowlist}")
    if not diags_by_task:
        print("No active diagnostics on this board.")
        return 0

    total = sum(len(dl) for dl in diags_by_task.values())
    print(f"{total} active diagnostic(s) across {len(diags_by_task)} task(s):\n")
    for tid, dl in diags_by_task.items():
        m = meta.get(tid, {})
        print(f"  {tid}  {m.get('status') or '?':8s}  @{m.get('assignee') or '(unassigned)':18s}  "
              f"{m.get('title') or '(untitled)'}")
        _print_diagnostics(dl, "    ", with_kind=True)
        print()
    return 0


def _cmd_link(args: argparse.Namespace) -> int:
    # A worker linking its own running card (dependency-block handoff) proves
    # ownership with its run id; linking a foreign task never needs one.
    expected_child_run_id = (
        _worker_run_id_for(args.child_id)
        if args.child_id == os.environ.get("HERMES_KANBAN_TASK") else None)
    with kbc.connect_closing() as conn:
        gated = kb.link_tasks(conn, args.parent_id, args.child_id,
                              expected_child_run_id=expected_child_run_id)
    print(f"Linked {args.parent_id} -> {args.child_id}")
    if gated:
        print(
            f"Note: {args.child_id} was ready and is now todo — parent "
            f"{args.parent_id} is not done yet. The ready -> running claim "
            f"re-checks parents, so the child only runs after the parent "
            f"completes; use `hermes kanban unlink {args.parent_id} {args.child_id}` "
            f"to run it now."
        )
    return 0


def _cmd_unlink(args: argparse.Namespace) -> int:
    with kbc.connect_closing() as conn:
        ok = kb.unlink_tasks(conn, args.parent_id, args.child_id)
    return _ok_or_err(ok, f"No such link: {args.parent_id} -> {args.child_id}",
                      f"Unlinked {args.parent_id} -> {args.child_id}")


def _cmd_claim(args: argparse.Namespace) -> int:
    with kbc.connect_closing() as conn:
        task = kb.claim_task(conn, args.task_id, ttl_seconds=args.ttl)
        if task is None:
            existing = kb.get_task(conn, args.task_id)
            if existing is None:
                return _err(f"no such task: {args.task_id}")
            return _err(f"cannot claim {args.task_id}: status={existing.status} "
                        f"lock={existing.claim_lock or '(none)'}")
        workspace = kbw.resolve_workspace(task)
        kbw.set_workspace_path(conn, task.id, str(workspace))
    print(f"Claimed {task.id}\nWorkspace: {workspace}")
    return 0


def _cmd_comment(args: argparse.Namespace) -> int:
    body = " ".join(args.text).strip()
    if args.max_len is not None:
        if args.max_len < 1:
            return _err("kanban: --max-len must be positive", 2)
        if len(body) > args.max_len:
            suffix = f"\n\n[trimmed to {args.max_len} chars by --max-len]"
            body = body[: max(0, args.max_len - len(suffix))].rstrip() + suffix
    author = args.author or _profile_author()
    with kbc.connect_closing() as conn:
        kb.add_comment(conn, args.task_id, author, body)
    print(f"Comment added to {args.task_id}")
    return 0


def _cmd_attach(args: argparse.Namespace) -> int:
    """Attach a local file via the shared ``store_attachment_bytes`` path (same 25 MB cap and name
    sanitisation as the dashboard upload and agent tool)."""
    import mimetypes
    _worker_run_id_for(args.task_id)

    src = Path(args.path).expanduser()
    if not src.is_file():
        return _err(f"kanban: no such file: {src}")
    data = src.read_bytes()
    name = args.name or src.name
    content_type = args.content_type or mimetypes.guess_type(name)[0]
    uploaded_by = args.author or _profile_author()
    try:
        with kbc.connect_closing() as conn:
            att_id = kb.store_attachment_bytes(conn, args.task_id, name, data, content_type=content_type,
                                               uploaded_by=uploaded_by)
    except kb.AttachmentTooLarge as exc:
        return _err(f"kanban: {exc}")
    print(f"Attached {name} to {args.task_id} (attachment {att_id}, {len(data)} bytes)")
    return 0


def _cmd_attachments(args: argparse.Namespace) -> int:
    with kbc.connect_closing() as conn:
        if kb.get_task(conn, args.task_id) is None:
            return _err(f"no such task: {args.task_id}")
        atts = kb.list_attachments(conn, args.task_id)
    if _json_out(args, [_obj_dict(a, _ATTACHMENT_FIELDS) for a in atts], ascii=True):
        return 0
    if not atts:
        print(f"No attachments on {args.task_id}")
        return 0
    print(f"Attachments on {args.task_id}:")
    for a in atts:
        ct = a.content_type or "-"
        print(f"  [{a.id}] {a.filename}  ({a.size} bytes, {ct}, by {a.uploaded_by or '-'})")
        print(f"        {a.stored_path}")
    return 0


def _cmd_attach_rm(args: argparse.Namespace) -> int:
    with kbc.connect_closing() as conn:
        removed = kb.delete_attachment(conn, args.attachment_id)
    if removed is None:
        return _err(f"no such attachment: {args.attachment_id}")
    print(f"Deleted attachment {args.attachment_id} ({removed.filename}) from {removed.task_id}")
    return 0


def _worker_run_id_for(task_id: str) -> Optional[int]:
    env_tid = os.environ.get("HERMES_KANBAN_TASK")
    if env_tid and env_tid != task_id:
        raise ValueError(f"worker is scoped to task {env_tid}; refusing to mutate {task_id}")
    raw = os.environ.get("HERMES_KANBAN_RUN_ID")
    if os.environ.get("HERMES_KANBAN_TASK") != task_id or not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def _goal_mode_handoff_rejection(task: Optional[kb.Task], evidence: str):
    """Goal judge for every terminal worker handoff (including review).

    Returns ``(verdict, reason_or_None)``: ``"done"`` allows; ``"blocked"`` = judge ruled the goal
    unachievable; ``"continue"``/``"wait"`` reject with the judge's reason. Judge failures allow
    the handoff (logged).

    See #100954.
    ``{"done", None}`` means the judge allows the handoff; anything else is a rejection whose verdict
    disambiguates the guidance the caller gives the worker (``continue`` = not done yet, ``blocked`` =
    judged unachievable — see #100954).
    """
    if task is None or not task.goal_mode:
        return ("done", None)
    try:
        from agent.auxiliary_client import get_text_auxiliary_client

        client, model = get_text_auxiliary_client("goal_judge")
    except Exception:
        client, model = None, None
    if client is None or not model:
        return ("done", None)

    from hermes_cli.goals import judge_goal

    verdict, reason, transport_failed = "done", "", False
    try:
        # Headless handoff checks run outside any agent turn: bind the per-task relay-affinity
        # scope (mirrors kanban_specify) so the relay does not reject the judge call (#113669).
        from agent.portal_tags import get_affinity_scope, reset_affinity_scope, set_affinity_scope
        affinity_token = None if get_affinity_scope() else set_affinity_scope(f"kanban:{task.id}")
        try:
            verdict, reason, _, _, transport_failed = judge_goal(
                goal=f"{task.title}\n\n{task.body or ''}".strip(),
                last_response=evidence.strip())
        finally:
            if affinity_token is not None:
                reset_affinity_scope(affinity_token)
    except Exception as judge_exc:
        import logging as _logging

        _logging.getLogger(__name__).warning("goal judge check failed, allowing lifecycle handoff: %s",
                                             judge_exc, exc_info=True)
    if transport_failed:
        # ``judge_goal`` fails open to ``continue`` on transport errors (relay 400, auth, timeout);
        # an unreachable judge is not a human "not done" and must not reject the handoff (#83610).
        import logging as _logging

        _logging.getLogger(__name__).warning("goal judge unreachable (%s), allowing lifecycle handoff", reason)
        return ("done", None)
    return (verdict, None if verdict == "done" else reason)


def _goal_gate_error(conn, tid: str, evidence: str, handoff: str, blocked_hint: str,
                     continue_hint: str) -> Optional[str]:
    """Goal-mode judge gate shared by ``complete`` / ``request-review`` (mirrors tools/kanban_tools.py);
    applied to every terminal handoff so request-review can't bypass it. Returns the error line, or
    None to allow."""
    verdict, rejection = _goal_mode_handoff_rejection(kb.get_task(conn, tid), evidence)
    if verdict == "blocked":
        return (f"kanban: goal {handoff} of {tid} rejected: judge ruled "
                f"the goal unachievable — {rejection}. {blocked_hint}")
    if rejection is not None:
        return f"kanban: goal {handoff} of {tid} rejected by judge: {rejection}. {continue_hint}"
    return None


def _cmd_complete(args: argparse.Namespace) -> int:
    """Mark one or more tasks done. Supports a single id or a list."""
    ids, rc = _require_ids(args)
    if rc:
        return rc
    summary = getattr(args, "summary", None)
    raw_meta = getattr(args, "metadata", None)
    # Handoff fields are per-run; refuse to copy them across N runs.
    if len(ids) > 1 and (summary or raw_meta):
        return _err("kanban: --summary / --metadata are per-task and can't be used "
                    "with multiple ids (would apply the same handoff to every task). "
                    "Complete tasks one at a time, or drop the flags for the bulk close.", 2)
    metadata, rc = _parse_metadata_flag(raw_meta)
    if rc:
        return rc
    fail_msg: dict[str, str] = {}
    with kbc.connect_closing() as conn:
        def op(tid):
            gate_err = _goal_gate_error(
                conn, tid, (summary or args.result or "").strip(), "completion",
                "Re-scope with kanban edit, or record the block with kanban block instead of completing.",
                "Provide evidence matching the task's acceptance criteria.")
            if gate_err:
                fail_msg[tid] = gate_err
                return False
            fail_msg[tid] = f"cannot complete {tid} (unknown id or terminal state)"
            try:
                done = kb.complete_task(conn, tid, result=args.result, summary=summary, metadata=metadata,
                                        expected_run_id=_worker_run_id_for(tid),
                                        force=bool(getattr(args, "force", False)))
            except kb.LiveClaimError:
                fail_msg[tid] = (f"cannot complete {tid}: a live worker is running it. Wait for the "
                                 f"worker, `hermes kanban reclaim {tid}` to release it, or re-run with "
                                 f"--force to close its run and complete anyway.")
                return False
            except kb.EmptyCompletionError as empty_err:
                fail_msg[tid] = (f"cannot complete {tid}: {empty_err}. Pass --result/--summary "
                                 f"describing what was done (an empty completion is not evidence).")
                return False
            if not done:
                # complete_task returns bare False for a dependency refusal too;
                # name the open parents instead of claiming the id is unknown.
                blockers = kb.unsatisfied_parents(conn, tid)
                if blockers:
                    detail = ", ".join(f"{pid} ({status})" for pid, status in blockers)
                    fail_msg[tid] = (f"cannot complete {tid}: unsatisfied parent dependencies: {detail}; "
                                     f"complete the parents first, or `hermes kanban unlink <parent> {tid}`.")
            return done

        return _bulk_apply(ids, op, lambda tid: f"Completed {tid}", fail_msg.__getitem__)


def _cmd_edit(args: argparse.Namespace) -> int:
    result = getattr(args, "result", None)
    raw_metadata = getattr(args, "metadata", None)
    summary = getattr(args, "summary", None)
    title = getattr(args, "title", None)
    body = getattr(args, "body", None)
    priority = getattr(args, "priority", None)
    if result is None and (summary is not None or raw_metadata is not None):
        return _err("kanban edit: --summary and --metadata require --result", 2)
    if all(value is None for value in (title, body, priority, result)):
        return _err("kanban edit: provide --title, --body, --priority, or --result", 2)
    metadata, rc = _parse_metadata_flag(raw_metadata)
    if rc:
        return rc
    with kbc.connect_closing() as conn:
        ok = kb.edit_task(
            conn, args.task_id, title=title, body=body, priority=priority,
            result=result, summary=summary, metadata=metadata,
        )
    return _ok_or_err(
        ok,
        f"cannot edit {args.task_id} (unknown id, or --result used on a task that is not done)",
        f"Edited {args.task_id}",
    )


def _commented(conn, reason: Optional[str], author, prefix: str, op):
    """Wrap a per-task ``op`` so a ``reason`` is first recorded as a ``PREFIX: reason`` comment."""
    def run(tid):
        if reason:
            kb.add_comment(conn, tid, author, f"{prefix}: {reason}")
        return op(tid)
    return run


def _cmd_block(args: argparse.Namespace) -> int:
    reason = _joined_words(args.reason)
    kind = getattr(args, "kind", None)
    author = _profile_author()
    ids = _bulk_ids(args)
    suffix = f": {reason}" if reason else ""
    with kbc.connect_closing() as conn:
        def ok_msg(tid):
            # Report where it landed: dependency blocks -> todo, tripped unblock-loop breaker -> triage.
            landed = kb.get_task(conn, tid)
            where = landed.status if landed else "blocked"
            if where == "todo":
                return f"{tid} → todo (dependency wait){suffix}"
            if kind == "dependency" and where == "blocked":
                return f"Blocked {tid} as needs_input (no open parent to wait on){suffix}"
            if where == "triage":
                # Only a typed owner-input block carries a question for a human.
                verdict = ("needs a human decision" if (landed.block_kind if landed else kind) == "needs_input"
                           else "orchestration attention needed")
                return f"{tid} → triage (unblock loop detected — {verdict}){suffix}"
            return f"Blocked {tid}{suffix}"

        op = _commented(conn, reason, author, "BLOCKED", lambda tid: kb.block_task(
            conn, tid, reason=reason, kind=kind, expected_run_id=_worker_run_id_for(tid)))
        return _bulk_apply(ids, op, ok_msg, lambda tid: f"cannot block {tid}")


def _cmd_schedule(args: argparse.Namespace) -> int:
    reason = _joined_words(args.reason)
    author = _profile_author()
    ids = _bulk_ids(args)
    suffix = f": {reason}" if reason else ""
    with kbc.connect_closing() as conn:
        op = _commented(conn, reason, author, "SCHEDULED", lambda tid: kb.schedule_task(
            conn, tid, reason=reason, expected_run_id=_worker_run_id_for(tid)))
        return _bulk_apply(ids, op, lambda tid: f"Scheduled {tid}{suffix}", lambda tid: f"cannot schedule {tid}")


def _cmd_unblock(args: argparse.Namespace) -> int:
    if os.environ.get("HERMES_KANBAN_TASK"):
        return _err("kanban unblock is orchestrator-only; workers must hand off their assigned task")
    ids, rc = _require_ids(args)
    if rc:
        return rc
    reason = _stripped_or_none(getattr(args, "reason", None))
    author = _profile_author() if reason else None
    suffix = f": {reason}" if reason else ""
    with kbc.connect_closing() as conn:
        op = _commented(conn, reason, author, "UNBLOCK", lambda tid: kb.unblock_task(conn, tid))
        return _bulk_apply(ids, op, lambda tid: f"Unblocked {tid}{suffix}",
                           lambda tid: f"cannot unblock {tid} (not blocked/scheduled?)")


def _cmd_request_review(args: argparse.Namespace) -> int:
    tid = args.task_id
    summary = _stripped_or_none(getattr(args, "summary", None))
    metadata, rc = _parse_metadata_flag(getattr(args, "metadata", None))
    if rc:
        return rc
    with kbc.connect_closing() as conn:
        gate_err = _goal_gate_error(
            conn, tid, summary or "", "review handoff",
            "Record the block with kanban block instead of requesting review.",
            "Provide acceptance evidence matching the task.")
        if gate_err:
            return _err(gate_err)
        ok, reason = kb.request_review(
            conn, tid, summary=summary, metadata=metadata, reviewer=getattr(args, "reviewer", None),
            expected_run_id=_worker_run_id_for(tid), force=bool(getattr(args, "force", False)), with_reason=True)
        if not ok:
            return _err(f"cannot request review for {tid}: {reason or 'not running/ready?'}")
        persisted_run = kb.latest_run(conn, tid)
        display_summary = persisted_run.summary if persisted_run else None
        print(f"Requested review for {tid}" + (f": {display_summary}" if display_summary else ""))
    return 0


def _cmd_request_changes(args: argparse.Namespace) -> int:
    tid = args.task_id
    reason = " ".join(args.reason).strip()
    with kbc.connect_closing() as conn:
        ok, detail = kb.request_changes(conn, tid, reason=reason, expected_run_id=_worker_run_id_for(tid))
        if not ok:
            return _err(f"cannot request changes for {tid}: {detail or 'invalid review state'}")
        print(f"Requested changes for {tid}" + (f"; routed to {detail}" if detail else ""))
    return 0


def _cmd_reopen_review(args: argparse.Namespace) -> int:
    ids, rc = _require_ids(args)
    if rc:
        return rc
    reason = getattr(args, "reason", None)
    if reason is not None:
        reason = str(kb.redact_review_value(reason.strip())).strip() or None
    author = _profile_author() if reason else None
    suffix = f": {reason}" if reason else ""
    with kbc.connect_closing() as conn:
        def op(tid):
            if not kb.reopen_review_task(conn, tid):
                return False
            if reason:
                kb.add_comment(conn, tid, author or "operator", f"CHANGES REQUESTED: {reason}")
            return True

        return _bulk_apply(ids, op, lambda tid: f"Reopened {tid}{suffix}",
                           lambda tid: f"cannot reopen {tid} (not in review?)")


def _cmd_promote(args: argparse.Namespace) -> int:
    reason = _joined_words(args.reason)
    author = _profile_author()
    # Dedupe while preserving order; positional task_id always first.
    ids = list(dict.fromkeys(_bulk_ids(args)))
    dry_run = bool(args.dry_run)

    results: list[dict[str, object]] = []
    with kbc.connect_closing() as conn:
        for tid in ids:
            ok, err = kb.promote_task(conn, tid, actor=author, reason=reason, dry_run=dry_run)
            results.append({"task_id": tid, "promoted": ok, "dry_run": dry_run,
                            "reason": reason, "error": err})

    failed = [r for r in results if not r["promoted"]]
    if getattr(args, "json", False):
        # Single-id stays a flat object for back-compat; bulk emits a list.
        _print_json(results[0] if len(results) == 1 else results)
        return 0 if not failed else 1

    tag = " (dry)" if dry_run else ""
    label = "Would promote" if dry_run else "Promoted"
    suffix = f": {reason}" if reason else ""
    for r in results:
        if r["promoted"]:
            print(f"{label} {r['task_id']} -> ready{tag}{suffix}")
        else:
            print(f"cannot promote {r['task_id']}: {r['error']}", file=sys.stderr)
    return 0 if not failed else 1


def _cmd_archive(args: argparse.Namespace) -> int:
    ids = list(args.task_ids or [])
    purge_ids = list(getattr(args, "purge_ids", None) or [])
    if ids and purge_ids:
        return _err("choose either task_ids to archive or --rm archived task_ids")
    if not ids and not purge_ids:
        return _err("at least one task_id is required")
    with kbc.connect_closing() as conn:
        if purge_ids:
            return _bulk_apply(purge_ids, lambda tid: kb.delete_archived_task(conn, tid), lambda tid: f"Deleted {tid}",
                               lambda tid: f"cannot delete {tid} (must already be archived)")
        return _bulk_apply(ids, lambda tid: kb.archive_task(conn, tid),
                           lambda tid: f"Archived {tid}", lambda tid: f"cannot archive {tid}")


def _cmd_stats(args: argparse.Namespace) -> int:
    with kbc.connect_closing() as conn:
        stats = kb.board_stats(conn)
    if _json_out(args, stats):
        return 0
    print("By status:")
    for k in ("triage", "todo", "scheduled", "ready", "running", "blocked", "done"):
        print(f"  {k:8s}  {stats['by_status'].get(k, 0)}")
    if stats["by_assignee"]:
        print("\nBy assignee:")
        for who, counts in sorted(stats["by_assignee"].items()):
            print(f"  {who:20s}  {_fmt_counts(counts)}")
    age = stats["oldest_ready_age_seconds"]
    if age is not None:
        print(f"\nOldest ready task age: {int(age)}s")
    return 0


def _cmd_notify_subscribe(args: argparse.Namespace) -> int:
    delivery_metadata = {
        key: value
        for key, value in (
            ("parent_chat_id", getattr(args, "parent_chat_id", None)),
            ("guild_id", getattr(args, "guild_id", None)),
        )
        if value
    }
    with kbc.connect_closing() as conn:
        if kb.get_task(conn, args.task_id) is None:
            return _err(f"no such task: {args.task_id}")
        kbn.add_notify_sub(
            conn, task_id=args.task_id, platform=args.platform, chat_id=args.chat_id,
            chat_type=args.chat_type, thread_id=args.thread_id, user_id=args.user_id,
            user_id_alt=getattr(args, "user_id_alt", None),
            notifier_profile=args.notifier_profile or _profile_author(),
            delivery_mode=getattr(args, "delivery_mode", None),
            delivery_metadata=delivery_metadata or None,
        )
    print(f"Subscribed {args.platform}:{args.chat_id}" + (f":{args.thread_id}" if args.thread_id else "")
          + f" to {args.task_id}")
    return 0


def _cmd_notify_list(args: argparse.Namespace) -> int:
    with kbc.connect_closing() as conn:
        subs = kbn.list_notify_subs(conn, args.task_id)
    if _json_out(args, subs):
        return 0
    if not subs:
        print("(no subscriptions)")
        return 0
    for s in subs:
        thr = f":{s['thread_id']}" if s.get("thread_id") else ""
        dmode, ctype = s.get("delivery_mode") or "notify", s.get("chat_type") or "dm"
        extras = "".join((
            f"  owner={s['notifier_profile']}" if s.get("notifier_profile") else "",
            "" if ctype == "dm" else f"  chat_type={ctype}",
            f"  user_id_alt={s['user_id_alt']}" if s.get("user_id_alt") else "",
            "" if dmode == "notify" else f"  mode={dmode}",
        ))
        print(f"  {s['task_id']:10s}  {s['platform']}:{s['chat_id']}{thr}  (since event {s['last_event_id']}){extras}")
    return 0


def _cmd_notify_unsubscribe(args: argparse.Namespace) -> int:
    with kbc.connect_closing() as conn:
        ok = kbn.remove_notify_sub(conn, task_id=args.task_id, platform=args.platform, chat_id=args.chat_id,
                                  thread_id=args.thread_id)
    return _ok_or_err(ok, "(no such subscription)", f"Unsubscribed from {args.task_id}")


def _cmd_log(args: argparse.Namespace) -> int:
    content = kb.read_worker_log(args.task_id, tail_bytes=args.tail)
    if content is None:
        return _err(f"(no log for {args.task_id} — task may not have spawned yet)")
    sys.stdout.write(content)
    if not content.endswith("\n"):
        sys.stdout.write("\n")
    return 0


def _cmd_runs(args: argparse.Namespace) -> int:
    """Show attempt history for a task."""
    rsk, rc = _run_state_kwargs(args, "runs")
    if rc:
        return rc
    with kbc.connect_closing() as conn:
        runs = kb.list_runs(conn, args.task_id, **rsk)
    if _json_out(args, [_obj_dict(r, _RUNS_RUN_FIELDS) for r in runs]):
        return 0
    if not runs:
        print(f"(no runs yet for {args.task_id})")
        return 0
    print(f"{'#':3s}  {'OUTCOME':12s}  {'PROFILE':16s}  {'ELAPSED':>8s}  STARTED")
    for i, r in enumerate(runs, 1):
        end = r.ended_at or int(time.time())
        # Clamp to 0 so NTP backward-jumps don't print negative durations.
        elapsed = max(0, end - r.started_at)
        el = f"{elapsed}s" if elapsed < 60 else f"{elapsed // 60}m" if elapsed < 3600 else f"{elapsed / 3600:.1f}h"
        outcome = r.outcome or ("(running)" if not r.ended_at else r.status)
        print(f"{i:3d}  {outcome:12s}  {(r.profile or '-'):16s}  {el:>8s}  {_fmt_ts(r.started_at)}")
        if r.summary:
            print(f"     → {r.summary.splitlines()[0][:100]}")
        if r.error:
            print(f"     ✖ {r.error[:100]}")
    return 0


def _cmd_context(args: argparse.Namespace) -> int:
    with kbc.connect_closing() as conn:
        text = kb.build_worker_context(conn, args.task_id)
    print(text)
    return 0


def _run_triage_sweep(args: argparse.Namespace, verb: str, mod, run_one, json_key: str,
                      json_fields: tuple[str, ...], human_ok) -> int:
    """Shared driver for ``specify`` / ``decompose``: validate ids (one task id XOR ``--all``), run
    ``run_one(tid, author=...)`` per id, print JSON or human lines, exit code."""
    all_flag = bool(getattr(args, "all_triage", False))
    author = getattr(args, "author", None) or _profile_author()
    want_json = bool(getattr(args, "json", False))
    tenant = getattr(args, "tenant", None)
    if args.task_id and all_flag:
        return _err("kanban: pass either a task id OR --all, not both", 2)
    if all_flag:
        ids = mod.list_triage_ids(tenant=tenant)
        if not ids:
            if want_json:
                print(json.dumps({json_key: 0, "total": 0}))
            else:
                print("No triage tasks" + (f" for tenant {tenant!r}" if tenant else "") + ".")
            return 0
    elif args.task_id:
        ids = [args.task_id]
    else:
        return _err(f"kanban: {verb} requires a task id or --all", 2)

    ok_count = 0
    for tid in ids:
        outcome = run_one(tid, author=author)
        if outcome.ok:
            ok_count += 1
        if want_json:
            print(json.dumps(_obj_dict(outcome, json_fields)))
        elif outcome.ok:
            print(human_ok(outcome))
        else:
            print(f"kanban: {verb} {outcome.task_id}: {outcome.reason}", file=sys.stderr)
    if not all_flag:
        return 0 if ok_count == 1 else 1
    # --all: exit 1 only when every candidate failed (honest signal for scripts).
    return 0 if (ok_count > 0 or not ids) else 1


def _retitled_suffix(outcome) -> str:
    return f" — retitled: {outcome.new_title!r}" if outcome.new_title else ""


def _cmd_specify(args: argparse.Namespace) -> int:
    """Spec a triage task (or all) via the auxiliary LLM, promote to todo."""
    from hermes_cli import kanban_specify as spec

    return _run_triage_sweep(args, "specify", spec, spec.specify_task, "specified",
                             ("task_id", "ok", "reason", "new_title"),
                             lambda o: f"Specified {o.task_id} → todo{_retitled_suffix(o)}")


def _decompose_ok_line(o) -> str:
    if o.fanout and o.child_ids:
        return (f"Decomposed {o.task_id} → {len(o.child_ids)} "
                f"children ({', '.join(o.child_ids)}); root promoted to todo")
    return f"Specified {o.task_id} → todo (no fanout){_retitled_suffix(o)}"


def _cmd_decompose(args: argparse.Namespace) -> int:
    """Fan a triage task (or all) out into child tasks via the auxiliary LLM."""
    from hermes_cli import kanban_decompose as decomp

    return _run_triage_sweep(args, "decompose", decomp, decomp.decompose_task, "decomposed",
                             ("task_id", "ok", "reason", "fanout", "child_ids", "new_title"), _decompose_ok_line)


_HANDLERS = {
    "init": _cmd_init, "create": _cmd_create, "swarm": _cmd_swarm,
    "list": _cmd_list, "ls": _cmd_list, "show": _cmd_show,
    "assign": _cmd_assign, "set-model": _cmd_set_model,
    "reclaim": _cmd_reclaim, "reassign": _cmd_reassign,
    "diagnostics": _cmd_diagnostics, "diag": _cmd_diagnostics,
    "link": _cmd_link, "unlink": _cmd_unlink, "claim": _cmd_claim,
    "comment": _cmd_comment, "attach": _cmd_attach,
    "attachments": _cmd_attachments, "attach-rm": _cmd_attach_rm,
    "complete": _cmd_complete, "edit": _cmd_edit, "block": _cmd_block,
    "schedule": _cmd_schedule, "unblock": _cmd_unblock,
    "request-review": _cmd_request_review, "request-changes": _cmd_request_changes,
    "reopen-review": _cmd_reopen_review, "promote": _cmd_promote,
    "archive": _cmd_archive, "tail": _cmd_tail, "dispatch": _cmd_dispatch,
    "daemon": _cmd_daemon, "watch": _cmd_watch, "stats": _cmd_stats,
    "log": _cmd_log, "runs": _cmd_runs, "heartbeat": _cmd_heartbeat,
    "assignees": _cmd_assignees, "notify-subscribe": _cmd_notify_subscribe,
    "notify-list": _cmd_notify_list, "notify-unsubscribe": _cmd_notify_unsubscribe,
    "context": _cmd_context, "specify": _cmd_specify, "decompose": _cmd_decompose,
    "gc": _cmd_gc,
}


# --- Slash-command entry point (used by /kanban from CLI and gateway) ---

_SLASH_KANBAN_HELP = """\
**/kanban** — manage the shared task board.

Common subcommands:
  `list` (alias `ls`)   List tasks on the current board
  `show <id>`           Task details + comments + events
  `stats`               Per-status / per-assignee counts
  `create <title>…`     Create a task (auto-subscribes you to events)
  `comment <id> <msg>`  Append a comment
  `attach <id> <path>`  Attach a local file; `attachments <id>` to list
  `complete <id>…`      Mark task(s) done
  `request-review <id>` Enter first-class review; `request-changes <id> <reason>` returns an active review to its implementer
  `block <id> [reason]` Mark blocked; `schedule <id> [reason]` parks time-delay work; `unblock <id>` to revive
  `assign <id> <profile>`  Reassign
  `boards list`         Show all boards
  `assignees`           Known profiles + counts
  `context <id>`        Full worker-context dump
  `runs <id>`           Attempt history
  `log <id>`            Worker log

Run `/kanban <subcommand> -h` for arguments. \
Read-only commands are safe while an agent is running.\
"""


def run_slash(rest: str) -> str:
    """Execute a ``/kanban …`` string (``rest`` = everything after ``/kanban``) and return captured
    stdout/stderr. Shared by the interactive CLI and the gateway so formatting is identical."""
    import io

    # Non-posix split (Windows) keeps backslashes as path separators but
    # leaves quote characters in the tokens — strip a fully wrapping pair
    # so `"my task"` reaches argparse as `my task`, not `"my task"`.
    tokens = []
    if rest and rest.strip():
        for tok in shlex.split(rest, posix=os.name == "posix"):
            if len(tok) >= 2 and tok[0] == tok[-1] and tok[0] in ("'", '"'):
                tok = tok[1:-1]
            tokens.append(tok)

    # Bare ``/kanban`` or ``/kanban help`` / ``--help`` / ``-h`` / ``?``:
    # show the curated short-help block instead of dumping argparse's full
    # usage tree (which is enormous and reads as garbage in a chat
    # bubble).  Per-subcommand help still works via ``/kanban foo -h``.
    if not tokens or tokens[0] in {"help", "--help", "-h", "?"}:
        return _SLASH_KANBAN_HELP
    # build_parser() needs a subparsers action to attach to: build a throwaway one and drive
    # kanban_parser directly so usage/error text reads ``/kanban``.
    _wrap = argparse.ArgumentParser(prog="/kanban-wrap", add_help=False)
    _wrap.exit_on_error = False  # type: ignore[attr-defined]
    kanban_parser = build_parser(_wrap.add_subparsers(dest="_top"))
    kanban_parser.prog = "/kanban"
    kanban_parser.exit_on_error = False  # type: ignore[attr-defined]
    subparsers = [a for a in kanban_parser._actions if isinstance(a, argparse._SubParsersAction)]
    for _action in subparsers:
        for _name, _choice in _action.choices.items():
            _choice.prog = f"/kanban {_name}"
            _choice.exit_on_error = False  # type: ignore[attr-defined]

    def _usage_for_error() -> str:
        if tokens:
            for _action in subparsers:
                subparser = _action.choices.get(tokens[0])
                if subparser is not None:
                    return subparser.format_usage().rstrip()
        return kanban_parser.format_usage().rstrip()

    buf_out, buf_err = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
            args = kanban_parser.parse_args(tokens)
    except SystemExit as exc:
        out, err = buf_out.getvalue().rstrip(), buf_err.getvalue().rstrip()
        if exc.code in {0, None} and out:  # ``-h`` help dump
            return out
        body = err or out
        return f"⚠ /kanban usage error\n{body}" if body else "⚠ /kanban usage error"
    except argparse.ArgumentError as exc:
        return f"⚠ /kanban usage error\n{_usage_for_error()}\n{exc}"

    with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
        try:
            kanban_command(args)
        except SystemExit:
            pass
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)

    out, err = buf_out.getvalue().rstrip(), buf_err.getvalue().rstrip()
    if err and out:
        return f"{out}\n{err}"
    return err if err else (out or "(no output)")


_PLANNER_HANDLERS = {
    "planner": _cmd_planner,
    "planner-preview": _cmd_planner_preview,
    "pre-gate-preview": _cmd_pre_gate_preview,
    "watchdog-preview": _cmd_watchdog_preview,
}
