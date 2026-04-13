---
name: apply-and-recapture
description: Apply the proposed fix to code, then recapture the same angles as initial-capture. The next iteration's "before" is this iteration's "after".
---

# apply-and-recapture

## What it does

1. Apply the diff from `fix-proposal` to the file at the indicated line range. If hot-reload is available, the running app re-renders; otherwise rebuild / re-run as needed.
2. Wait briefly for the new visual state to settle.
3. Re-capture using the SAME angles as `initial-capture` (or the previous iteration's capture). Stored under `iter-<n>/`.

## Why same angles

Comparing different angles between iterations is meaningless. The compare-iterations module needs angle-to-angle correspondence.

## Failure handling

If the apply step fails (compile error, type error, syntax error from the diff), do not proceed to recapture. Report the failure and let the user decide whether to:

- Revert and propose differently.
- Hand-edit to make the diff compile.
- Abort the loop.

## Idempotency

Single-iteration destructive edit. The next iteration restarts the loop with the new state as "before".
