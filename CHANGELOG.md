# Changelog

All notable changes to Super-Model are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## Unreleased

No changes yet.

## [0.4.0] - 2026-05-09

Documented + tested. Anyone scanning the repo can understand what it does and verify it works on their machine.

### Added

- 17-file foundation test suite at `tests/foundation/` (104 assertions; all pass on the supported matrix).
- `requirements-dev.txt` declaring pytest + filelock.
- `tests/foundation/conftest.py` with reusable `super_root` / `tmp_project` / `tmp_global_home` fixtures.
- README.md with quickstart, what-it-is, directory layout, distribution model rationale, and security model summary.
- 5 architecture deep dives in `docs/architecture/`:
  - `config-cascade.md` - 2-layer global + project cascade with fail-fast validation.
  - `hook-points.md` - SessionStart + slash command shim semantics.
  - `cache-markers.md` - HMAC-signed verdict markers + conservative-degradation model.
  - `idempotency-model.md` - install / re-install / drift detection.
  - `super-execute-backends.md` - hook-point composition of 3 backends x 3 policies.
- `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md` (governance baseline).

### Security

- Tests cover cache filename sanitization (null bytes, NTFS Alternate Data Streams, Windows reserved device names, path separators, Unicode look-alikes, oversized names, dotfiles).
- Tests cover atomic-write discipline (FileLock + fsync + 0o600 on POSIX).
- Tests cover HMAC-signed cache markers (forged markers read as `None`).

## [0.3.0] - 2026-04-18

First installable build. Any project can run `python super-model-setup.py <project>` and get a fully wired install.

### Added

- 7 `super-*` slash command shims in `commands/` (no `/super-execute` shim - chain-fired only from `/super-brainstorm`).
- `super-model-setup.py` install script (Python 3.11+ enforced; 3.6-compatible parse for the version guard).
- `super-model-setup.bat` and `super-model-setup.sh` wrappers for one-command install on Windows / POSIX.

### Changed

- Slash command shims also installed to `.windsurf/workflows/` and `.clinerules/workflows/` for Windsurf + Cline parity.

## [0.2.0] - 2026-04-12

Skills catalog complete. All 8 top-level skills present with manifests + modules; 7 helper / always-on skills support them.

### Added

- Polyglot SessionStart hook: `hooks/run-hook.cmd` is the SAME file valid on Windows AND Unix.
- Hardened `hooks/session-start` bash body: canonical-path verification, 32 KiB size cap, pure-bash JSON escaping, per-platform output safety.
- 7 helper / always-on skills: `using-super-model`, `writing-skills`, `test-driven-development`, `systematic-debugging`, `receiving-code-review`, `using-git-worktrees`, `verification-before-completion`.
- `using-super-model` as the always-on policy skill, auto-injected by the SessionStart hook.
- 8 top-level `super-*` skills:
  - `super-brainstorm` (14 modules; 3 hard approval gates: verbal design, written design, written spec; presets: full / fast / spec-only).
  - `super-code-review` (9 modules; HMAC-signed cache marker output).
  - `super-prepare-branch` (4 modules; reads the code-review cache marker; chain-fires review on miss).
  - `super-delete-branch` (4 modules; value-check before any `git branch -D`).
  - `super-model-setup` (8 install modules; backs the install script).
  - `super-visual-debug` (6 modules; capability memory between iterations).
  - `super-mcp-builder` (4 modules; no MCP source ever vendored).
  - `super-execute` (8 modules; hook-point composition of 3 backends + 3 policies; chain-fired only from `super-brainstorm`).
- 57 modules total across the 8 top-level skills.

## [0.1.0] - 2026-03-06

First tagged pre-release. Library foundation in place: atomic I/O, HMAC, cache markers, config cascade, module loader.

### Added

- 3 JSON Schema files at `schemas/`: `config.schema.json`, `module-frontmatter.schema.json`, `cache-marker.schema.json`.
- Python package `super_lib` at `scripts/super_lib/`:
  - `_io.atomic_write_json` (FileLock + fsync + 0o600 on POSIX).
  - `_hmac` (per-user secret at `~/.super-model/cache-secret.bin`).
  - `cache.read_marker` / `write_marker` (HMAC-signed; conservative degradation on tamper).
  - `config.resolve` (2-layer global + project cascade; fail-fast validation on load).
  - `modules.read_manifest` / `list_modules` / `parse_frontmatter`.
- `pyproject.toml` declares the package; `pip install -e .` works.

### Changed

- Forked from `obra/superpowers` v3.4.1; restructured around a per-project distribution model.
- Renamed `lib/` to `scripts/`; new package home at `scripts/super_lib/`.
- Rebranded `.claude-plugin/plugin.json` and `marketplace.json` to the Super-Model namespace.
- Top-level slash commands prefixed `super-*` to avoid collision with the upstream plugin.

### Removed

- User-level installer (`lib/initialize-skills.sh`) - per-project install only.
- Codex-specific bootstrap (`.codex/`) - Super-Model targets Claude Code, Windsurf, and Cline (VS Code).
