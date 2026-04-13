---
name: policy-code-review-checkpoints
description: At configured batch boundaries (every N steps, or before each plan commit), fire super-code-review and gate further progress on a READY-TO-MERGE verdict. Cache markers from earlier reviews are honored.
hooks_consumed:
  post-batch-complete: code_review_checkpoint
---

# policy-code-review-checkpoints

## What it does

Fires `super-code-review` at configured batch boundaries:

- Default: every 5 completed steps.
- Configurable via `super_execute.policies.policy-code-review-checkpoints.batch_size`.
- Always fires at the end of the plan.

Reads the HMAC-signed code-review marker (via `super_lib.cache.read_marker`) for the current HEAD SHA. If a fresh READY-TO-MERGE marker exists, skip the actual review. Otherwise run it.

## Continue or stop

- READY-TO-MERGE -> continue to the next batch.
- NEEDS-FIXES -> stop. Present findings to the user. User addresses, then re-runs `super-execute --resume` (which picks up at the next pending step after the fixes commit).

## Why batch boundaries

A per-step review would be too noisy (most steps' diffs aren't ready to be reviewed individually). End-of-plan review only would let problems accumulate across many steps before surfacing. Periodic checkpoints catch drift at survivable granularity.

## Idempotency

Cache-driven; same HEAD SHA produces same review marker. Conservative degradation on HMAC mismatch.
