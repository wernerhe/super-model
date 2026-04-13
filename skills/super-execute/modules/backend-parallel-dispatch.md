---
name: backend-parallel-dispatch
description: Backend that dispatches independent plan steps to subagents in parallel. Significantly faster for plans with parallelizable steps; useful only when steps have explicit `dependencies` declared so the scheduler can build a DAG.
dispatch: subagent
agent: code-implementer
hooks_provided:
  - per-step-execute
---

# backend-parallel-dispatch

## What it does

Reads the plan's step `dependencies` field (each step lists IDs of steps that must complete first). Builds a DAG; dispatches all currently-runnable steps to subagents in parallel.

When a step completes, any of its dependents that now have all upstream steps complete becomes runnable. Loop until all steps complete or any step fails.

## When to prefer

- Plans where many steps are mutually independent (e.g., "add 5 unrelated endpoints").
- Aggressive time-to-completion targets.
- Steps that touch disjoint file sets (avoiding merge conflicts in concurrent commits).

## When NOT to use

- Plans with implicit ordering not captured in `dependencies` (parallel execution will get the wrong sequence).
- Steps that share state in subtle ways.
- Plans for security-sensitive code (parallel commits are harder to review chronologically).

## Hook contract

Provides `per-step-execute`. Consumes nothing.

## Conflict handling

Two subagents producing diffs that conflict on the same file at the same lines triggers a stop: the controller serializes by re-dispatching the later step after the earlier one commits.

## Idempotency

Per-step subagent invocation. Same idempotency semantics as backend-subagent-driven.
