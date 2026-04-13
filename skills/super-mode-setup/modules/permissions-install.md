---
name: permissions-install
description: Merge 20 install-approval Bash patterns into <project>/.claude/settings.json's permissions.ask array. Preserves $defaults sentinel and any existing user-added entries.
---

# permissions-install

## What it does

The install-approval policy is a set of 20 canonical Bash command patterns that should require user approval before execution - typically package-manager invocations (`pip install`, `npm install`, `cargo install`, `apt install`, etc.). These are listed in `CANONICAL_INSTALL_RULES` inside `super-mode-setup.py`.

This module merges those 20 patterns into `<project>/.claude/settings.json` at `permissions.ask[]`, with the `"$defaults"` sentinel preserved at the front of the array.

Merge semantics:

- Existing `"$defaults"` stays at position 0.
- Existing user-added rules are preserved.
- Duplicates are not introduced (string-equality dedup).
- The 20 Super-Model rules are appended after `"$defaults"` and any existing entries.

## Why

Package-manager commands can install arbitrary code with elevated privileges. Requiring explicit user approval at the IDE permission boundary prevents an LLM from accidentally pulling in a typo-squatting package or escalating the environment without consent.

## Idempotency

Merge with dedup. Re-running with rules already present is a no-op.
