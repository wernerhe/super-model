# Changelog

All notable changes to Super-Model are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## Unreleased

### Added

- Polyglot SessionStart hook: `hooks/run-hook.cmd` is the SAME file valid on Windows AND Unix.
- Hardened `hooks/session-start` bash body: canonical-path verification, 32 KiB size cap, pure-bash JSON escaping, per-platform output safety.

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
