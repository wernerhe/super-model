---
name: approach-profile
description: First module. Ask the user to pick an approach profile that shapes the rest of the brainstorm flow - new feature, bug fix, refactor, MCP integration, infrastructure, exploratory. The profile activates conditional modules downstream.
---

# approach-profile

## Deployment preflight (Claude Code only)

Before asking the approach-profile question, on a **Claude Code** deployment only
(`super_lib.deployment.is_claude_code` — the env signal `CLAUDE_PLUGIN_ROOT` is
set and `CURSOR_PLUGIN_ROOT` is not), check the live model and reasoning effort
against the project's Claude preferences
(`super_lib.config.deployment_preferences("super-brainstorm")`, default
`model: opus`, `effort: xhigh`). If the session is below target, surface **one
advisory line** recommending the switch before the design phase, e.g.:

> super-brainstorm is calibrated for current Opus at xhigh effort. You're on
> `<model>`/`<effort>` — consider `/model opus` and `/effort xhigh` before we
> start the design.

This nudge is **advisory and non-blocking**: never stall the gated flow on it,
never repeat it, and never fire it on a non-Claude deployment (the preference is
Claude-specific). The persistent default is already seeded into
`.claude/settings.json` by `super-model-setup`; this line only covers a session
the user has manually moved off the default.

## What it does

Presents the user with a multi-choice question about the nature of the work:

```
What kind of work is this?
  1. New feature        - adding capability that didn't exist
  2. Bug fix            - fixing a broken behavior
  3. Refactor           - restructuring without changing behavior
  4. MCP integration    - wiring or building an MCP server
  5. Infrastructure     - tooling, CI, deployment, config
  6. Exploratory        - "I'm not sure yet; let's figure it out"
  7. What do you think Claude   - I'll propose one based on context
```

## Effect on downstream modules

- "MCP integration" enables `mcp-tool-config` (otherwise default-disabled).
- "Infrastructure" or "Exploratory" may enable `autonomous-mode-config` (long-running unattended work).
- "Bug fix" suggests `systematic-debugging` should run upstream of the design phase.
- "Refactor" makes test-coverage gates more strict.

## Output

A single `approach_profile` value carried through the rest of the flow.

## Idempotency

Single-choice question; one answer per invocation.
