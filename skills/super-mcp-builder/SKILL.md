---
name: super-mcp-builder
description: Discover, install, configure, or scaffold MCP (Model Context Protocol) servers for the current project. Reads the user's MCP config and the project's .mcp.json; does NOT bundle MCP source code in the Super-Model repo.
---

# super-mcp-builder

The MCP wiring skill. Super-Model's deliberate boundary: the repo references MCPs by command and args; it does not ship MCP source code. Users build / clone / install MCPs from their canonical sources and wire them through this skill.

## When to use

- The user needs a new MCP capability (database access, browser control, ticketing, file search, etc.).
- An existing MCP is misconfigured or its command line has changed.
- A new MCP is being authored from scratch.

## The 4-module flow

1. `discover-mcps` - enumerate MCPs already referenced in `~/.claude/.mcp.json`, `<project>/.mcp.json`, and well-known upstream registries.
2. `install-upstream` - given a user-chosen upstream MCP, install it via its canonical command (uvx, npx, pipx, docker run, etc.) and add the entry to `<project>/.mcp.json`.
3. `alter-config` - modify an existing MCP entry in `<project>/.mcp.json` (change args, env vars, transport).
4. `build-new` - scaffold a brand-new MCP server in a separate repo (NOT inside Super-Model); guide the user through stdio / SSE choice and tool definitions.

## Hard boundary: no MCP source in Super-Model

This skill NEVER:

- Clones MCP source into the Super-Model repo.
- Adds MCP code as a git submodule.
- Vendors MCP code into `vendor/` or similar.

This skill ALWAYS:

- References MCPs by their canonical command line (uvx package, npx package, docker image).
- Stores the wiring in `<project>/.mcp.json`.
- For built-from-scratch MCPs: creates them in their own repo and references them by absolute path or git URL.

## Verify after running

- `<project>/.mcp.json` validates against the MCP config shape (well-formed JSON, `mcpServers` is a dict).
- The intended MCP appears in the Claude Code MCP picker / Windsurf MCP list after a restart.
- No MCP source code exists under the Super-Model directory tree.
