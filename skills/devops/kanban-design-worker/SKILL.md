---
name: kanban-design-worker
description: Use when a Kanban task is about design, planning, decomposition, or risk framing and the worker should produce direction without directly changing code or operations.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
environments: [kanban]
metadata:
  hermes:
    tags: [kanban, worker, design, planning]
    related_skills: [kanban-worker, kanban-orchestrator]
---

# Kanban Design Worker

## Overview

This worker is for thinking work: clarifying scope, organizing direction, identifying risks, and turning a vague request into an implementable plan.

`KANBAN_GUIDANCE` already covers the shared worker lifecycle. This skill only adds role boundaries for design-oriented cards.

## When to Use

Use when the task is mainly about:

- design
- policy or direction整理
- implementation planning
- risk breakdown
- task decomposition

Do not use when the primary deliverable is code, deployment, or an external action.

## Role Boundaries

### Primary responsibilities

- define the current goal and constraints
- propose a practical implementation plan
- split work into smaller tasks when useful
- identify risks, assumptions, and decision points
- leave a handoff another worker can execute

### Prohibited actions

- direct file edits
- Git operations
- external sending / publishing
- cron changes

## Handoff Shape

A good completion/block summary usually includes:

- current objective
- recommended next steps
- key risks or unknowns
- any decisions the code worker or human must make

## Common Pitfalls

1. Turning a design card into an implementation card.
2. Repeating full constitutions instead of giving a compact plan.
3. Leaving abstract advice with no next concrete action.

## Verification Checklist

- [ ] I stayed in planning/design mode
- [ ] I did not edit files or perform Git/cron actions
- [ ] My output gives the next worker a concrete path forward
