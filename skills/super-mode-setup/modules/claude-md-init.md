---
name: claude-md-init
description: Seed the project's CLAUDE.md with the Super-Model section on first install. Create-only - never overwrites existing CLAUDE.md content; preserves user edits across re-installs.
---

# claude-md-init

## What it does

On first install: creates `<project>/CLAUDE.md` if absent. Content seeded from `CLAUDE_MD_TEMPLATE` in `super-mode-setup.py`. The template references the absolute path to the Super-Model source directory and tells Claude to read it.

On re-install: detects existing CLAUDE.md, does NOT overwrite. If the file exists but the Super-Model section header is missing, reports as drift so the user can decide whether to re-seed.

## Idempotency

Append-only / create-only. Never destructive of user content.

## Why create-only

Users edit CLAUDE.md heavily - it is the canonical place for project-specific Claude guidance. A re-install that clobbered the file would erase that work. Worse, it would do so silently. The right boundary: Super-Model seeds it once; the user owns it after that.
