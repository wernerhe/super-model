---
name: alter-config
description: Modify an existing MCP entry in <project>/.mcp.json - change args, env vars, transport, or rename. Validates that the resulting config is well-formed JSON before writing.
---

# alter-config

## What it does

Edits an existing entry under `mcpServers` in `<project>/.mcp.json`. Common alterations:

- Change `args` (e.g., add a `--root` path for the filesystem MCP).
- Add or modify `env` vars (e.g., set `GITHUB_PERSONAL_ACCESS_TOKEN`).
- Switch transport (stdio vs SSE / HTTP).
- Rename the MCP key.

## Process

1. Read current entry; present to user.
2. Apply requested change in memory.
3. Validate resulting `.mcp.json` parses as JSON with `mcpServers` as a dict.
4. Write via the atomic-write helper (lock + fsync + 0600 on POSIX).
5. Confirm with user; instruct to restart the IDE for changes to take effect.

## Hard rules

- NEVER edit `~/.claude/.mcp.json` (user-level) without explicit user instruction. The default scope is project-level.
- NEVER embed plaintext secrets (API tokens) in `<project>/.mcp.json` if the project is tracked by git. Recommend `env` reference instead: `"env": {"GITHUB_TOKEN": "${GITHUB_TOKEN}"}` with the actual token in `.env` or shell rc.

## Idempotency

Whole-file rewrite via atomic-write. Re-applying the same change is a no-op (file content identical).
