---
name: branch-info-collect
description: Read git metadata about the branch to be deleted - tip SHA, upstream tracking, last commit subject + author + date, and ahead/behind counts versus main. Read-only.
---

# branch-info-collect

## What it does

Collects metadata about the branch the user wants to delete:

- Tip SHA (`git rev-parse <branch>`).
- Upstream tracking ref, if any (`git for-each-ref --format='%(upstream:short)' refs/heads/<branch>`).
- Last commit subject, author, and date.
- Ahead / behind counts vs `main` (`git rev-list --left-right --count main...<branch>`).
- Active worktree presence (`git worktree list | grep -F <branch>`).

## Output

A structured record:

```json
{
  "branch": "feature/foo",
  "tip_sha": "a1b2c3d",
  "upstream": "origin/feature/foo",
  "last_commit": {"subject": "Add foo widget", "author": "Harry", "date": "2026-05-20"},
  "ahead_of_main": 3,
  "behind_main": 12,
  "worktree": null
}
```

## Why structured output

Downstream modules (`uniqueness-check`, `value-check`) consume this record to make decisions. Keeping the shape consistent means the value-preview to the user is always complete.

## Idempotency

Read-only. Never mutates git state.
