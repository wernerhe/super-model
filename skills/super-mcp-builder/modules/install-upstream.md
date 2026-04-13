---
name: install-upstream
description: Install an existing upstream MCP server via its canonical command (uvx / npx / pipx / docker) and add the entry to <project>/.mcp.json. Does not vendor MCP source code.
---

# install-upstream

## What it does

Given a user-chosen upstream MCP (by name or upstream URL):

1. Determine the canonical install command from the MCP's documentation:
   - Python: `uvx <package>` or `pipx install <package>`
   - Node: `npx -y <package>`
   - Docker: `docker run --rm -i <image>`
2. Construct the `mcpServers.<name>` entry with `command`, `args`, and optional `env`.
3. Add the entry to `<project>/.mcp.json` (creates the file with `{"mcpServers": {}}` if absent).
4. If `<project>/.mcp.json` already has an entry under that name, prompt before overwriting.

## What it does NOT do

- Does NOT clone the MCP's git repo into `<project>/`.
- Does NOT vendor the MCP source into Super-Model.
- Does NOT install the MCP into `~/.claude/.mcp.json` (user-level) unless explicitly requested.

## Verify

After install:

- `<project>/.mcp.json` parses as valid JSON.
- The MCP's canonical command works in a separate terminal (e.g., `npx -y @modelcontextprotocol/server-filesystem` exits with a usage banner).
- Restart the IDE and the MCP appears in the picker.

## Idempotency

If the entry already exists with identical content, no-op. If different content, prompt before overwrite.
