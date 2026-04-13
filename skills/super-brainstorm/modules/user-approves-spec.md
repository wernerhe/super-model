---
name: user-approves-spec
description: Third hard approval gate. Wait for the user's written approval of the COMMITTED spec doc before writing the implementation plan. Same gate semantics as the design-approval gate but at the spec level.
---

# user-approves-spec

## What it does

The third hard gate. After `write-spec-doc` and `spec-review` have produced the committed spec, ask:

> "Please read `docs/specs/<topic>.md`. Reply 'approved' to proceed to plan writing, or describe what needs to change."

WAIT for explicit approval. Do not proceed to `write-implementation-plan`.

## Why three gates and not two

Two gates (design + plan) means the spec slides past unreviewed - the implementation has to derive specs from the design implicitly, which is where most ambiguity-driven bugs originate. Three gates makes the spec a first-class artifact with its own approval surface.

NOT 4 gates either. Adding a fourth (approve-the-plan) makes the flow heavy enough that users start skipping or batching gates - which defeats the purpose.

Three is the calibrated number after live use.

## Hard rule

Do NOT proceed silently. Re-ping after reasonable timeout. The gate is "no plan without explicit spec approval".

## Idempotency

One-time approval per spec version. Re-iteration sends the user back to write-spec-doc.
