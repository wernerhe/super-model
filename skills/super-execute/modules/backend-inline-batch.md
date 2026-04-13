---
name: backend-inline-batch
description: Backend where the controller LLM executes plan steps directly without dispatching subagents. Fastest, but uses the most controller context. Default backend. Provides the per-step-execute hook.
hooks_provided:
  - per-step-execute
---

# backend-inline-batch

## What it does

The controller LLM executes each step in place:

- Read the step's `description`, `files`, `tests`.
- Make the necessary edits.
- Run the tests.
- Commit.

No subagent dispatch overhead.

## When to prefer

- Small plans (under ~10 steps) where context budget is not an issue.
- Plans where step-to-step state matters (each step builds on the previous in non-obvious ways).
- Iterative work where the controller wants to retain memory of the last step's decisions.

## Trade-offs vs subagent-driven

- Faster (no dispatch overhead).
- Uses more controller context (every step's full file content stays loaded).
- Less isolation (a controller mistake on step 3 can subtly poison the reasoning on step 4).

## Hook contract

Provides `per-step-execute`. Consumes nothing.

## Idempotency

Each step's commit is atomic. Re-running on a partial-completion picks up at the next pending step.
