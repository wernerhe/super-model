---
name: push-readiness
description: Final check before declaring a branch merge-ready - no uncommitted changes, no detached HEAD, branch has an upstream or is set up to track one, and the remote is reachable.
---

# push-readiness

## What it does

Last-mile checks that catch the embarrassing "you said merge-ready but the branch isn't even pushed":

- `git status` clean? No uncommitted changes, no untracked files that should be committed.
- HEAD attached to a named branch (not a detached state from a rebase or checkout)?
- Upstream tracking ref set (`git for-each-ref --format='%(upstream:short)' refs/heads/<branch>`), OR user explicitly confirmed they want local-only?
- Remote reachable (`git ls-remote --heads <upstream-remote>`)?
- If pushed: is the local tip equal to the remote tip, or do we still need a push?

## Output

A final verdict:

```
Branch 'feature/foo' is merge-ready:
  - working tree:    clean
  - HEAD attached:   yes (feature/foo)
  - upstream:        origin/feature/foo (in sync)
  - remote:          reachable
```

OR a blocking issue list.

## Fix policy

`fix_with_confirm` for trivial cases (push the branch with `git push -u origin <branch>`); `suggest_only` for cases where context matters (uncommitted changes might be intentional WIP).

## Idempotency

Read-only at this module. Any actual push is a separate user decision after this module's output.
