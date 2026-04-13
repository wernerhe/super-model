---
name: rebase-preview
description: Dry-run a rebase of the current branch onto the target branch (typically main). Surface conflicts before the actual rebase so the user can resolve them deliberately rather than mid-merge.
---

# rebase-preview

## What it does

1. Determine the target branch (default `main`; configurable via `.super/config.json` or by user override).
2. Fetch the target ref to ensure it's current.
3. Use `git merge-tree` (or a temporary worktree with `--no-commit` rebase) to detect conflicts WITHOUT modifying any working state.
4. For each conflict, capture: file path, the conflicting hunk, the local change, the target-branch change.

## Output

If clean -> "rebase preview clean; no conflicts against `<target>`."

If conflicts -> list per file with the conflicting hunks shown:

```
src/foo.py:42-48
  Local:   def foo(x): return x + 1
  Target:  def foo(x, y): return x + y
  Hint:    signature drift; coordinate with target-branch author.
```

## Hard rule

NEVER auto-rebase to "resolve" conflicts. Conflict resolution requires human judgment about which version of the truth is correct. Surface and stop.

## Idempotency

Read-only. Uses `git merge-tree` or a temp worktree; the user's primary working tree is never modified.
