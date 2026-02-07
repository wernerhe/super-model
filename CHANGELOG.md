# Changelog

All notable changes to Super-Model are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Changed

- Forked from `obra/superpowers` v3.4.1; restructuring around a per-project distribution model.
- Top-level slash commands will be prefixed `super-*` to avoid namespace collision with the upstream plugin.

### Removed

- User-level skills installer (`lib/initialize-skills.sh`) — Super-Model uses per-project install only.
- Codex-specific bootstrap (`.codex/`) — Super-Model targets Claude Code, Windsurf, and Cline (VS Code).
- Upstream skills not in the Super-Model catalog (brainstorming, condition-based-waiting, defense-in-depth, dispatching-parallel-agents, executing-plans, finishing-a-development-branch, requesting-code-review, root-cause-tracing, sharing-skills, subagent-driven-development, testing-anti-patterns, testing-skills-with-subagents, writing-plans, commands).
