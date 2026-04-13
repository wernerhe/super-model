---
name: hooks-install
description: Merge the SessionStart hook entry into <project>/.claude/settings.json. Preserves existing hooks (additive merge), does not clobber user-configured hooks.
---

# hooks-install

## What it does

Reads `<project>/.claude/settings.json` (creates if absent), locates or initializes the `hooks.SessionStart` array, and appends a Super-Model entry that invokes `hooks/run-hook.cmd session-start` from the Super-Model source path:

```json
{
  "type": "command",
  "command": "\"<super-model-source>/hooks/run-hook.cmd\" session-start",
  "async": false
}
```

Existing SessionStart hooks (from other plugins / user-configured) are preserved. The Super-Model entry is added if not already present (idempotent dedup).

The matcher is `startup|clear|compact` - matching Claude Code's three session-init events.

## Why run-hook.cmd

The polyglot wrapper at `hooks/run-hook.cmd` is the SAME file on Windows and Unix. On Windows, cmd.exe runs the batch portion which finds Git for Windows bash. On Unix, bash treats the cmd block as a heredoc and falls through to the Unix exec line. Single source of truth.

## Idempotency

Merge with dedup on command-string match. Re-running with hook already present is a no-op.
