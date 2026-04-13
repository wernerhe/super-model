---
name: write-design-doc
description: After Gate #1 (verbal design approval), write the design doc to docs/design/<topic>.md and commit it. The committed doc is the canonical reference for downstream review modules.
---

# write-design-doc

## What it does

1. Compose the design doc using the verbal sketch from `design-presentation` as the source.
2. Standard sections: Problem, Solution, Tradeoffs, Non-Goals, Risks, Open Questions.
3. Write to `docs/design/<topic>.md` (or `docs/design/<topic>/README.md` if the design has sub-pages).
4. Commit with a clear message: `Add design: <topic>`.

## Format

Markdown, ≥ 300 lines for non-trivial designs (substantial enough that downstream `audit-evaluation` has something to audit). Sub-files for any long appendices.

## Why commit immediately

A committed design doc:

- Survives chat context resets.
- Is reviewable as code (PR comments, blame, diff).
- Becomes the authoritative reference for `policy-design-fidelity` at execute time.

## Idempotency

If `docs/design/<topic>.md` already exists, ASK before overwriting. Re-runs after revision should produce a new commit (`Revise design: <topic>`), not a silent overwrite.
