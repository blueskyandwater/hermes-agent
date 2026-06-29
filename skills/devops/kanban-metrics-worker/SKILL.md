---
name: kanban-metrics-worker
description: Use when a Kanban task is about recording operational quality metrics such as question counts, memory actions, guard decisions, violations, scores, or trends without inventing or auto-applying conclusions.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
environments: [kanban]
metadata:
  hermes:
    tags: [kanban, worker, metrics, reporting]
    related_skills: [kanban-worker]
---

# Kanban Metrics Worker

## Overview

This worker records and organizes measurable results. It should capture counts and trend data cleanly without drifting into judgment or automation.

`KANBAN_GUIDANCE` already covers the shared worker lifecycle. This skill only defines the metrics role.

## When to Use

Use when the task is mainly about:

- Question Count
- Memory Save / Update / Ignore counts
- Guard Allow / Confirm / Deny counts
- Constitution Violation counts
- Overall Score recording
- trend aggregation

## Primary responsibilities

- record only measurable values
- preserve the source and time window when relevant
- distinguish zero from unknown
- summarize trends without inventing missing numbers

## Prohibited actions

- scoring or judging on its own
- auto-applying improvement actions
- recording guessed values

## Data Hygiene

- use `N/A` or equivalent when a value is unavailable
- keep the metric name stable across reports
- call out missing inputs explicitly

## Common Pitfalls

1. Turning trend reporting into subjective evaluation.
2. Filling gaps with estimated numbers.
3. Mixing incompatible time windows in one summary.

## Verification Checklist

- [ ] Every recorded value is sourced or explicitly unknown
- [ ] I did not invent scores or apply changes
- [ ] Trend summaries stay within the available data
