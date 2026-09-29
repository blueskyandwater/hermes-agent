"""``hermes insights`` subcommand parser."""

from __future__ import annotations

import sys
from typing import Callable


def build_insights_parser(subparsers, *, cmd_insights: Callable) -> None:
    """Attach the ``insights`` subcommand to ``subparsers``."""
    insights_parser = subparsers.add_parser(
        "insights", help="Show usage insights and analytics",
        description="Analyze session history to show token usage, costs, tool patterns, and activity trends",
    )
    insights_parser.add_argument(
        "--days", type=int, default=30, help="Number of days to analyze (default: 30)")
    insights_parser.add_argument(
        "--source", help="Filter by platform (cli, telegram, discord, etc.)")
    insights_parser.set_defaults(func=cmd_insights)


def build_analytics_parser(subparsers) -> None:
    """Attach the fork usage-log analytics surface to the refactored CLI."""
    def _add_common_analytics_flags(subparser):
        """Add --json flag shared across analytics subcommands."""
        subparser.add_argument(
            "--json",
            action="store_true",
            help="Output JSON instead of Markdown",
        )

    analytics_parser = subparsers.add_parser(
        "analytics",
        help="Aggregate usage.log data",
        description="Aggregate and report usage.log data — cost, tokens, routes, models.",
    )
    analytics_subparsers = analytics_parser.add_subparsers(dest="analytics_action", required=True)

    # analytics daily
    daily_parser = analytics_subparsers.add_parser(
        "daily",
        help="Daily aggregation",
        description="Show daily usage summary: requests, cost, tokens, routes, models.",
    )
    daily_parser.add_argument("--days", type=int, default=1, help="Days to look back (default: 1)")
    _add_common_analytics_flags(daily_parser)

    # analytics weekly
    weekly_parser = analytics_subparsers.add_parser(
        "weekly",
        help="Weekly aggregation",
        description="Show weekly usage summary aggregated by ISO week.",
    )
    weekly_parser.add_argument("--weeks", type=int, default=4, help="Weeks to look back (default: 4)")
    _add_common_analytics_flags(weekly_parser)

    # analytics routes
    routes_parser = analytics_subparsers.add_parser(
        "routes",
        help="Route-type breakdown",
        description="Show per-route stats: requests, cost, tokens, avg latency, top classification reasons.",
    )
    routes_parser.add_argument("--days", type=int, default=7, help="Days to look back (default: 7)")
    _add_common_analytics_flags(routes_parser)

    # analytics models
    models_parser = analytics_subparsers.add_parser(
        "models",
        help="Model breakdown",
        description="Show per-model stats: requests, cost, tokens, avg latency, route distribution.",
    )
    models_parser.add_argument("--days", type=int, default=7, help="Days to look back (default: 7)")
    _add_common_analytics_flags(models_parser)

    def cmd_analytics(args):
        try:
            from agent.analytics import UsageLogAnalytics

            analytics = UsageLogAnalytics()
            use_json = getattr(args, "json", False)

            if args.analytics_action == "daily":
                report = analytics.aggregate_daily(days=args.days)
            elif args.analytics_action == "weekly":
                report = analytics.aggregate_weekly(weeks=args.weeks)
            elif args.analytics_action == "routes":
                report = analytics.aggregate_by_route(days=args.days)
            elif args.analytics_action == "models":
                report = analytics.aggregate_by_model(days=args.days)
            else:
                print(f"Unknown analytics subcommand: {args.analytics_action}")
                return

            if use_json:
                print(analytics.format_json(report))
            else:
                print(analytics.format_markdown(report))
        except Exception as e:
            print(f"Error generating analytics: {e}", file=sys.stderr)

    analytics_parser.set_defaults(func=cmd_analytics)
