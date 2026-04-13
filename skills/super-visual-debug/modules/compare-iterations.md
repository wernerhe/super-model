---
name: compare-iterations
description: Compare the just-captured iteration against the previous one (or initial-capture) per angle. Surface remaining diffs to the user; ask whether to continue or stop.
---

# compare-iterations

## What it does

Diffs the most recent iteration's captures against the previous iteration's per angle:

- If an image-diff tool is available, generate a side-by-side diff or a highlighted-pixels overlay.
- Otherwise present the user with the two captures and a brief textual description of what was changed.

Summarizes:

- Which angles improved (closer to user's stated intent).
- Which angles regressed (new differences introduced).
- Which angles are unchanged.

## Continue / stop decision

After every comparison:

1. If the user explicitly approves the current state -> stop, exit the loop, write to capability-memory, done.
2. If there are unresolved differences -> go to fix-proposal for the next iteration.
3. If iteration count >= 5 without convergence -> stop and ask the user whether to re-scope.

## Output

A continue-or-stop signal to the loop driver.

## Idempotency

Read-only.
