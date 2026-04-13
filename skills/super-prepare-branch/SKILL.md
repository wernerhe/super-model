---
name: super-prepare-branch
description: Verify a feature branch is merge-ready - check for a fresh super-code-review verdict, clean commit history, no conflicts on rebase preview, and remote push-readiness. Reads the HMAC-signed code-review cache marker; chain-fires super-code-review if missing or stale.
---

# super-prepare-branch

The merge-gate skill. Run before opening a PR or pushing to a shared branch. Cheap to run repeatedly because it relies on a cache marker from `super-code-review`; if nothing has changed since the last review, no re-review.

## When to use

- The user is about to open a PR.
- The user is about to push a branch to the team's shared remote.
- A worktree branch is "done" and ready to merge.

## The 4-module flow

1. `review-cache-check` - read the HMAC-signed code-review marker for the current HEAD SHA. If present and HMAC-valid, skip re-review. Otherwise chain-fire `super-code-review`.
2. `commit-hygiene` - check commit messages, no fixup commits left, no commits with subject like "WIP" or "save".
3. `rebase-preview` - dry-run a rebase onto the target branch (typically `main`); report any conflicts.
4. `push-readiness` - check that the branch is pushed (or ready to push), no detached HEAD, no uncommitted changes.

## Cache integration

The `review-cache-check` module is the integration point between this skill and `super-code-review`. Marker shape:

```
<project>/.super/cache/code-review-<commit-sha>.json
```

The HMAC integrity gate is the key trust boundary: if someone (or some process) tampered with the marker to flip the verdict to READY-TO-MERGE, the HMAC mismatches and `read_marker` returns `None`. That triggers a real re-review.

## Hard rules

- NEVER claim "merge-ready" without a fresh READY-TO-MERGE verdict from super-code-review.
- NEVER bypass the rebase preview to avoid surfacing conflicts.
- If `commit-hygiene` finds WIP / fixup commits, ASK the user to squash or amend before proceeding.

## Verify after running

- The user has a clear yes / no on "is this branch ready to merge?"
- Any blocking issues are surfaced with file:line precision.
- The cache marker (if present at start) was used; the re-review (if triggered) wrote a fresh marker.
