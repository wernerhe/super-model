# Changelog

All notable changes to Super-Model are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## Unreleased

### Added

- 3 JSON Schema files at `schemas/`: `config.schema.json`, `module-frontmatter.schema.json`, `cache-marker.schema.json`.

### Changed

- Forked from `obra/superpowers` v3.4.1; restructured around a per-project distribution model.
- Renamed `lib/` to `scripts/`; new package home at `scripts/super_lib/`.
- Rebranded `.claude-plugin/plugin.json` and `marketplace.json` to the Super-Model namespace.
- Top-level slash commands prefixed `super-*` to avoid collision with the upstream plugin.

### Removed

- User-level installer (`lib/initialize-skills.sh`) - per-project install only.
- Codex-specific bootstrap (`.codex/`) - Super-Model targets Claude Code, Windsurf, and Cline (VS Code).
