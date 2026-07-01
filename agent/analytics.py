"""
Usage Log Analytics for Hermes Agent.

Aggregates usage.log (JSONL) data into structured reports.
Three modes: standalone (python -m agent.analytics), hermes CLI subcommand,
or programmatic (UsageLogAnalytics class).

Design principles:
- Zero dependency on agent internals (no AIAgent, no SessionDB)
- Pure data processing: read JSONL → aggregate → format
- No API keys, no message content, no raw API responses
- usage.log format is never modified
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_REQUIRED_FIELDS = frozenset(
    {"ts", "model", "provider", "total_tokens", "estimated_cost_usd", "route_type", "status"}
)
_BOOLEAN_FIELDS = frozenset({"fallback_triggered"})
_DEFAULT_DAYS = 1

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _resolve_log_path(path: str | None = None) -> str:
    """Resolve usage.log path from argument, config, or env var."""
    if path:
        return os.path.expanduser(path)
    # Try reading config
    cfg_path = os.path.expanduser("~/.hermes/config.yaml")
    if os.path.isfile(cfg_path):
        try:
            import yaml  # optional dep
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
            p = cfg.get("usage_log_path", "")
            if p:
                return os.path.expanduser(p)
        except Exception:
            pass
    env = os.environ.get("HERMES_USAGE_LOG", "")
    if env:
        return os.path.expanduser(env)
    return os.path.expanduser("~/.hermes/logs/usage.log")


def _parse_date(d: str) -> datetime:
    """Parse YYYY-MM-DD date string to timezone-aware datetime."""
    parts = d.split("-")
    return datetime(int(parts[0]), int(parts[1]), int(parts[2]), tzinfo=timezone.utc)


def _date_key(ts_str: str) -> str:
    """Extract YYYY-MM-DD from ISO timestamp string."""
    return ts_str[:10]  # "2026-06-01T13:22:18" → "2026-06-01"


def _week_key(ts_str: str) -> str:
    """Extract YYYY-Www (ISO week) from timestamp string."""
    try:
        dt = datetime.fromisoformat(ts_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        iso = dt.isocalendar()
        return f"{iso[0]}-W{iso[1]:02d}"
    except (ValueError, TypeError):
        return ts_str[:7]  # fallback: YYYY-MM


def _is_malformed(record: dict) -> bool:
    """Return True if a record is missing required fields or has bad types."""
    if not isinstance(record, dict):
        return True
    if not record.get("ts"):
        return True
    # status is always set even on errors
    if "status" not in record:
        return True
    return False


def _safe_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _safe_int(v: Any, default: int = 0) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def _safe_bool(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        return v.lower() in ("true", "1", "yes")
    if isinstance(v, int):
        return v == 1
    return bool(v)


# ---------------------------------------------------------------------------
# Core analytics
# ---------------------------------------------------------------------------


class UsageLogAnalytics:
    """Aggregate usage.log data into structured reports.

    Args:
        log_path: Path to usage.log JSONL file. If None, auto-resolve.
    """

    def __init__(self, log_path: str | None = None):
        self._log_path = _resolve_log_path(log_path)
        self._records: List[dict] = []
        self._loaded = False
        self._stats: dict = {}  # populate after aggregate

    # ---- Reader ----

    def read_records(self, days: int | None = None) -> List[dict]:
        """Read and filter usage.log records.

        Args:
            days: Number of past days to include. None = all records.

        Returns:
            List of parsed JSON records (filtered by date).
        """
        path = Path(self._log_path)
        if not path.is_file():
            self._records = []
            self._loaded = True
            return []

        records: List[dict] = []
        malformed = 0
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    malformed += 1
                    continue
                if _is_malformed(record):
                    malformed += 1
                    continue
                records.append(record)

        # Date filter
        if days is not None and days > 0:
            cutoff = datetime.now(timezone.utc) - timedelta(days=days)
            cutoff_str = cutoff.strftime("%Y-%m-%d")
            records = [r for r in records if _date_key(r.get("ts", "")) >= cutoff_str]

        self._records = records
        self._loaded = True
        self._stats = {"total_raw": len(records), "malformed": malformed}
        return records

    # ---- Aggregators ----

    def aggregate_daily(self, days: int = 1) -> Dict[str, Any]:
        """Daily aggregation report.

        Args:
            days: Days to look back (default: 1 = today).

        Returns:
            Dict with keys: date, summary, routes, models, fallback, bypass, daily_breakdown
        """
        records = self.read_records(days)
        if not records:
            return self._empty_report("daily")

        # Group by date
        by_date: Dict[str, List[dict]] = defaultdict(list)
        for r in records:
            by_date[_date_key(r.get("ts", ""))].append(r)

        dates = sorted(by_date.keys())
        report: Dict[str, Any] = {
            "report_type": "daily",
            "period": {"days": days, "dates": dates},
        }

        # Summary
        total_req = len(records)
        total_cost = sum(_safe_float(r.get("estimated_cost_usd", 0)) for r in records)
        total_input = sum(_safe_int(r.get("input_tokens", 0)) for r in records)
        total_output = sum(_safe_int(r.get("output_tokens", 0)) for r in records)
        total_tokens = sum(_safe_int(r.get("total_tokens", 0)) for r in records)
        latencies = [_safe_float(r.get("latency_ms", 0)) for r in records if r.get("latency_ms")]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0

        report["summary"] = {
            "requests": total_req,
            "cost_usd": round(total_cost, 6),
            "input_tokens": total_input,
            "output_tokens": total_output,
            "total_tokens": total_tokens,
            "avg_latency_ms": round(avg_latency, 1),
        }

        # Route breakdown
        route_counts: Counter = Counter()
        route_costs: Dict[str, float] = defaultdict(float)
        for r in records:
            rt = r.get("route_type", "unknown")
            route_counts[rt] += 1
            route_costs[rt] += _safe_float(r.get("estimated_cost_usd", 0))
        report["routes"] = {
            r: {"count": c, "cost_usd": round(route_costs[r], 6)}
            for r, c in sorted(route_counts.items(), key=lambda x: -x[1])
        }

        # Model breakdown
        model_counts: Counter = Counter()
        model_costs: Dict[str, float] = defaultdict(float)
        model_tokens: Dict[str, int] = defaultdict(int)
        for r in records:
            m = r.get("model", "unknown")
            model_counts[m] += 1
            model_costs[m] += _safe_float(r.get("estimated_cost_usd", 0))
            model_tokens[m] += _safe_int(r.get("total_tokens", 0))
        report["models"] = {
            m: {"count": c, "cost_usd": round(model_costs[m], 6), "total_tokens": model_tokens[m]}
            for m, c in sorted(model_counts.items(), key=lambda x: -x[1])
        }

        # Fallback events
        fallbacks = [
            r for r in records if _safe_bool(r.get("fallback_triggered"))
        ]
        report["fallback"] = {
            "count": len(fallbacks),
            "records": [
                {
                    "ts": r.get("ts", ""),
                    "primary": r.get("model", ""),
                    "fallback": r.get("fallback_model", ""),
                    "attempt": _safe_int(r.get("attempt_number", 1)),
                }
                for r in fallbacks
            ],
        }

        # Bypass events
        bypasses = [r for r in records if r.get("status") == "bypass"]
        bypass_counts: Counter = Counter()
        for r in bypasses:
            bypass_counts[r.get("bypass_command", "unknown")] += 1
        report["bypass"] = {
            "count": len(bypasses),
            "commands": dict(bypass_counts),
        }

        # Per-day breakdown (for multi-day queries)
        if len(dates) > 1:
            report["daily_breakdown"] = []
            for d in dates:
                day_records = by_date[d]
                day_cost = sum(_safe_float(r.get("estimated_cost_usd", 0)) for r in day_records)
                day_tokens = sum(_safe_int(r.get("total_tokens", 0)) for r in day_records)
                report["daily_breakdown"].append({
                    "date": d,
                    "requests": len(day_records),
                    "cost_usd": round(day_cost, 6),
                    "total_tokens": day_tokens,
                })

        return report

    def aggregate_weekly(self, weeks: int = 4) -> Dict[str, Any]:
        """Weekly aggregation report.

        Args:
            weeks: Number of past weeks to include (default: 4).

        Returns:
            Dict with weekly aggregation data.
        """
        days = weeks * 7
        records = self.read_records(days)
        if not records:
            return self._empty_report("weekly")

        by_week: Dict[str, List[dict]] = defaultdict(list)
        for r in records:
            by_week[_week_key(r.get("ts", ""))].append(r)

        weeks_sorted = sorted(by_week.keys())

        report: Dict[str, Any] = {
            "report_type": "weekly",
            "period": {"weeks": weeks, "days": days, "weeks_list": weeks_sorted},
        }

        # Total summary
        total_req = len(records)
        total_cost = sum(_safe_float(r.get("estimated_cost_usd", 0)) for r in records)
        total_tokens = sum(_safe_int(r.get("total_tokens", 0)) for r in records)
        latencies = [_safe_float(r.get("latency_ms", 0)) for r in records if r.get("latency_ms")]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0

        report["summary"] = {
            "requests": total_req,
            "cost_usd": round(total_cost, 6),
            "total_tokens": total_tokens,
            "avg_latency_ms": round(avg_latency, 1),
        }

        # Weekly breakdown
        report["weekly_breakdown"] = []
        for w in weeks_sorted:
            w_records = by_week[w]
            w_cost = sum(_safe_float(r.get("estimated_cost_usd", 0)) for r in w_records)
            w_tokens = sum(_safe_int(r.get("total_tokens", 0)) for r in w_records)
            report["weekly_breakdown"].append({
                "week": w,
                "requests": len(w_records),
                "cost_usd": round(w_cost, 6),
                "total_tokens": w_tokens,
            })

        # Route breakdown (total)
        route_counts: Counter = Counter()
        for r in records:
            route_counts[r.get("route_type", "unknown")] += 1
        report["routes"] = dict(route_counts.most_common())

        # Model breakdown (total)
        model_counts: Counter = Counter()
        for r in records:
            model_counts[r.get("model", "unknown")] += 1
        report["models"] = dict(model_counts.most_common())

        # Fallback
        fallbacks = [r for r in records if _safe_bool(r.get("fallback_triggered"))]
        report["fallback"] = {"count": len(fallbacks)}

        # Bypass
        bypasses = [r for r in records if r.get("status") == "bypass"]
        report["bypass"] = {"count": len(bypasses)}

        return report

    def aggregate_by_route(self, days: int = 7) -> Dict[str, Any]:
        """Route-type breakdown report.

        Args:
            days: Days to look back (default: 7).

        Returns:
            Dict with per-route stats.
        """
        records = self.read_records(days)
        if not records:
            return self._empty_report("routes")

        by_route: Dict[str, List[dict]] = defaultdict(list)
        for r in records:
            by_route[r.get("route_type", "unknown")].append(r)

        report: Dict[str, Any] = {
            "report_type": "routes",
            "period": {"days": days},
        }

        routes_data = {}
        for route, recs in sorted(by_route.items()):
            cost = sum(_safe_float(r.get("estimated_cost_usd", 0)) for r in recs)
            tokens = sum(_safe_int(r.get("total_tokens", 0)) for r in recs)
            input_t = sum(_safe_int(r.get("input_tokens", 0)) for r in recs)
            output_t = sum(_safe_int(r.get("output_tokens", 0)) for r in recs)
            latencies = [_safe_float(r.get("latency_ms", 0)) for r in recs if r.get("latency_ms")]
            avg_lat = sum(latencies) / len(latencies) if latencies else 0.0
            reasons: Counter = Counter()
            for r in recs:
                cr = r.get("classification_reason", "")
                if cr:
                    reasons[cr] += 1

            routes_data[route] = {
                "requests": len(recs),
                "cost_usd": round(cost, 6),
                "total_tokens": tokens,
                "input_tokens": input_t,
                "output_tokens": output_t,
                "avg_latency_ms": round(avg_lat, 1),
                "top_reasons": dict(reasons.most_common(3)),
            }

        report["routes"] = routes_data
        return report

    def aggregate_by_model(self, days: int = 7) -> Dict[str, Any]:
        """Model breakdown report.

        Args:
            days: Days to look back (default: 7).

        Returns:
            Dict with per-model stats.
        """
        records = self.read_records(days)
        if not records:
            return self._empty_report("models")

        by_model: Dict[str, List[dict]] = defaultdict(list)
        for r in records:
            by_model[r.get("model", "unknown")].append(r)

        report: Dict[str, Any] = {
            "report_type": "models",
            "period": {"days": days},
        }

        models_data = {}
        for model, recs in sorted(by_model.items()):
            cost = sum(_safe_float(r.get("estimated_cost_usd", 0)) for r in recs)
            tokens = sum(_safe_int(r.get("total_tokens", 0)) for r in recs)
            input_t = sum(_safe_int(r.get("input_tokens", 0)) for r in recs)
            output_t = sum(_safe_int(r.get("output_tokens", 0)) for r in recs)
            latencies = [_safe_float(r.get("latency_ms", 0)) for r in recs if r.get("latency_ms")]
            avg_lat = sum(latencies) / len(latencies) if latencies else 0.0
            routes: Counter = Counter()
            for r in recs:
                routes[r.get("route_type", "unknown")] += 1

            models_data[model] = {
                "requests": len(recs),
                "cost_usd": round(cost, 6),
                "total_tokens": tokens,
                "input_tokens": input_t,
                "output_tokens": output_t,
                "avg_latency_ms": round(avg_lat, 1),
                "routes": dict(routes.most_common()),
            }

        report["models"] = models_data
        return report

    # ---- Formatters ----

    def format_markdown(self, report: Dict[str, Any]) -> str:
        """Format a report as Markdown string."""
        rt = report.get("report_type", "unknown")
        lines: List[str] = []

        if rt == "daily":
            lines.append(f"# Hermes Daily Analytics\n")
            dates = report.get("period", {}).get("dates", [])
            if dates:
                lines.append(f"**Period:** {dates[0]}" + (f" — {dates[-1]}" if len(dates) > 1 else "") + "\n")

            summary = report.get("summary", {})
            lines.append("## Summary\n")
            lines.append(f"| Metric | Value |")
            lines.append(f"|---|---:|")
            lines.append(f"| Requests | {summary.get('requests', 0):,} |")
            lines.append(f"| Cost | ${summary.get('cost_usd', 0):.6f} |")
            lines.append(f"| Input tokens | {summary.get('input_tokens', 0):,} |")
            lines.append(f"| Output tokens | {summary.get('output_tokens', 0):,} |")
            lines.append(f"| Total tokens | {summary.get('total_tokens', 0):,} |")
            lines.append(f"| Avg latency | {summary.get('avg_latency_ms', 0):.0f}ms |")
            lines.append("")

            # Routes
            routes = report.get("routes", {})
            lines.append("## Routes\n")
            lines.append(f"| Route | Count | Cost |")
            lines.append(f"|---|---|---:|")
            for route, data in routes.items():
                lines.append(f"| {route} | {data['count']} | ${data['cost_usd']:.6f} |")
            lines.append("")

            # Models
            models = report.get("models", {})
            lines.append("## Models\n")
            lines.append(f"| Model | Count | Cost | Tokens |")
            lines.append(f"|---|---|---:|---:|")
            for model, data in models.items():
                # Shorten long model names
                short_name = model.split("/")[-1] if "/" in model else model
                lines.append(f"| {short_name} | {data['count']} | ${data['cost_usd']:.6f} | {data['total_tokens']:,} |")
            lines.append("")

            # Daily breakdown (multi-day)
            daily_breakdown = report.get("daily_breakdown", [])
            if daily_breakdown:
                lines.append("## Daily Breakdown\n")
                lines.append(f"| Date | Requests | Cost | Tokens |")
                lines.append(f"|---|---:|---:|---:|")
                for d in daily_breakdown:
                    lines.append(f"| {d['date']} | {d['requests']} | ${d['cost_usd']:.6f} | {d['total_tokens']:,} |")
                lines.append("")

            # Fallback
            fb = report.get("fallback", {})
            lines.append(f"## Fallback\n")
            lines.append(f"- Occurrences: **{fb.get('count', 0)}**")
            for fb_rec in fb.get("records", []):
                fb_model = fb_rec.get("fallback_model", "") or "—"
                lines.append(f"  - {fb_rec.get('ts', '')}: {fb_rec.get('primary', '')} → {fb_model}")
            lines.append("")

            # Bypass
            bp = report.get("bypass", {})
            lines.append(f"## Command Bypass\n")
            lines.append(f"- Total bypasses: **{bp.get('count', 0)}**")
            for cmd, cnt in bp.get("commands", {}).items():
                lines.append(f"  - `/{cmd}`: {cnt} times")
            lines.append("")

        elif rt == "weekly":
            lines.append(f"# Hermes Weekly Analytics\n")
            weeks_list = report.get("period", {}).get("weeks_list", [])
            if weeks_list:
                lines.append(f"**Period:** {weeks_list[0]} — {weeks_list[-1]}\n")

            summary = report.get("summary", {})
            lines.append("## Summary\n")
            lines.append(f"| Metric | Value |")
            lines.append(f"|---|---:|")
            lines.append(f"| Requests | {summary.get('requests', 0):,} |")
            lines.append(f"| Cost | ${summary.get('cost_usd', 0):.6f} |")
            lines.append(f"| Total tokens | {summary.get('total_tokens', 0):,} |")
            lines.append(f"| Avg latency | {summary.get('avg_latency_ms', 0):.0f}ms |")
            lines.append("")

            # Weekly breakdown
            wb = report.get("weekly_breakdown", [])
            lines.append("## Weekly Breakdown\n")
            lines.append(f"| Week | Requests | Cost | Tokens |")
            lines.append(f"|---|---:|---:|---:|")
            for w in wb:
                lines.append(f"| {w['week']} | {w['requests']} | ${w['cost_usd']:.6f} | {w['total_tokens']:,} |")
            lines.append("")

            lines.append(f"## Routes\n")
            for route, cnt in report.get("routes", {}).items():
                lines.append(f"- **{route}**: {cnt}")
            lines.append("")

            lines.append(f"## Models\n")
            for model, cnt in report.get("models", {}).items():
                short_name = model.split("/")[-1] if "/" in model else model
                lines.append(f"- **{short_name}**: {cnt}")
            lines.append("")

            fb = report.get("fallback", {})
            lines.append(f"## Fallback\n")
            lines.append(f"- Occurrences: **{fb.get('count', 0)}**\n")

            bp = report.get("bypass", {})
            lines.append(f"## Command Bypass\n")
            lines.append(f"- Total bypasses: **{bp.get('count', 0)}**\n")

        elif rt == "routes":
            lines.append(f"# Hermes Route Analytics\n")
            lines.append(f"**Period:** last {report.get('period', {}).get('days', 7)} days\n")
            lines.append(f"| Route | Requests | Cost | Tokens | Input | Output | Avg Latency | Top Reason |")
            lines.append(f"|---|---:|---:|---:|---:|---:|---:|:---|")
            for route, data in report.get("routes", {}).items():
                top_reason = ""
                if data.get("top_reasons"):
                    top_reason = next(iter(data["top_reasons"]))
                lines.append(
                    f"| {route} | {data['requests']} | ${data['cost_usd']:.6f} "
                    f"| {data['total_tokens']:,} | {data['input_tokens']:,} "
                    f"| {data['output_tokens']:,} | {data['avg_latency_ms']:.0f}ms | {top_reason} |"
                )
            lines.append("")

        elif rt == "models":
            lines.append(f"# Hermes Model Analytics\n")
            lines.append(f"**Period:** last {report.get('period', {}).get('days', 7)} days\n")
            lines.append(f"| Model | Requests | Cost | Tokens | Input | Output | Avg Latency |")
            lines.append(f"|---|---:|---:|---:|---:|---:|---:|")
            for model, data in report.get("models", {}).items():
                short_name = model.split("/")[-1] if "/" in model else model
                lines.append(
                    f"| {short_name} | {data['requests']} | ${data['cost_usd']:.6f} "
                    f"| {data['total_tokens']:,} | {data['input_tokens']:,} "
                    f"| {data['output_tokens']:,} | {data['avg_latency_ms']:.0f}ms |"
                )
            lines.append("")

        elif rt == "error":
            lines.append(f"# Hermes Analytics — {report.get('error', 'No data')}\n")
            lines.append(f"No usage records found for the requested period.\n")

        else:
            lines.append(f"# Hermes Analytics — Unknown report type\n")

        return "\n".join(lines)

    def format_json(self, report: Dict[str, Any]) -> str:
        """Format a report as pretty-printed JSON string."""
        return json.dumps(report, ensure_ascii=False, indent=2, default=str)

    # ---- Internal ----

    def _empty_report(self, report_type: str) -> Dict[str, Any]:
        return {
            "report_type": "error",
            "error": f"No usage records found for {report_type} query",
        }


# ---------------------------------------------------------------------------
# CLI entry point (standalone: python -m agent.analytics)
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    """Entry point for ``python -m agent.analytics``."""
    parser = argparse.ArgumentParser(
        prog="python -m agent.analytics",
        description="Hermes Usage Log Analytics — aggregate usage.log data",
    )
    parser.add_argument(
        "subcommand",
        choices=["daily", "weekly", "routes", "models"],
        help="Report type",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=None,
        help="Days to look back (default: daily=1, weekly=28, routes=7, models=7)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON instead of Markdown",
    )
    parser.add_argument(
        "--log-path",
        default=None,
        help="Path to usage.log (default: auto-detect)",
    )

    args = parser.parse_args(argv)

    analytics = UsageLogAnalytics(log_path=args.log_path)

    # Default days per subcommand
    default_days = {"daily": 1, "weekly": 28, "routes": 7, "models": 7}
    days = args.days if args.days is not None else default_days.get(args.subcommand, 7)

    if args.subcommand == "daily":
        report = analytics.aggregate_daily(days=days)
    elif args.subcommand == "weekly":
        report = analytics.aggregate_weekly(weeks=max(1, days // 7))
    elif args.subcommand == "routes":
        report = analytics.aggregate_by_route(days=days)
    elif args.subcommand == "models":
        report = analytics.aggregate_by_model(days=days)

    if args.json:
        print(analytics.format_json(report))
    else:
        print(analytics.format_markdown(report))

    return 0


if __name__ == "__main__":
    sys.exit(main())