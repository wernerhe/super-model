---
name: backend-subagent-driven
description: Backend that dispatches each plan step to a fresh subagent with a narrow task description. Best for steps that need focus or have a high blast radius. Provides the per-step-execute hook.
dispatch: subagent
agent: code-implementer
hooks_provided:
  - per-step-execute
---

# backend-subagent-driven

## What it does

For each step, dispatch a subagent with:

- The step's `description`.
- The step's `files` (the subagent edits only these).
- The step's `tests` (the subagent ensures these pass).
- A reference to the design doc and spec.
- The using-super-model SUBAGENT-STOP exemption is in effect: the subagent focuses on the dispatched task.

The subagent returns:

- The diff applied.
- The test results (passed / failed).
- A brief summary of what was done.

## When to prefer

- Step has a high blast radius (touching infrastructure, security boundaries).
- Step is large enough that the controller LLM's context would balloon.
- Step is independent enough that fresh context helps (no cross-step state in the controller).

## Hook contract

Provides `per-step-execute`. Consumes nothing.

## Idempotency

Per-step subagent invocation. The subagent may decline to re-execute a step whose changes are already present.
