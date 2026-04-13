---
name: mcp-wiring
description: Copy relevant MCP server entries from ~/.claude/.mcp.json into <project>/.mcp.json. Super-Model does NOT bundle MCP source code; this module wires references only.
---

# mcp-wiring

## What it does

Reads `~/.claude/.mcp.json` (user-level MCP configuration), filters for entries that look applicable to the target project, and merges them into `<project>/.mcp.json`. Existing `<project>/.mcp.json` entries are preserved; duplicates are not introduced.

If `~/.claude/.mcp.json` does not exist, the project file is initialized as `{"mcpServers": {}}` and the user is informed they can run `super-mcp-builder` later to wire MCPs.

## What it does NOT do

This module NEVER copies MCP server source code into the Super-Model repo. The repo references MCPs by name and command; it does not ship them. This is a deliberate boundary: shipping third-party MCP source would create a maintenance burden + a sprawling supply-chain surface area. Users wire their own.

The companion skill `super-mcp-builder` handles discovery, installation, and configuration of MCPs from upstream sources.

## Idempotency

Merge with dedup. Re-running with no upstream changes is a no-op.
