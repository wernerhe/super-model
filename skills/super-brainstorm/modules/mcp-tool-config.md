---
name: mcp-tool-config
description: Conditional module - only runs if approach-profile == "MCP integration" or clarifying-questions surfaced MCP needs. Walks the user through MCP selection / wiring and chains to super-mcp-builder when an actual install is needed.
enabled_by_default: false
---

# mcp-tool-config

## What it does

Conditional. Runs only when:

- Approach profile = "MCP integration", OR
- Clarifying questions surfaced an MCP need (e.g., user described needing database access, browser automation, ticketing API).

Walks the user through:

1. What capability does the MCP need to provide?
2. Is there an existing MCP that does this? (Calls `super-mcp-builder` -> `discover-mcps` to check.)
3. Configure existing OR scaffold new (chain-fire `super-mcp-builder`).
4. Record the MCP wiring in the design doc so downstream readers know it's a dependency.

## Why conditional

Most projects don't add MCPs each brainstorm cycle. Making this default-disabled means the modal brainstorm flow doesn't waste a step on irrelevant config.

## Idempotency

May chain-fire `super-mcp-builder`; the wiring change is destructive but the design-doc note is just text.
