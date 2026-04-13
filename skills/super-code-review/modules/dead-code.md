---
name: dead-code
description: Identify functions, classes, variables, or imports that are defined but never referenced after the changes in the diff. Reports as important if the dead code is in a frequently-edited file (likely to cause confusion).
---

# dead-code

## What it does

For each symbol defined in the diff (function, class, top-level variable, imported name):

- Search the codebase for references after the change.
- If zero references AND the symbol is not part of a public API surface (no `__all__` membership, not exported, not in a public docstring), flag.

## Severity

- `important` if the dead symbol is in a frequently-edited file - dead code in active areas confuses readers and accumulates.
- `minor` if the dead symbol is in a rarely-touched module.

## Fix policy

`fix_with_risk_report` - propose deletion with a "risk: low (no references found)" annotation. The user accepts the deletion or explicitly keeps the symbol (e.g., it's a stub for a planned feature).

## What it does NOT catch

- Dynamically-referenced symbols (`getattr`, eval, plugin loaders).
- Symbols used in test fixtures only (these are sometimes legitimately dead in prod).
- These need human eyes.

## Idempotency

Read-only.
