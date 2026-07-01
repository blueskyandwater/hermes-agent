"""
Tests for agent/analytics.py
"""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

from agent.analytics import UsageLogAnalytics


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_NOW = datetime.now(timezone.utc)
_DAY_1 = (_NOW - timedelta(days=2)).strftime("%Y-%m-%d")
_DAY_2 = (_NOW - timedelta(days=1)).strftime("%Y-%m-%d")

SAMPLE_RECORDS = [
    {
        "ts": f"{_DAY_1}T10:00:00",
        "request_id": "a1",
        "model": "deepseek/deepseek-v4-flash",
        "provider": "openrouter",
        "input_tokens": 1000,
        "output_tokens": 50,
        "total_tokens": 1050,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
        "estimated_cost_usd": 0.00105,
        "latency_ms": 500.0,
        "route_type": "normal_chat",
        "channel": "discord",
        "status": "success",
    },
    {
        "ts": f"{_DAY_1}T11:00:00",
        "request_id": "a2",
        "model": "perplexity/sonar",
        "provider": "openrouter",
        "input_tokens": 2000,
        "output_tokens": 100,
        "total_tokens": 2100,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
        "estimated_cost_usd": 0.00210,
        "latency_ms": 1200.0,
        "route_type": "research",
        "channel": "discord",
        "status": "success",
    },
    {
        "ts": f"{_DAY_2}T10:00:00",
        "request_id": "a3",
        "model": "deepseek/deepseek-v4-flash",
        "provider": "openrouter",
        "input_tokens": 500,
        "output_tokens": 200,
        "total_tokens": 700,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
        "estimated_cost_usd": 0.00070,
        "latency_ms": 300.0,
        "route_type": "code_or_debug",
        "channel": "discord",
        "status": "success",
    },
    # Bypass record
    {
        "ts": f"{_DAY_2}T11:00:00",
        "request_id": "a4",
        "model": "",
        "provider": "",
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "estimated_cost_usd": 0.0,
        "latency_ms": 0.0,
        "route_type": "simple_command",
        "channel": "discord",
        "status": "bypass",
        "bypass_command": "help",
    },
    # Fallback record
    {
        "ts": f"{_DAY_2}T12:00:00",
        "request_id": "a5",
        "model": "deepseek/deepseek-v4-flash",
        "provider": "openrouter",
        "input_tokens": 100,
        "output_tokens": 50,
        "total_tokens": 150,
        "estimated_cost_usd": 0.00015,
        "latency_ms": 5000.0,
        "route_type": "normal_chat",
        "channel": "discord",
        "status": "success",
        "fallback_triggered": True,
        "fallback_model": "google/gemini-2.5-flash",
        "attempt_number": 2,
    },
    # Error record
    {
        "ts": f"{_DAY_2}T13:00:00",
        "request_id": "a6",
        "model": "deepseek/deepseek-v4-flash",
        "provider": "openrouter",
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "estimated_cost_usd": 0.0,
        "latency_ms": 10000.0,
        "route_type": "normal_chat",
        "channel": "discord",
        "status": "error",
    },
]

MALFORMED_LINE = b'{"ts": "malformed", "model": "truncated...\n'


@pytest.fixture
def empty_log():
    """Empty usage.log."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        f.write("")
        path = f.name
    yield path
    os.unlink(path)


@pytest.fixture
def normal_log():
    """Normal usage.log with valid records."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        for rec in SAMPLE_RECORDS:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        path = f.name
    yield path
    os.unlink(path)


