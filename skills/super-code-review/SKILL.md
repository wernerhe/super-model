---
name: super-code-review
description: Run a comprehensive code review at a milestone (typically before merging a feature branch). Writes an HMAC-signed cache marker for super-prepare-branch to consume; if nothing changed since the last review, super-prepare-branch can skip re-running.
---

# super-code-review

The comprehensive code review skill. Catches the issues that fast feedback loops miss - dead code, namespace drift, dependency rot, coverage gaps - by sweeping the diff systematically across 9 dimensions.

## When to use

- A feature branch is "done" and the user is about to push / open PR / merge.
- A risky refactor needs a once-over before going downstream.
- A `super-prepare-branch` invocation finds no cache marker and chain-fires this skill.

## The 9-module sweep

1. `file-references` - dead imports, orphan files, broken doc links.
2. `namespace-consistency` - new identifiers fit existing naming conventions.
3. `dead-code` - functions / variables / imports defined but never used in the diff.
4. `test-coverage` - changed lines covered by tests; new branches have tests.
5. `security-scan` - secrets in plaintext, command injection, dependency vulns.
6. `dependency-health` - new deps vetted, version pins reasonable, no abandoned packages.
7. `doc-drift` - public API changes reflected in docs / READMEs / docstrings.
8. `performance-hotspots` - O(n^2) inside loops, accidental N+1, repeated regex compiles.
9. `complexity` - functions over a threshold (cyclomatic / cognitive), single-responsibility violations.

Each module produces zero or more findings tagged with severity (critical / important / minor) and an optional fix proposal.

## Cache marker output

On successful completion, writes:

```
<project>/.super/cache/code-review-<commit-sha>.json
```

via `super_lib.cache.write_marker`. The payload includes:

- `verdict`: READY-TO-MERGE | NEEDS-FIXES.
- `findings`: list of findings with severity, file, line range, description, suggested fix.
- `commit_sha`: HEAD SHA at review time.
- `timestamp`: UTC ISO-8601.

HMAC-signed so a downstream `super-prepare-branch` can trust the verdict; tampered markers are treated as missing and trigger a re-review.

## Hard rules

- NEVER claim "READY-TO-MERGE" with unresolved CRITICAL findings.
- ALWAYS write the cache marker, even on NEEDS-FIXES verdict - super-prepare-branch needs the record.
- NEVER auto-apply fixes from modules marked `fix_policy: never`. Always present and ask.

## Verify after running

- `<project>/.super/cache/code-review-<sha>.json` exists with a valid HMAC.
- The verdict matches the user's assessment (no over-stating "ready").
- Each finding has a clear file:line and a description the user can act on.
