---
name: super-execute
description: Execute an implementation plan step by step. Chain-fired from super-brainstorm at the execute-implementation-plan module. Selects a backend (subagent-driven / inline-batch / parallel-dispatch) and applies policies (TDD enforcement, code-review checkpoints, design fidelity) via the hook-point composition system.
---

# super-execute

The plan-execution skill. Takes a plan file produced by `super-brainstorm` and turns it into committed code, one step at a time. The plan is the source of truth; this skill is the executor.

## When to use

- Chain-fired automatically from `super-brainstorm` at its terminal `execute-implementation-plan` module.
- Invoked directly when the user already has a plan file from a previous brainstorm session.

## NOT user-invokable

There is no `/super-execute` slash command. The skill chain-fires only. This is deliberate: executing a plan without going through brainstorm's design + spec + approval gates is exactly the failure mode the gates exist to prevent.

## The architecture: backends + policies via hooks

`super-execute` is hook-point composition. Each step in the plan goes through a fixed lifecycle:

```
pre-step-check  ->  per-step-execute  ->  post-step-check  ->  post-batch-complete
```

- **Backends** PROVIDE the `per-step-execute` hook. Exactly one backend is chosen per invocation.
- **Policies** CONSUME the other hooks (`pre-step-check`, `post-step-check`, `post-batch-complete`) to enforce discipline.

This lets a user enable TDD-enforcement without caring which backend executes the step, and vice versa.

## Backends (one is chosen)

1. `backend-subagent-driven` - each step dispatched to a fresh subagent with a narrow task description.
2. `backend-inline-batch` - the controller LLM executes steps in batches itself; fastest but largest context.
3. `backend-parallel-dispatch` - independent steps dispatched in parallel to subagents.

Default backend: `backend-inline-batch`. Configurable via `super_execute.backend` in `.super/config.json`.

## Policies (zero or more enabled)

1. `policy-tdd-enforcement` - rejects step completion unless tests were written FIRST and a RED -> GREEN transition is recorded.
2. `policy-code-review-checkpoints` - fires `super-code-review` at configured batch boundaries (e.g., every 5 steps or before each commit).
3. `policy-design-fidelity` - verifies each step's output against the design doc; flags drift.

All policies enabled by default.

## Plan file shape

```yaml
plan_id: "add-user-auth-2026-05-20"
design_ref: "docs/design/user-auth.md"
spec_ref: "docs/specs/user-auth.md"
steps:
  - id: 1
    description: "Add User model with email + password_hash"
    files: ["src/models/user.py"]
    tests: ["tests/test_user_model.py"]
  - id: 2
    description: "..."
    ...
```

## Verify after running

- All plan steps marked complete (or explicit "skipped: reason" for any).
- Test suite passes (verification-before-completion is the terminal gate).
- Code-review verdict (from chain-fired `super-code-review` at the end) is READY-TO-MERGE.
- No design-fidelity flags from `policy-design-fidelity`.