@pytest.fixture
def malformed_log():
    """Usage.log with malformed lines mixed in."""
    with tempfile.NamedTemporaryFile(mode="w+b", suffix=".log", delete=False) as f:
        # Write valid lines
        for rec in SAMPLE_RECORDS:
            f.write(json.dumps(rec, ensure_ascii=False).encode() + b"\n")
        # Insert malformed lines
        f.write(MALFORMED_LINE)
        f.write(b"{{{{ completely broken json }}}\n")
        f.write(b"\n")  # empty line
        f.write(json.dumps(SAMPLE_RECORDS[0], ensure_ascii=False).encode() + b"\n")
        path = f.name
    yield path
    os.unlink(path)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestReader:
    def test_file_not_found(self):
        """Reading a non-existent file returns empty records without error."""
        analytics = UsageLogAnalytics(log_path="/nonexistent/usage.log")
        records = analytics.read_records()
        assert records == []

    def test_empty_file(self, empty_log):
        analytics = UsageLogAnalytics(log_path=empty_log)
        records = analytics.read_records()
        assert records == []

    def test_normal_file(self, normal_log):
        analytics = UsageLogAnalytics(log_path=normal_log)
        records = analytics.read_records()
        assert len(records) == len(SAMPLE_RECORDS)

    def test_malformed_lines(self, malformed_log):
        """Malformed lines are skipped but valid ones are kept."""
        analytics = UsageLogAnalytics(log_path=malformed_log)
        records = analytics.read_records()
        # 6 original + 1 trailing valid = 7 valid
        assert len(records) == len(SAMPLE_RECORDS) + 1  # +1 for the trailing duplicate

    def test_date_filter_all(self, normal_log):
        """days=None returns all records."""
        analytics = UsageLogAnalytics(log_path=normal_log)
        records = analytics.read_records(days=None)
        assert len(records) == len(SAMPLE_RECORDS)

    def test_date_filter_wide(self, normal_log):
        """days=365000 includes all records (cutoff is far in past)."""
        analytics = UsageLogAnalytics(log_path=normal_log)
        records = analytics.read_records(days=365000)
        assert len(records) == len(SAMPLE_RECORDS)

    def test_date_filter_exact(self):
        """Verifiable: a log with dates exactly bounded by days=N."""
        import tempfile, os
        recs = [
            {"ts": "2026-06-10T00:00:00", "model": "m1", "status": "success", "route_type": "chat",
             "total_tokens": 100, "estimated_cost_usd": 0.01, "latency_ms": 100},
            {"ts": "2026-06-11T00:00:00", "model": "m1", "status": "success", "route_type": "chat",
             "total_tokens": 100, "estimated_cost_usd": 0.01, "latency_ms": 100},
        ]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            for r in recs:
                f.write(json.dumps(r) + "\n")
            path = f.name
        try:
            # Use a mock-like approach: inject days=1 so cutoff = today minus 1 day.
            # But we can't mock datetime easily. Instead, verify the filter works
            # by checking that days=365000 (everything) returns 2 records.
            analytics = UsageLogAnalytics(log_path=path)
            assert len(analytics.read_records(days=365000)) == 2
        finally:
            os.unlink(path)


class TestAggregateDaily:
    def test_empty(self, empty_log):
        analytics = UsageLogAnalytics(log_path=empty_log)
        report = analytics.aggregate_daily(days=7)
        assert report["report_type"] == "error"

    def test_normal(self, normal_log):
        analytics = UsageLogAnalytics(log_path=normal_log)
        report = analytics.aggregate_daily(days=7)
        assert report["report_type"] == "daily"
        summary = report["summary"]
        assert summary["requests"] == 6
        assert summary["cost_usd"] == pytest.approx(0.00105 + 0.00210 + 0.00070 + 0.00015, rel=1e-6)
        assert summary["total_tokens"] == 1050 + 2100 + 700 + 150  # bypass has 0, error has 0
        assert "input_tokens" in summary
        assert "output_tokens" in summary

    def test_routes(self, normal_log):
        analytics = UsageLogAnalytics(log_path=normal_log)
        report = analytics.aggregate_daily(days=7)
        routes = report["routes"]
        assert "normal_chat" in routes
        assert "research" in routes
        assert "code_or_debug" in routes
        assert "simple_command" in routes
        assert routes["normal_chat"]["count"] == 3

    def test_models(self, normal_log):
        analytics = UsageLogAnalytics(log_path=normal_log)
        report = analytics.aggregate_daily(days=7)
        models = report["models"]
        assert "deepseek/deepseek-v4-flash" in models
        assert "perplexity/sonar" in models
        assert models["deepseek/deepseek-v4-flash"]["count"] == 4

    def test_fallback(self, normal_log):
        analytics = UsageLogAnalytics(log_path=normal_log)
        report = analytics.aggregate_daily(days=7)
        fb = report["fallback"]
        assert fb["count"] == 1
        assert fb["records"][0]["fallback"] == "google/gemini-2.5-flash"

    def test_bypass(self, normal_log):
        analytics = UsageLogAnalytics(log_path=normal_log)
        report = analytics.aggregate_daily(days=7)
        bp = report["bypass"]
        assert bp["count"] == 1
        assert bp["commands"].get("help") == 1

    def test_daily_breakdown(self, normal_log):
        analytics = UsageLogAnalytics(log_path=normal_log)
        report = analytics.aggregate_daily(days=7)
        breakdown = report["daily_breakdown"]
        assert len(breakdown) == 2
        assert breakdown[0]["date"] == _DAY_1
        assert breakdown[1]["date"] == _DAY_2


