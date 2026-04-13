---
name: gitignore-update
description: Append .super/cache/ and .worktrees/ entries to the project's .gitignore. Idempotent dedup - re-running adds nothing if entries already present.
---

# gitignore-update

## What it does

Reads `<project>/.gitignore` (or creates it if absent) and ensures it contains:

```
.super/cache/
.worktrees/
```

Existing entries are preserved. Duplicate entries are not introduced. If the file ends without a trailing newline, one is added before appending.

## Why these entries

- `.super/cache/` holds per-project cache markers (HMAC-signed verdicts from super-code-review). They invalidate per-commit and should not be tracked.
- `.worktrees/` is the canonical per-project worktree directory (see the using-git-worktrees skill). Worktree contents are checkouts and must never be tracked in the parent repo.

## Idempotency

Idempotent append + dedup. Re-running with the entries already present is a no-op.
