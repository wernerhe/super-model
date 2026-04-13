---
name: policy-design-fidelity
description: After each step, verify the step's output matches the design doc and spec. Flag drift (the implementation diverged from what was approved) so the user can either re-approve the new direction or roll back.
hooks_consumed:
  post-step-check: design_fidelity_check
---

# policy-design-fidelity

## What it does

After each step completes, compare:

- The step's diff (what changed).
- The step's description (what the plan said should change).
- The relevant section of the design doc and spec.

Flag drift in three categories:

- **Scope creep:** the step touched files outside its declared `files` list, or added functionality not in the spec.
- **Spec deviation:** the implementation differs from the spec's signature / behavior contract.
- **Design contradiction:** the implementation contradicts a calibrated design decision (something the design doc says NOT to do).

## Output

A per-step fidelity record. Drift findings carry severity:

- `critical` for design contradictions.
- `important` for spec deviations.
- `minor` for scope creep.

## Continue or stop

- No drift -> continue.
- Minor drift -> note and continue.
- Important / critical drift -> stop. User decides: roll back, amend the design / spec, or accept the drift with a documented rationale.

## Why this matters

Plans are calibrated against designs. A plan can be technically complete (all steps done, tests pass) but functionally wrong (the result doesn't match the approved design). This policy catches that gap.

## Idempotency

Read-only verification.
