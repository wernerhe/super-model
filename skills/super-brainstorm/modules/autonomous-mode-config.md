---
name: autonomous-mode-config
description: Conditional module - only runs if approach-profile suggests long-running unattended work. Configures super-execute's policies for autonomous execution (e.g., higher TDD enforcement, more frequent code-review checkpoints, design-fidelity always on).
enabled_by_default: false
---

# autonomous-mode-config

## What it does

Conditional. Runs only when the user explicitly wants the implementation to run unattended (e.g., overnight, in CI, while the user is off-keyboard).

Configures `super-execute` policies for the unattended case:

- `policy-tdd-enforcement`: strict (no exceptions).
- `policy-code-review-checkpoints`: smaller batch size (e.g., every 3 steps instead of 5).
- `policy-design-fidelity`: any drift = stop-and-page-user.
- Backend choice: typically `backend-subagent-driven` for tighter context isolation.

Records these choices in the plan file's `policies` section so `super-execute` reads them at chain-fire time.

## Why conditional

Most brainstorm sessions are attended - the user is in the chat watching. Default-disabled keeps the question out of the modal flow.

## Idempotency

Configuration writes only; no destructive changes.
