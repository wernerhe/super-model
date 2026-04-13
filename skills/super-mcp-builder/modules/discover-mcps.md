---
name: discover-mcps
description: Enumerate MCP servers known to the system - those configured in ~/.claude/.mcp.json, the project's .mcp.json, and well-known upstream registries. Read-only.
---

# discover-mcps

## What it does

Builds a unified view of all MCPs the user has access to:

1. **Already-configured (user-level):** read `~/.claude/.mcp.json`. List MCPs by name + command.
2. **Already-configured (project-level):** read `<project>/.mcp.json`. List MCPs.
3. **Upstream catalog:** present a short list of widely-used MCPs the user may not know about (filesystem, github, postgres, sqlite, fetch, brave-search, etc.) with their canonical install commands.

## Output

A grouped table:

| Scope | Name | Command | Status |
|---|---|---|---|
| user | filesystem | npx @modelcontextprotocol/server-filesystem | configured |
| project | github | npx @modelcontextprotocol/server-github | configured |
| catalog | postgres | npx @modelcontextprotocol/server-postgres | available |

## Why

Most MCP confusion comes from "do I have this one already?" The flat answer up front prevents redundant installs and tells the user which scope a given MCP lives in.

## Idempotency

Read-only.
