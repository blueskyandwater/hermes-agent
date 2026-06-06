"""Regression tests for #28712 — kanban dispatcher must not auto-promote
worker-initiated ``kanban_block`` (sticky blocks), but must keep
auto-recovering circuit-breaker blocks.

The bug: when a worker called ``kanban_block(reason="review-required:
...")`` to hand off to a human, the dispatcher's ``recompute_ready``
would promote the task back to ``ready`` on the next tick.  The fresh
worker found nothing to do (work already applied), exited cleanly, and
got recorded as a ``protocol_violation`` → ``gave_up`` → promote → loop
until manual intervention.

These tests pin down:

* Worker / operator-initiated blocks are sticky and survive
  ``recompute_ready``.
* Circuit-breaker blocks (``gave_up`` event, status flipped via
  ``_record_task_failure``) still auto-recover — the original intent
  of #40c1decb3 is preserved.
* An explicit ``kanban_unblock`` clears the sticky state.
* The full block → promote → crash → ``gave_up`` loop is broken after
  this fix: subsequent ticks leave the task blocked.

The tangentially related schema-init ordering bug originally reported
in #28712 (``init_db`` crashing on legacy DBs that pre-dated the
``session_id`` migration) is covered separately by
``test_kanban_db.py::test_connect_migrates_legacy_db_before_optional_column_indexes``,
landed via #28754 / #28781 ahead of this fix.
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from hermes_cli import kanban_db as kb


@pytest.fixture
def kanban_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Isolated HERMES_HOME with an empty kanban DB."""
    home = tmp_path / ".hermes"
    home.mkdir()
    monkeypatch.setenv("HERMES_HOME", str(home))
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    kb.init_db()
    return home


# ---------------------------------------------------------------------------
# Worker-initiated kanban_block must be sticky
# ---------------------------------------------------------------------------


def test_worker_block_is_not_auto_promoted_by_recompute_ready(kanban_home: Path) -> None:
    """A standalone task that a worker explicitly blocks for review
    must stay blocked across an arbitrary number of dispatcher ticks.
    Before #28712's fix, ``recompute_ready`` would silently flip it
    back to ``ready`` on the very next tick."""
    with kb.connect() as conn:
        tid = kb.create_task(conn, title="needs human review")
        kb.claim_task(conn, tid)
        assert kb.block_task(
            conn, tid,
            reason="review-required: please verify ACL change",
            expected_run_id=kb.get_task(conn, tid).current_run_id,
        )
        assert kb.get_task(conn, tid).status == "blocked"

        # Hammer the promotion code — exactly the dispatcher loop's
        # behaviour, just compressed in time.
        for _ in range(5):
            promoted = kb.recompute_ready(conn)
            assert promoted == 0, "worker-blocked task must not auto-promote"
            assert kb.get_task(conn, tid).status == "blocked"


def test_worker_block_on_child_with_done_parents_is_still_sticky(kanban_home: Path) -> None:
    """The parent-completion path is the one ``recompute_ready`` was
    designed for, so it's the most dangerous false-positive: even when
    every parent is done, a worker-initiated block on the child must
    stay blocked."""
    with kb.connect() as conn:
        parent = kb.create_task(conn, title="parent")
        child = kb.create_task(conn, title="child", parents=[parent])
        kb.complete_task(conn, parent, result="parent ok")

        kb.claim_task(conn, child)
        kb.block_task(
            conn, child,
            reason="review-required: child needs sign-off",
            expected_run_id=kb.get_task(conn, child).current_run_id,
        )
        assert kb.get_task(conn, child).status == "blocked"

        promoted = kb.recompute_ready(conn)
        assert promoted == 0
        assert kb.get_task(conn, child).status == "blocked"


# ---------------------------------------------------------------------------
# Circuit-breaker blocks still auto-recover (preserve #40c1decb3 intent)
# ---------------------------------------------------------------------------


