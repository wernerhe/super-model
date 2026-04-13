---
name: execute-implementation-plan
description: Terminal module. Chain-fires super-execute with the plan file produced by write-implementation-plan. Hands off to the executor; super-brainstorm completes here.
---

# execute-implementation-plan

## What it does

The last module in `super-brainstorm`. Chain-fires `super-execute` with:

- The plan file path.
- The design and spec refs (already in the plan, but passed redundantly for clarity).
- Any user-specified resume offset (for picking up an interrupted execution).

## How chain-fire works

`super-execute` is NOT user-invokable (no `/super-execute` slash command). It is invoked only as a chain target from this module. The chain means:

1. `super-brainstorm` completes its 13 prior modules.
2. The TodoWrite list updates: "Plan" todo -> done; "Execute" todo -> in_progress.
3. `super-execute` skill is loaded and run with the plan.
4. When `super-execute` completes, the "Execute" todo -> done; `super-brainstorm` returns.

## Why chain-fire instead of slash command

Forcing the executor to come from brainstorm means there's always an approved design + spec + plan before any execution. The 3 hard gates cannot be bypassed by jumping straight to execute.

## Idempotency

The chain-fire is a one-shot delegation. If `super-execute` was already partially run, it picks up at the next pending step (per its own `execute-implementation-plan` orchestration module).
