---
name: policy-tdd-enforcement
description: Enforce RED-GREEN-REFACTOR per step. Vetoes a step at pre-step-check if no test file is declared, and verifies the RED-to-GREEN transition at post-step-check.
hooks_consumed:
  pre-step-check: tdd_pre_check
  post-step-check: tdd_post_check
risk_assessment: required
---

# policy-tdd-enforcement

## What it does

### pre-step-check (tdd_pre_check)

- If the step has `files` but no `tests`, veto: "TDD policy requires a `tests` list per step. Update the plan."
- If the step's declared test files do not exist yet, OK (about to be created in RED phase).

### post-step-check (tdd_post_check)

- Verify the declared test files now exist.
- Verify those tests have run at least once before the step's main code change (RED phase).
- Verify those tests now pass (GREEN phase).
- If any check fails, flag the step as TDD-incomplete.

## Why this is a policy not a backend

The TDD discipline is orthogonal to which backend executes the step. A subagent-driven step and an inline-batch step both need the same TDD enforcement. Making it a hook-consumer means one implementation works across all backends.

## Risk assessment

`required` - every step under this policy must produce a risk metadata record describing whether the test coverage is sufficient and what's NOT covered.

## Idempotency

Read-only verification. The verification itself is idempotent.
