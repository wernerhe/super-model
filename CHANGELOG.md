# Changelog

All notable changes to Super-Model are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

No changes yet.

---

## [2.0.0] - 2026-05-23

The first Super-Model release. Forked from `obra/superpowers` v3.4.1 and rebuilt across 14 phases.

### Added

- 8 top-level `super-*` skills:
  - `super-brainstorm` (14 modules; 3 hard approval gates: verbal design, written design, written spec; presets: full / fast / spec-only).
  - `super-code-review` (9 modules; HMAC-signed cache marker output).
  - `super-prepare-branch` (4 modules; reads the code-review cache marker; chain-fires review on miss).
  - `super-delete-branch` (4 modules; value-check before any `git branch -D`).
  - `super-mode-setup` (8 install modules; backs the install script).
  - `super-visual-debug` (6 modules; capability memory between iterations).
  - `super-mcp-builder` (4 modules; no MCP source ever vendored).
  - `super-execute` (8 modules; hook-point composition of 3 backends + 3 policies; chain-fired only from `super-brainstorm`).
- 7 supporting helper / always-on skills (`using-super-model`, `writing-skills`, `test-driven-development`, `systematic-debugging`, `receiving-code-review`, `using-git-worktrees`, `verification-before-completion`).
- 7 `super-*` slash command shims in `commands/`.
- 2 agent definitions in `agents/` (`code-reviewer`, `code-implementer`).
- Polyglot SessionStart hook (`hooks/run-hook.cmd` is the SAME file on Windows and Unix); hardened `hooks/session-start` (canonical-path verification, 32 KiB size cap, pure-bash JSON escaping).
- Python foundation in `scripts/super_lib/`:
  - `_io.atomic_write_json` (FileLock + fsync + 0o600 on POSIX).
  - `_hmac` (per-user secret at `~/.super-model/cache-secret.bin`).
  - `cache.read_marker` / `write_marker` (HMAC-signed; conservative degradation on tamper).
  - `config.resolve` (2-layer global + project cascade; fail-fast validation on load).
  - `modules.read_manifest` / `list_modules` / `parse_frontmatter`.
- 3 JSON schemas (`schemas/config.schema.json`, `module-frontmatter.schema.json`, `cache-marker.schema.json`).
- `super-mode-setup.py` install script (Python 3.11+ enforced; 3.6-compatible parse for the version guard) plus `.bat` / `.sh` wrappers.
- 17-test foundation suite (`tests/foundation/`) - 104 assertions; all pass on the supported matrix.
- 5 architecture deep dives in `docs/architecture/` (config cascade, hook points, cache markers, idempotency model, super-execute backends).
- CI: GitHub Actions matrix over {Ubuntu, Windows, macOS} x {Python 3.11, 3.12}; ruff lint + format; pre-commit config.

### Changed

- Distribution model: per-project (`<project>/Super-Model/`), not per-user. No user-level state.
- Top-level slash commands prefixed `super-*` to avoid collision with the upstream plugin.
- 20-rule install-approval policy merged into `<project>/.claude/settings.json` `permissions.ask`, with `$defaults` preserved at index 0.
- `code-reviewer` agent frontmatter description rewritten to be YAML-safe (the upstream description had embedded `<example>Context:` colon-space sequences that broke `yaml.safe_load`).

### Removed

- User-level skills installer (`lib/initialize-skills.sh`) - per-project install only.
- Codex-specific bootstrap (`.codex/`) - Super-Model targets Claude Code, Windsurf, and Cline (VS Code).
- Upstream skills not in the Super-Model catalog (brainstorming, condition-based-waiting, defense-in-depth, dispatching-parallel-agents, executing-plans, finishing-a-development-branch, requesting-code-review, root-cause-tracing, sharing-skills, subagent-driven-development, testing-anti-patterns, testing-skills-with-subagents, writing-plans, commands).

### Security

- HMAC-signed cache markers prevent forged verdicts from bypassing review gates. Tampered markers read as `None` (conservative degradation); consumers re-run the underlying check.
- Cache filename sanitization rejects null bytes, NTFS Alternate Data Streams, Windows reserved device names, path separators, Unicode look-alikes, oversized names, and dotfiles.
- Atomic-write discipline: FileLock + fsync + 0o600 on POSIX prevents partial writes from leaving observable corrupt state.
- Config validation on load (not just on write) fails fast with a clear error message including the offending file path and JSON-pointer location.
- 20 install-approval Bash patterns require user approval before any `pip install`, `npm install`, `apt install`, etc. - the policy survives across re-installs via additive merge with dedup.
- SessionStart hook hardening: canonical path verification, 32 KiB size cap, pure-bash JSON escaping, per-platform output safety.
