---
name: build-new
description: Scaffold a brand-new MCP server in its own repository (NEVER inside Super-Model). Guide the user through stdio vs SSE choice, tool definitions, and the canonical project layout.
---

# build-new

## What it does

When the user needs an MCP that does not exist upstream, this module scaffolds a fresh MCP server project. The MCP lives in its OWN repository, not inside Super-Model.

## Process

1. **Choose location:** ask the user where to create the new MCP project. Default suggestion: a sibling directory to `<current-project>`, e.g., `<workspace>/my-custom-mcp/`.
2. **Choose language:** Python (uv / pipx ergonomics) or Node (npx ergonomics).
3. **Choose transport:** stdio (simpler, most common) or SSE / HTTP (when the MCP needs to be remote).
4. **Initialize the project:**
   - `uv init my-custom-mcp` for Python.
   - `npm init -y` for Node.
   - Install the MCP SDK: `uv add mcp` or `npm install @modelcontextprotocol/sdk`.
5. **Scaffold a minimal server:** a single tool that echoes its input, to prove the wiring works.
6. **Wire into `<current-project>/.mcp.json`:** reference the MCP by absolute path (stdio) or URL (SSE / HTTP).
7. **Test:** restart the IDE and verify the echo tool appears.

## Hard boundary

The new MCP project is NEVER created under the Super-Model source tree. Super-Model's repo stays MCP-source-free.

## Verify

- The new MCP repo has its own `pyproject.toml` / `package.json` and git history.
- `<current-project>/.mcp.json` references the new MCP by absolute path or URL.
- The echo tool returns its input verbatim when called from the IDE.

## Why

Authoring an MCP inside Super-Model would couple the lifecycles. A bug in the MCP would block Super-Model commits; a Super-Model refactor would risk breaking the MCP. Separate repos = independent lifecycles.