def test_circuit_breaker_block_still_auto_promotes(kanban_home: Path) -> None:
    """A child that was put into ``blocked`` *without* a worker-issued
    ``kanban_block`` (e.g. a transient crash, manual DB triage) and whose
    ``consecutive_failures`` is still *below* the circuit-breaker limit
    must get auto-promoted when its parents complete — preserves the
    pre-#28712 recovery semantics for genuinely transient failures.

    The complementary case — a block whose failure count has *reached*
    the limit must stay blocked — is covered by
    ``test_kanban_db.py::test_recompute_ready_skips_tasks_at_failure_limit``
    (#35072).  Together they pin the contract: ``recompute_ready`` defers
    the give-up decision to the same effective limit the breaker uses, so
    the two never disagree.
    """
    with kb.connect() as conn:
        parent = kb.create_task(conn, title="parent")
        child = kb.create_task(conn, title="child", parents=[parent])
        kb.complete_task(conn, parent, result="ok")

        # Simulate a transient circuit-breaker / direct triage that flips
        # status without emitting a ``blocked`` event — exactly what
        # ``_record_task_failure`` does below the limit.  One failure is
        # under the default limit (2), so recovery is still correct.
        conn.execute(
            "UPDATE tasks SET status='blocked', consecutive_failures=1, "
            "last_failure_error='transient error' WHERE id=?",
            (child,),
        )
        conn.commit()

        promoted = kb.recompute_ready(conn)
        assert promoted == 1
        task = kb.get_task(conn, child)
        assert task.status == "ready"
        # Counter is preserved across recovery (not reset) so the breaker
        # can still accumulate if the task keeps failing (#35072).
        assert task.consecutive_failures == 1


def test_gave_up_event_alone_does_not_make_block_sticky(kanban_home: Path) -> None:
    """The circuit-breaker emits ``gave_up`` (not ``blocked``).  Make
    sure ``_has_sticky_block`` doesn't accidentally treat ``gave_up``
    as sticky — otherwise we'd regress the safety net for genuinely
    transient crashes."""
    with kb.connect() as conn:
        parent = kb.create_task(conn, title="parent")
        child = kb.create_task(conn, title="child", parents=[parent])
        kb.complete_task(conn, parent, result="ok")

        # Status + event match what _record_task_failure writes when
        # the breaker trips.
        conn.execute(
            "UPDATE tasks SET status='blocked' WHERE id=?", (child,),
        )
        conn.execute(
            "INSERT INTO task_events (task_id, kind, payload, created_at) "
            "VALUES (?, 'gave_up', NULL, ?)",
            (child, int(time.time())),
        )
        conn.commit()

        promoted = kb.recompute_ready(conn)
        assert promoted == 1
        assert kb.get_task(conn, child).status == "ready"


# ---------------------------------------------------------------------------
# unblock_task clears the sticky state
# ---------------------------------------------------------------------------


def test_unblock_clears_sticky_state_and_lets_block_recover(kanban_home: Path) -> None:
    """``hermes kanban unblock`` (or the ``kanban_unblock`` tool) is
    the only legitimate way out of a worker-initiated block.  After
    unblock, a *subsequent* circuit-breaker block on the same task
    must again be eligible for auto-recovery."""
    with kb.connect() as conn:
        tid = kb.create_task(conn, title="t")
        kb.claim_task(conn, tid)
        kb.block_task(
            conn, tid,
            reason="review-required: ...",
            expected_run_id=kb.get_task(conn, tid).current_run_id,
        )
        assert kb.unblock_task(conn, tid)
        # After unblock the task is no longer blocked at all.
        assert kb.get_task(conn, tid).status == "ready"

        # Now simulate a *later* circuit-breaker block (no new
        # ``blocked`` event, just status flip).  The most recent
        # block/unblock event is ``unblocked`` → guard does not fire
        # → recompute can recover.
        conn.execute(
            "UPDATE tasks SET status='blocked' WHERE id=?", (tid,),
        )
        conn.commit()

        promoted = kb.recompute_ready(conn)
        assert promoted == 1
        assert kb.get_task(conn, tid).status == "ready"


# ---------------------------------------------------------------------------
# Full bug-shaped loop: block → promote → crash → gave_up → next tick
# ---------------------------------------------------------------------------


def test_protocol_violation_loop_is_broken(kanban_home: Path) -> None:
    """Reproduces the exact #28712 loop and asserts the dispatcher
    leaves the task blocked instead of cycling.

    Loop shape from the issue:

    1. Worker calls ``kanban_block`` → status='blocked',
       ``task_runs.outcome='blocked'``, ``blocked`` event.
    2. (Bug) Dispatcher promotes back to ``ready``.
    3. Fresh worker exits cleanly without terminal tool call →
       ``protocol_violation`` event.
    4. ``_record_task_failure(failure_limit=1)`` → ``gave_up`` event,
       status='blocked' again.
    5. (Bug) Dispatcher promotes again → infinite loop.

    With the fix in place, step 2 never happens — the test simulates
    one would-be loop cycle by faking the crash-then-gave_up entries
    that *would* have been written and asserts the *next* tick still
    leaves the task blocked.
    """
    with kb.connect() as conn:
        tid = kb.create_task(conn, title="loop reproducer")
        kb.claim_task(conn, tid)
        kb.block_task(
            conn, tid,
            reason="review-required: human eyes please",
            expected_run_id=kb.get_task(conn, tid).current_run_id,
        )
        assert kb.get_task(conn, tid).status == "blocked"

        # First dispatcher tick — must NOT promote.
        assert kb.recompute_ready(conn) == 0
        assert kb.get_task(conn, tid).status == "blocked"

        # Simulate the (hypothetical) protocol_violation + gave_up
        # entries that the dispatcher would have written if the bug
        # were still present.  Even with those event rows in place,
        # the worker-initiated ``blocked`` event is the most recent
        # of the ``{blocked, unblocked}`` pair, so the sticky guard
        # still fires.
        now = int(time.time())
        conn.execute(
            "INSERT INTO task_events (task_id, kind, payload, created_at) "
            "VALUES (?, 'protocol_violation', NULL, ?)",
            (tid, now),
        )
        conn.execute(
            "INSERT INTO task_events (task_id, kind, payload, created_at) "
            "VALUES (?, 'gave_up', NULL, ?)",
            (tid, now + 1),
        )
        conn.commit()

        # Subsequent ticks must still leave it blocked.
        for _ in range(3):
            promoted = kb.recompute_ready(conn)
            assert promoted == 0
            assert kb.get_task(conn, tid).status == "blocked"


