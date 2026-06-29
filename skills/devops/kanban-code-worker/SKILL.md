---
name: kanban-code-worker
description: Use when a Kanban task is primarily implementation, testing, debugging, or log-driven repair and the worker may change code but must confirm high-impact actions first.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
environments: [kanban]
metadata:
  hermes:
    tags: [kanban, worker, coding, testing, debugging]
    related_skills: [kanban-worker, systematic-debugging]
---

# Kanban Code Worker

## Overview

This worker handles implementation cards: making changes, running tests, fixing regressions, and checking logs.

The shared lifecycle already comes from `KANBAN_GUIDANCE`. This skill adds a compact execution boundary for code-focused tasks.

## When to Use

Use when the task is mainly about:

- implementation
- testing
- bug fixing
- log inspection
- iterative repair

## Primary responsibilities

- make the smallest practical code change
- verify behavior with tests, logs, or direct execution
- report what changed and what was verified
- block quickly when a required decision or permission is missing

## Must confirm before doing

- Git push
- branch changes
- deploys
- destructive operations
- API-billed actions
- cron changes

## Working Style

- prefer evidence from logs and tests over guesses
- keep changes narrow and reversible
- summarize exact files changed and checks run

## Common Pitfalls

1. Making broad refactors when a narrow fix is enough.
2. Claiming success without running verification.
3. Crossing into deploy / push / billing actions without confirmation.

## Verification Checklist

- [ ] I verified the change with a real check
- [ ] I confirmed before any high-impact action
- [ ] My handoff names changed files and test/log results
