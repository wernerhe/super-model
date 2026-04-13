---
name: super-mode-setup
description: Run super-mode-setup.py to install Super-Model into a target project - CLAUDE.md, .super/config.json, .gitignore entries, MCP wiring, SessionStart hook, install-approval policy, and the 7 slash command shims for Claude Code + Windsurf + Cline (VS Code).
---

# super-mode-setup

Orchestrates the per-project install of Super-Model. The LOGICAL flow lives here in module bodies; the actual filesystem work lives in `super-mode-setup.py` at the repo root.

The skill describes WHAT each step does; the script DOES the work. This separation lets the LLM reason about steps without re-implementing them.

## When to use

- The user runs `/super-mode-setup` (or invokes `super-mode-setup.py` / `.bat` / `.sh` directly).
- A new project is being initialized with Super-Model.
- A re-install is needed to verify each step is still in canonical state.

## What the 8 modules do (in order)

1. `claude-md-init` - seed `<project>/CLAUDE.md` with the Super-Model section (create-only).
2. `super-config-init` - write `<project>/.super/config.json` (create-only).
3. `gitignore-update` - append `.super/cache/` and `.worktrees/` to `.gitignore` (dedup).
4. `project-type-detection` - read `pyproject.toml` / `package.json` / `Cargo.toml` / etc.; record findings.
5. `mcp-wiring` - copy relevant entries from `~/.claude/.mcp.json` into `<project>/.mcp.json`.
6. `hooks-install` - merge SessionStart hook into `<project>/.claude/settings.json` (preserve existing).
7. `permissions-install` - merge 20 install-approval Bash rules into `permissions.ask`; preserve `$defaults` sentinel.
8. `slash-commands-install` - write 7 `super-*` slash command files for Claude Code (`.claude/commands/`), Windsurf (`.windsurf/workflows/` + `.windsurf/rules/super-model.md`), and Cline (`.clinerules/workflows/` + `.clinerules/super-model.md`).

All 8 are idempotent. Re-running produces no diffs if nothing has changed.

## Drive-root refusal

`super-mode-setup.py` refuses to run if the parent of its own directory resolves to a drive root (`C:\`, `/`). The fail-fast message tells the user to drop the Super-Model folder INSIDE a project directory.

## Verify after running

- `/super` slash menu shows 7 entries (no `super-model:` namespace pollution from a plugin co-install).
- `<project>/.claude/settings.json` has the SessionStart hook + 20 install-approval rules.
- `<project>/.super/config.json` exists.
- `<project>/CLAUDE.md` has a Super-Model section appended.
- `<project>/.gitignore` has `.super/cache/` and `.worktrees/`.
- `<project>/.windsurf/workflows/super-*.md` (7 files), `<project>/.windsurf/rules/super-model.md`.
- `<project>/.clinerules/workflows/super-*.md` (7 files), `<project>/.clinerules/super-model.md`.

## Reproduction notes

- Module bodies are the source of truth for WHAT each step does; the Python script must agree with them.
- Tests under `tests/foundation/test_super_mode_setup_modules.py` assert manifest entries map 1:1 to module files.
- Two heavier tests (`test_super_mode_setup_script.py`, `test_super_mode_setup_security_hardening.py`) exercise the script behavior end-to-end.
