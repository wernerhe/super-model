---
name: complexity
description: Flag functions over a complexity threshold (cyclomatic / cognitive) added or modified in the diff. Single-responsibility violations and overlong functions get surfaced for refactoring before they become tomorrow's tech debt.
---

# complexity

## What it does

For each function added or substantially modified in the diff:

- **Cyclomatic complexity:** count of independent paths. Default threshold: 10.
- **Cognitive complexity:** measure how hard the function is to follow (nested conditionals, recursion, mixed paradigms). Default threshold: 15.
- **Length:** lines of code. Default threshold: 80 lines per function.
- **Single-responsibility heuristic:** functions whose docstring or name suggests "do A and B" or whose body has clearly separable sections.

## Severity

- `important` for functions that exceed multiple thresholds simultaneously.
- `minor` for single-threshold exceedances on otherwise-clear functions.

## Fix policy

`suggest_only` - the module suggests where the function could be split but never auto-refactors. Refactor decisions need human judgment about cohesion and naming.

## What it does NOT catch

- Function-level complexity that's appropriate for the problem (parsers, complex domain logic).
- The thresholds are heuristics; the user can adjust them in `.super/config.json` if the project genuinely needs higher values.

## Idempotency

Read-only.
