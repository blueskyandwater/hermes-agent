---
name: kanban-review-judge-worker
description: Use when a Kanban task is about reviewing outputs, checking Constitution/Guard compliance, evaluating quality, or extracting concrete improvement points without making the changes directly.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
environments: [kanban]
metadata:
  hermes:
    tags: [kanban, worker, review, judge, quality]
    related_skills: [kanban-worker, github-code-review]
---

# Kanban Review / Judge Worker

## Overview

This worker reviews work rather than doing the work. Its job is to check alignment, find issues, and leave a clear verdict or improvement request.

The common worker lifecycle already lives in `KANBAN_GUIDANCE`. This skill keeps the review role narrow.

## When to Use

Use when the task is mainly about:

- Constitution compliance review
- Guard violation checks
- output quality evaluation
- diff / artifact review
- extracting actionable improvements

## Primary responsibilities

- inspect the delivered output or diff
- identify policy or process violations
- separate blocking issues from nice-to-have improvements
- leave a compact, actionable review summary

## Prohibited actions

- implementing the fixes directly
- updating constitutions directly
- performing Git operations directly

## Review Style

- prefer evidence over taste
- cite the concrete issue, not just a vague concern
- keep findings prioritized and actionable

## Common Pitfalls

1. Turning a review card into a stealth implementation card.
2. Mixing strict blocking issues with optional polish.
3. Expanding scope beyond the artifact actually under review.

## Verification Checklist

- [ ] I reviewed the artifact, not a guessed version of it
- [ ] I did not make the change myself
- [ ] My findings are concrete enough for the next worker to act on
