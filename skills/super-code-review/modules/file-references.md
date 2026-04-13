---
name: file-references
description: Scan the diff for broken file references - imports of deleted files, orphaned files no longer imported by anything, and broken markdown links. Reports as minor findings unless a public API surface is implicated.
---

# file-references

## What it does

Across the changed code:

- **Dead imports:** files imported from no longer exist. Importing module either crashes at load time or the import is unreachable.
- **Orphan files:** files in the diff (added or pre-existing) that nothing imports. Often indicates a forgotten cleanup or a half-finished refactor.
- **Broken markdown links:** `[label](./path)` references in docs that point to nonexistent files.

## Severity

- `important` if the broken reference affects a public API or a documented surface.
- `minor` otherwise.

## Fix policy

`fix_with_confirm` - propose the obvious fix (remove the dead import, restore the missing file, update the link) and ask before applying.

## What it does NOT catch

- Cross-language dead references (e.g., a Python file imports a TS file via subprocess).
- References that exist at runtime via dynamic import / reflection.
- These need human eyes.

## Idempotency

Read-only.