# ---------------------------------------------------------------------------
# Schema-init recovery on legacy DBs is covered by
# tests/hermes_cli/test_kanban_db.py::test_connect_migrates_legacy_db_before_optional_column_indexes
# (landed via #28754 / #28781).  The original PR shipped a duplicate test
# here; dropped during salvage to avoid two assertions of the same contract.
# ---------------------------------------------------------------------------


def test_review_required_auto_creates_review_card(kanban_home: Path) -> None:
    with kb.connect() as conn, pytest.MonkeyPatch.context() as mp:
        mp.setattr("hermes_cli.profiles.profile_exists", lambda name: name in {"review-worker", "code-worker"})
        tid = kb.create_task(conn, title="needs review", assignee="code-worker")
        kb.claim_task(conn, tid)
        kb.block_task(
            conn, tid,
            reason="review-required: verify final diff and tests",
            expected_run_id=kb.get_task(conn, tid).current_run_id,
        )
        tasks = kb.list_tasks(conn)
        reviews = [t for t in tasks if t.assignee == "review-worker" and t.id != tid]
        assert len(reviews) == 1
        assert "AUTO_REVIEW_TARGET_TASK_ID=" in (reviews[0].body or "")


def test_auto_review_pass_completes_target_task(kanban_home: Path) -> None:
    with kb.connect() as conn, pytest.MonkeyPatch.context() as mp:
        mp.setattr("hermes_cli.profiles.profile_exists", lambda name: name in {"review-worker", "code-worker"})
        target = kb.create_task(conn, title="impl", assignee="code-worker")
        kb.claim_task(conn, target)
        kb.block_task(
            conn, target,
            reason="review-required: verify",
            expected_run_id=kb.get_task(conn, target).current_run_id,
        )
        review = next(t for t in kb.list_tasks(conn) if t.assignee == "review-worker")
        kb.complete_task(
            conn,
            review.id,
            summary="pass: looks good",
            metadata={"review_decision": "pass"},
        )
        assert kb.get_task(conn, target).status == "done"


def test_auto_review_fail_spawns_repair_card(kanban_home: Path) -> None:
    with kb.connect() as conn, pytest.MonkeyPatch.context() as mp:
        mp.setattr("hermes_cli.profiles.profile_exists", lambda name: name in {"review-worker", "code-worker"})
        target = kb.create_task(conn, title="impl", assignee="code-worker")
        kb.claim_task(conn, target)
        kb.block_task(
            conn, target,
            reason="review-required: verify",
            expected_run_id=kb.get_task(conn, target).current_run_id,
        )
        review = next(t for t in kb.list_tasks(conn) if t.assignee == "review-worker")
        kb.complete_task(
            conn,
            review.id,
            summary="fail: tests missing",
            metadata={"review_decision": "fail"},
        )
        repair_cards = [
            t for t in kb.list_tasks(conn)
            if t.assignee == "code-worker" and t.id not in {target, review.id}
        ]
        assert len(repair_cards) == 1
        assert repair_cards[0].status in {"ready", "todo"}


# ---------------------------------------------------------------------------
# Blocked-task watchdog: _reconcile_blocked_review_tasks heals orphan review
# cards when block_task()'s followup was lost (crash between status flip
# and _ensure_auto_review_followup).
# ---------------------------------------------------------------------------


