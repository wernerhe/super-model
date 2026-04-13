---
name: execute-implementation-plan
description: Main orchestration loop. Iterates the plan's steps, fires the four lifecycle hooks per step (pre-step-check, per-step-execute, post-step-check, post-batch-complete), and produces a per-step completion record. The terminal module of any super-execute invocation.
---

# execute-implementation-plan

## What it does

Drives the per-step lifecycle for the entire plan:

```
for step in plan.steps:
    fire pre-step-check   -> all enabled policies inspect; any can veto.
    if vetoed:
        report and stop.
    fire per-step-execute -> the chosen backend produces commits + tests.
    fire post-step-check  -> policies verify the step output.
    if at batch boundary:
        fire post-batch-complete -> e.g., code-review checkpoint.
    record step status.
```

## Hook-point semantics

- `pre-step-check` (multi-consumer): every enabled policy can veto the step before execution.
- `per-step-execute` (single-provider): exactly one backend handles the actual code-producing work.
- `post-step-check` (multi-consumer): policies verify; failures may roll back the step.
- `post-batch-complete` (multi-consumer): periodic checkpoints (code review, design fidelity sweep).

## Output

A run record:

```json
{
  "plan_id": "add-user-auth-2026-05-20",
  "steps_completed": 7,
  "steps_total": 9,
  "steps_skipped": [{"id": 8, "reason": "user-requested skip"}],
  "code_review_verdict": "READY-TO-MERGE",
  "policy_findings": []
}
```

## Idempotency

Per-step execution is destructive (commits code). Re-running on a partially-completed plan picks up at the next pending step; already-completed steps are skipped (their commits already exist).
