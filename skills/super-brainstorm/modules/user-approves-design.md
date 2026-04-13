---
name: user-approves-design
description: Second hard approval gate. Wait for the user's written approval of the COMMITTED design doc before writing the spec. The committed doc is the artifact under review - not the verbal sketch, not the audit-evaluation output - the actual file the user can read end to end.
---

# user-approves-design

## What it does

The second hard gate. After `write-design-doc` has committed the doc and `audit-evaluation` + `implementation-plan-review` have surfaced any concerns, ask the user:

> "Please read `docs/design/<topic>.md` end to end. Reply 'approved' to proceed to spec writing, or describe what needs to change."

Then WAIT. Do not proceed to `write-spec-doc` until the user replies 'approved' (or equivalent affirmative).

## Why written approval of the committed doc

The verbal Gate #1 approved the sketch. This gate approves the canonical artifact. If they diverged - if the doc says something the verbal didn't, or omits something the verbal had - this is the gate where the divergence must be reconciled.

## Hard rule

Do NOT silently proceed if the user goes quiet. Re-ping after reasonable timeout: "Still waiting on design approval - any concerns?" The hard gate is "no spec without explicit approval", not "no spec without active disapproval".

## Idempotency

Approval is a one-time signal. If the user says "let's revise", go back to write-design-doc and re-iterate before re-asking for approval.
