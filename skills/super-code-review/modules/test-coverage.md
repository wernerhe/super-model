---
name: test-coverage
description: Check that changed lines have test coverage. New branches in conditional logic require new test cases. Reports gaps with file:line precision so the user knows exactly where to add tests.
---

# test-coverage

## What it does

For the lines changed in the diff:

- Run coverage tooling if available (`coverage.py`, `nyc`, `tarpaulin`, etc.). Identify which changed lines are not exercised by tests.
- For new conditionals (added `if` / `match` / `?:`), verify at least one test case exercises each branch.
- For new public functions, verify at least one direct test exists.

## Severity

- `critical` if changed lines in a Rigid module (defined in `using-super-model`) are uncovered.
- `important` if new public functions are uncovered.
- `minor` for partial coverage on internal helpers.

## Fix policy

`suggest_only` - the module proposes specific test cases ("write a test for case X where input is empty") but never auto-writes tests. Test design is human work.

## What it does NOT catch

- Tests that pass for the wrong reason (no real assertions, broken mocks).
- The test-driven-development skill catches those upstream by enforcing RED-GREEN-REFACTOR.

## Idempotency

Read-only.
