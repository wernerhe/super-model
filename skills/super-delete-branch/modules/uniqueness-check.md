---
name: uniqueness-check
description: Determine whether the branch's tip commit is reachable from any other ref (other local branches, tags, remote branches). If reachable elsewhere, deletion is safe.
---

# uniqueness-check

## What it does

Asks the central question: "if I delete this branch, will I lose any commits?"

Concretely, checks whether the branch tip SHA is reachable from any OTHER ref:

```sh
git for-each-ref --format='%(refname)' refs/heads refs/tags refs/remotes \
  | grep -v "^refs/heads/<branch-being-deleted>$" \
  | xargs -I{} sh -c "git merge-base --is-ancestor <tip-sha> {} && echo {}"
```

If any other ref contains the tip as an ancestor, the commits live on -> safe delete.

## Output

```json
{
  "reachable_elsewhere": true,
  "via": ["refs/heads/main", "refs/remotes/origin/feature/foo"]
}
```

OR

```json
{
  "reachable_elsewhere": false,
  "via": []
}
```

## Why this matters

`git branch -d` already refuses to delete unreachable branches. `git branch -D` silently force-deletes them. Without this check, an LLM that defaults to `-D` to "just get it done" silently destroys work. With this check, the next module (`value-check`) can show the user EXACTLY what is at stake.

## Idempotency

Read-only. Never mutates git state.
