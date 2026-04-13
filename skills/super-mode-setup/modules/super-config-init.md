---
name: super-config-init
description: Create the project's .super/config.json on first install. Create-only - never overwrites a user-edited config. Empty config means the skill catalog runs with defaults.
---

# super-config-init

## What it does

Creates `<project>/.super/config.json` with `{}` on first install. The empty config means every skill runs with its baked-in defaults from its `manifest.json`.

If the file already exists, leaves it untouched.

## Idempotency

Create-only. Re-install never overwrites a user-edited config.

## Schema

The file is validated against `schemas/config.schema.json` on every load. A hand-edited bad config is rejected at the resolve point with the file path embedded in the error - so the user gets actionable feedback rather than an opaque traceback later at field access.