def test_watchdog_heals_orphan_blocked_review_card(kanban_home: Path) -> None:
    """A blocked task whose review card was never created (simulating a
    crash after block_task() flipped the status but before
    _ensure_auto_review_followup) gets its review card re-created by
    _reconcile_blocked_review_tasks on the next dispatch tick."""
    with kb.connect() as conn, pytest.MonkeyPatch.context() as mp:
        mp.setattr("hermes_cli.profiles.profile_exists", lambda name: name in {"review-worker", "code-worker"})
        tid = kb.create_task(conn, title="watchdog target", assignee="code-worker")
        kb.claim_task(conn, tid)
        kb.block_task(
            conn, tid,
            reason="review-required: verify watchdog",
            expected_run_id=kb.get_task(conn, tid).current_run_id,
        )
        assert kb.get_task(conn, tid).status == "blocked"

        # Review card should have been created by block_task followup.
        tasks = kb.list_tasks(conn)
        reviews = [t for t in tasks if t.assignee == "review-worker" and t.id != tid]
        assert len(reviews) == 1, "review card must exist after normal block_task"

        # Now simulate the orphan: delete the review card (and its events/comments)
        review_id = reviews[0].id
        conn.execute("DELETE FROM task_events WHERE task_id = ?", (review_id,))
        conn.execute("DELETE FROM task_comments WHERE task_id = ?", (review_id,))
        conn.execute("DELETE FROM task_runs WHERE task_id = ?", (review_id,))
        conn.execute("DELETE FROM tasks WHERE id = ?", (review_id,))
        conn.commit()
        # Confirm it's gone.
        assert kb.get_task(conn, review_id) is None
        tasks = kb.list_tasks(conn)
        reviews = [t for t in tasks if t.assignee == "review-worker"]
        assert len(reviews) == 0, "review card should be gone after deletion"

        # Watchdog heals.
        healed = kb._reconcile_blocked_review_tasks(conn)
        assert len(healed) == 1
        assert healed[0] == tid

        # Review card re-created.
        tasks = kb.list_tasks(conn)
        reviews = [t for t in tasks if t.assignee == "review-worker"]
        assert len(reviews) == 1
        new_review = reviews[0]
        assert "AUTO_REVIEW_TARGET_TASK_ID=" in (new_review.body or "")
        assert new_review.status == "ready"

        # Second call is idempotent.
        healed2 = kb._reconcile_blocked_review_tasks(conn)
        assert len(healed2) == 0, "watchdog must be idempotent"


def test_watchdog_skips_non_review_blocked_tasks(kanban_home: Path) -> None:
    """Tasks blocked with a plain reason (not review-required:) are
    ignored by the watchdog."""
    with kb.connect() as conn, pytest.MonkeyPatch.context() as mp:
        mp.setattr("hermes_cli.profiles.profile_exists", lambda name: name in {"review-worker", "code-worker"})
        tid = kb.create_task(conn, title="non-review block")
        kb.claim_task(conn, tid)
        kb.block_task(
            conn, tid,
            reason="waiting on upstream dependency",
            expected_run_id=kb.get_task(conn, tid).current_run_id,
        )
        healed = kb._reconcile_blocked_review_tasks(conn)
        assert len(healed) == 0, "non-review block must not trigger watchdog"


def test_watchdog_in_dispatch_once_result(kanban_home: Path) -> None:
    """dispatch_once populates blocked_watchdog_healed when healing occurs."""
    with kb.connect() as conn, pytest.MonkeyPatch.context() as mp:
        mp.setattr("hermes_cli.profiles.profile_exists", lambda name: name in {"review-worker", "code-worker"})
        tid = kb.create_task(conn, title="dispatch watchdog", assignee="code-worker")
        kb.claim_task(conn, tid)
        kb.block_task(
            conn, tid,
            reason="review-required: verify dispatch path",
            expected_run_id=kb.get_task(conn, tid).current_run_id,
        )

        # Orphan the review card.
        tasks = kb.list_tasks(conn)
        review = next(t for t in tasks if t.assignee == "review-worker")
        conn.execute("DELETE FROM task_events WHERE task_id = ?", (review.id,))
        conn.execute("DELETE FROM task_comments WHERE task_id = ?", (review.id,))
        conn.execute("DELETE FROM task_runs WHERE task_id = ?", (review.id,))
        conn.execute("DELETE FROM tasks WHERE id = ?", (review.id,))
        conn.commit()

        # dispatch_once with no ready tasks to spawn.
        result = kb.dispatch_once(conn, dry_run=True)
        assert tid in result.blocked_watchdog_healed, f"expected {tid} in {result.blocked_watchdog_healed}"
        # Confirm the review card was actually re-created.
        tasks = kb.list_tasks(conn)
        reviews = [t for t in tasks if t.assignee == "review-worker"]
        assert len(reviews) == 1