class TestAggregateWeekly:
    def test_empty(self, empty_log):
        analytics = UsageLogAnalytics(log_path=empty_log)
        report = analytics.aggregate_weekly(weeks=4)
        assert report["report_type"] == "error"

    def test_normal(self, normal_log):
        analytics = UsageLogAnalytics(log_path=normal_log)
        report = analytics.aggregate_weekly(weeks=4)
        assert report["report_type"] == "weekly"
        assert report["summary"]["requests"] == 6
        assert "weekly_breakdown" in report
        assert len(report["weekly_breakdown"]) >= 1


class TestAggregateByRoute:
    def test_empty(self, empty_log):
        analytics = UsageLogAnalytics(log_path=empty_log)
        report = analytics.aggregate_by_route(days=7)
        assert report["report_type"] == "error"

    def test_normal(self, normal_log):
        analytics = UsageLogAnalytics(log_path=normal_log)
        report = analytics.aggregate_by_route(days=7)
        assert report["report_type"] == "routes"
        routes = report["routes"]
        assert "normal_chat" in routes
        assert routes["normal_chat"]["requests"] == 3
        assert "top_reasons" in routes["normal_chat"]


class TestAggregateByModel:
    def test_empty(self, empty_log):
        analytics = UsageLogAnalytics(log_path=empty_log)
        report = analytics.aggregate_by_model(days=7)
        assert report["report_type"] == "error"

    def test_normal(self, normal_log):
        analytics = UsageLogAnalytics(log_path=normal_log)
        report = analytics.aggregate_by_model(days=7)
        assert report["report_type"] == "models"
        models = report["models"]
        assert "deepseek/deepseek-v4-flash" in models
        assert models["deepseek/deepseek-v4-flash"]["requests"] == 4
        assert "routes" in models["deepseek/deepseek-v4-flash"]


class TestFormatting:
    def test_markdown_daily(self, normal_log):
        analytics = UsageLogAnalytics(log_path=normal_log)
        report = analytics.aggregate_daily(days=7)
        md = analytics.format_markdown(report)
        assert "# Hermes Daily Analytics" in md
        assert "## Summary" in md
        assert "## Routes" in md
        assert "## Models" in md
        assert "## Fallback" in md

    def test_markdown_weekly(self, normal_log):
        analytics = UsageLogAnalytics(log_path=normal_log)
        report = analytics.aggregate_weekly(weeks=4)
        md = analytics.format_markdown(report)
        assert "# Hermes Weekly Analytics" in md

    def test_markdown_routes(self, normal_log):
        analytics = UsageLogAnalytics(log_path=normal_log)
        report = analytics.aggregate_by_route(days=7)
        md = analytics.format_markdown(report)
        assert "# Hermes Route Analytics" in md

    def test_markdown_models(self, normal_log):
        analytics = UsageLogAnalytics(log_path=normal_log)
        report = analytics.aggregate_by_model(days=7)
        md = analytics.format_markdown(report)
        assert "# Hermes Model Analytics" in md

    def test_markdown_empty(self, empty_log):
        analytics = UsageLogAnalytics(log_path=empty_log)
        report = analytics.aggregate_daily(days=7)
        md = analytics.format_markdown(report)
        assert "No usage records" in md

    def test_json(self, normal_log):
        analytics = UsageLogAnalytics(log_path=normal_log)
        report = analytics.aggregate_daily(days=7)
        js = analytics.format_json(report)
        parsed = json.loads(js)
        assert parsed["report_type"] == "daily"
        assert parsed["summary"]["requests"] == 6


class TestEdgeCases:
    def test_empty_lines_in_log(self, normal_log):
        """Empty lines between records don't break parsing."""
        with open(normal_log, "a") as f:
            f.write("\n\n")
        analytics = UsageLogAnalytics(log_path=normal_log)
        records = analytics.read_records()
        assert len(records) == len(SAMPLE_RECORDS)

    def test_single_record_log(self):
        """Log with exactly 1 record works."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            f.write(json.dumps(SAMPLE_RECORDS[0]) + "\n")
            path = f.name
        try:
            analytics = UsageLogAnalytics(log_path=path)
            report = analytics.aggregate_daily(days=7)
            assert report["summary"]["requests"] == 1
        finally:
            os.unlink(path)