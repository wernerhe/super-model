---
name: commit-hygiene
description: Check the branch's commits for housekeeping issues - WIP commits, fixup commits, debug-print commits, commits with empty bodies, commits whose subject exceeds 72 characters. Block merge-ready verdict on hygiene violations.
---

# commit-hygiene

## What it does

Walks the commits on the current branch (since the merge base with `main` / target branch) and flags:

- **WIP commits:** subject contains `WIP`, `wip`, `TODO`, `tmp`, `save`, `dump`, etc.
- **Fixup commits:** subject starts with `fixup!`, `squash!`, `amend!`. These are amend markers, not real commits, and must be resolved via interactive rebase before merge.
- **Debug commits:** subject mentions `debug`, `print`, `breakpoint`, `console.log` and the diff bears it out.
- **Empty body:** commit has only a subject line, no body. Acceptable for trivial commits but flagged for substantial ones.
- **Subject too long:** commit subject exceeds 72 characters (breaks `git log --oneline` and most PR-display heuristics).

## Severity

- `critical` for fixup / squash markers - they will break merge if not resolved.
- `important` for WIP / debug commits in branch tip.
- `minor` for cosmetic issues (long subjects, empty bodies on small commits).

## Fix policy

`suggest_only` - rewriting commit history needs human judgment. Module proposes the interactive-rebase plan (squash these, amend those, drop the debug commit) but never auto-rebases.

## Idempotency

Read-only.
