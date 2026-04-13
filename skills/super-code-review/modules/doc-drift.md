---
name: doc-drift
description: Check that public API changes in the diff are reflected in docstrings, README, CHANGELOG, and architecture docs. Reports documented surfaces that no longer match the code.
---

# doc-drift

## What it does

For each public-API change in the diff:

- Function signature changed -> docstring still describes the old signature?
- Public function deleted -> README / docs still reference it?
- New feature added -> CHANGELOG `Unreleased` section mentions it?
- Architecture-level change (new module, removed module) -> `docs/architecture/` reflects it?

## Severity

- `important` for stale docstrings on public APIs (downstream callers consult them).
- `important` for missing CHANGELOG entries on user-visible changes.
- `minor` for stale internal-architecture notes.

## Fix policy

`fix_with_confirm` - propose the doc update (suggested docstring, suggested CHANGELOG entry) and ask. Doc rewrites are easy for LLMs and high-value to keep in sync.

## What it does NOT catch

- Documentation tone / quality issues (rambling docstrings that are technically correct).
- The `writing-skills` skill handles content quality at authoring time.

## Idempotency

Read-only.
