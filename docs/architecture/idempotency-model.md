# Idempotency model: super-mode-setup.py

Every install step in `super-mode-setup.py` is idempotent. Running the script twice in a row on the same target produces no diffs unless the source ships new content. User edits to user-owned files are preserved.

## What "idempotent" means here

For each of the 8 install modules, the second invocation has effects EQUAL to or a SUBSET of the first invocation. Specifically:

- **No-op cases:** If the file already has the canonical content, no write happens. The script reports "already present" or "already configured".
- **Additive cases:** If the file has partial content (some canonical entries already there), missing entries are added; existing entries are NOT touched.
- **Preservation cases:** User-edited content is detected and left alone. Reported back to the user as "user edits preserved" (or similar).

## File-by-file behavior

| File / target | First install | Re-install behavior |
|---|---|---|
| `CLAUDE.md` | Created with full template if absent. | NEVER overwritten. If `## Installation Policy` heading missing (case-insensitive), appended; otherwise no change. |
| `.super/config.json` | Created with `{}`. | NEVER overwritten. |
| `.gitignore` | Created or appended with `.super/cache/`, `.worktrees/`. | Dedup; existing user entries preserved; canonical entries added only if missing. |
| `.mcp.json` | Created with `{"mcpServers": {}}`. | NEVER overwritten. |
| `.claude/settings.json` -> `hooks.SessionStart` | Hook entry added. | Matched by command string; not duplicated. Other hooks preserved. |
| `.claude/settings.json` -> `permissions.ask` | `$defaults` + 20 install-approval rules. | `$defaults` preserved at index 0; new rules added if missing; user rules preserved. |
| `.claude/commands/super-*.md` (7) | Written from source. | Drift detection: body matches expected -> no-op; body differs but only frontmatter changed -> rewrite; body differs from expected (user edit) -> PRESERVE, report. |
| `.windsurf/workflows/super-*.md` (7) | Same as above. | Same drift detection. |
| `.clinerules/workflows/super-*.md` (7) | Same. | Same. |
| `.windsurf/rules/super-model.md` | Written from canonical body. | Body kept in sync with source on every run (the always-on rule is a Super-Model artifact, not a user-owned file). |
| `.clinerules/super-model.md` | Same. | Same. |

## Drift detection heuristic

Per `_detect_user_edits` in `super-mode-setup.py`:

```
body = text.split('---', 2)[2].strip()  # body past frontmatter

if body_existing != body_expected:
    user has edited the body; preserve.
```

The frontmatter `description:` is allowed to update without flagging - Super-Model may ship description updates between releases.

## What's NOT idempotent

Two cases by design:

1. **Always-on rule files** (`.windsurf/rules/super-model.md`, `.clinerules/super-model.md`) are rewritten on every run. They're Super-Model property; the user should not edit them. If they do, the edit is replaced on next install.

2. **First-install side effects on `.gitignore`.** If the project does not have a `.gitignore` at all, one is created. Subsequent runs are idempotent against the created file. This is a one-shot "first install" effect, not a continuous one.

## Verification

The `tests/foundation/test_super_mode_setup_script.py` and `test_super_mode_setup_security_hardening.py` suites assert these behaviors with concrete fixtures:

- Pre-existing CLAUDE.md with user content is preserved.
- Pre-existing `.super/config.json` is not overwritten.
- Pre-existing `permissions.ask` entries (including `$defaults` and user rules) are preserved with dedup.
- User-edited slash command bodies are preserved on re-run.
- Settings.json merge does not remove existing hooks or permissions entries.

## Why this matters

Without idempotency, every `super-mode-setup` invocation would be a destructive event the user has to think about. With idempotency, it's a no-op safety net - run it whenever you want to refresh the Super-Model surface, with zero risk to your edits.
