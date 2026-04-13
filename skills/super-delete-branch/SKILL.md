---
name: super-delete-branch
description: Safely delete a git branch after verifying its commits are reachable elsewhere (merged or pushed) so no work is silently lost. Refuses to delete a branch holding unique work without explicit confirmation.
---

# super-delete-branch

A safety-first branch-deletion flow. The default `git branch -d` already refuses when commits are unreachable, but `-D` force-deletes silently - a common foot-gun. This skill never invokes `-D` without an explicit user confirmation after presenting what's at stake.

## When to use

- The user asks to delete a branch.
- The user has finished work on a branch and wants to clean it up.
- A worktree on a stale branch needs to be removed.

## The 4-module flow

1. `branch-info-collect` - read the branch's tip SHA, upstream tracking, last commit subject, ahead/behind counts vs main.
2. `uniqueness-check` - is the tip commit reachable from any other ref (main, other branches, tags, remote branches)?
3. `value-check` - if NOT reachable, show the user what they would lose: list of commits unique to this branch, last commit message + date.
4. `delete-confirm` - either safe-delete (`git branch -d`) when reachable, OR ask explicit confirmation with the loss preview before `git branch -D`.

## Hard rules

- NEVER run `git branch -D` without an explicit "yes delete it" from the user AFTER showing the value preview.
- ALWAYS show the upstream-tracking state. A branch pushed to a remote may be safe to delete locally even if not merged - the user may know the remote is the canonical copy.
- If the branch has an active worktree (`git worktree list` shows it), refuse and direct the user to `git worktree remove` first.

## Verify after running

- `git branch -a` no longer lists the deleted branch.
- No "your branch is ahead" or dangling-commit warnings.
- The associated worktree (if any) is also cleaned up.
