---
name: namespace-consistency
description: Check that new identifiers (file names, module names, function names, class names) follow the project's existing naming conventions. Reports drift before it sets a new precedent.
---

# namespace-consistency

## What it does

For each new identifier introduced in the diff:

- Detect the project's convention by sampling existing names in the same scope (snake_case vs camelCase vs kebab-case, plural vs singular for collections, etc.).
- Flag the new name if it deviates without an obvious reason.
- Suggest the conforming variant.

## Examples

- File added: `userProfile.py` in a project where everything else is `user_profile.py`-style snake_case -> flag.
- Function added: `GetCacheMarker()` in a Python codebase where the rest is `get_cache_marker()` -> flag.
- Constant added: `cacheKey` in a module where other constants are `CACHE_KEY` -> flag.

## Severity

`minor` by default. Convention drift is real but rarely blocking. Promote to `important` if the new identifier is part of a public API surface where the convention is documented.

## Fix policy

`suggest_only` - convention drift can be intentional (e.g., interop with a third-party library that uses different conventions). Present the suggestion; let the human decide.

## Idempotency

Read-only.
