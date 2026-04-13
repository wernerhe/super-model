---
name: value-check
description: If the branch holds commits not reachable elsewhere, enumerate them and present a human-readable loss preview to the user. Skipped when uniqueness-check says reachable_elsewhere is true.
---

# value-check

## What it does

Runs only when `uniqueness-check` reports `reachable_elsewhere: false`. Enumerates the commits that exist ONLY on the branch being deleted:

```sh
git log <branch> --not $(git for-each-ref --format='%(refname)' refs/heads refs/tags refs/remotes | grep -v "^refs/heads/<branch>$")
```

For each unique commit, captures:

- Short SHA
- Subject (first line of commit message)
- Author name
- Author date

## Output

A formatted preview the user sees BEFORE the delete-confirm prompt:

```
Branch 'feature/wip-experiment' holds 3 commits not reachable elsewhere:

  a1b2c3d  2026-05-18  Harry  Try alternative caching approach
  e4f5g6h  2026-05-19  Harry  WIP: refactor cache.py
  i7j8k9l  2026-05-20  Harry  Squash later: trial implementation

Deleting this branch will discard these 3 commits permanently
unless they are checked out elsewhere first.
```

## Why preview before delete

LLMs are biased toward action. Without an explicit loss preview at the user's eyeballs, an "OK delete it" can mean "OK delete it because you said it's safe" when actually it isn't. The preview makes the cost concrete.

## Idempotency

Read-only.
