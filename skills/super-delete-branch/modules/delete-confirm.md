---
name: delete-confirm
description: Issue the actual delete. Safe-delete (git branch -d) when reachable elsewhere; otherwise require an explicit user confirmation after the value-check preview before issuing git branch -D.
---

# delete-confirm

## What it does

Branches based on the upstream module outputs:

### Reachable elsewhere (uniqueness-check: true)

Issue `git branch -d <branch>`. Safe; no confirmation needed.

### NOT reachable elsewhere (uniqueness-check: false)

1. Display the `value-check` preview to the user.
2. Ask: "Delete branch `<name>` and discard these <N> commits? (yes/no)"
3. ONLY on explicit "yes" - run `git branch -D <branch>`.
4. Any other response - abort, leave the branch alone.

### Active worktree present

Refuse to delete. Direct the user to:

```sh
git worktree remove <path-to-worktree>
git branch -D <branch>   # or -d if safe
```

## Hard rules

- NEVER run `git branch -D` without an explicit user "yes" AFTER seeing the value-check preview.
- NEVER bypass uniqueness-check + value-check just because "the user is sure".
- If the upstream tracking ref is pushed, mention this in the prompt: "Note: this branch was pushed to <upstream>. The remote copy is unaffected."

## Idempotency

Single destructive action. Re-running on an already-deleted branch produces a clear "branch not found" error, not a silent no-op.
