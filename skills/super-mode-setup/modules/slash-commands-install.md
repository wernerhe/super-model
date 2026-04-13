---
name: slash-commands-install
description: Write 7 super-* slash command shim files for Claude Code (.claude/commands/), Windsurf (.windsurf/workflows/ + .windsurf/rules/super-model.md), and Cline (.clinerules/workflows/ + .clinerules/super-model.md). Drift-detected re-installs preserve user edits.
---

# slash-commands-install

## What it does

Writes the 7 user-invokable slash command surface to all three supported IDEs:

### Claude Code

- `<project>/.claude/commands/super-brainstorm.md`
- `<project>/.claude/commands/super-code-review.md`
- `<project>/.claude/commands/super-delete-branch.md`
- `<project>/.claude/commands/super-mcp-builder.md`
- `<project>/.claude/commands/super-mode-setup.md`
- `<project>/.claude/commands/super-prepare-branch.md`
- `<project>/.claude/commands/super-visual-debug.md`

### Windsurf

- `<project>/.windsurf/workflows/super-*.md` (7 files, same names as above)
- `<project>/.windsurf/rules/super-model.md` (always-on rule body)

### Cline (VS Code)

- `<project>/.clinerules/workflows/super-*.md` (7 files)
- `<project>/.clinerules/super-model.md` (always-on rule body; every file in `.clinerules/` is implicitly always-on for Cline, no `trigger: always_on` frontmatter needed)

## Drift detection

On re-install, the module computes the EXPECTED content of each slash command file from the current Super-Model source and compares it to what exists on disk:

- File identical -> no-op.
- File missing -> create it.
- Only frontmatter `description:` differs -> rewrite (description-string updates without clobbering body).
- Body differs from expected -> flag as user-edited; do NOT overwrite; report to user.

This lets Super-Model ship description-string updates without erasing user customizations to the shim bodies.

## Why three IDEs

Claude Code, Windsurf, and Cline are the three major agentic IDEs the user wants Super-Model to feel native in. A single `super-mode-setup` run wires all three so the user does not have to think about which IDE they happen to be using.

## Idempotency

Drift-detected re-write. Re-running on a clean state is a no-op.
