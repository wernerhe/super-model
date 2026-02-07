# Super-Model

Per-project agentic skills library for AI coding IDEs (Claude Code, Cursor, Windsurf, VS Code + Cline).

Forked from [`obra/superpowers`](https://github.com/obra/superpowers) v3.4.1 and rebuilt around a per-project distribution model — each project gets its own self-contained `<project>/Super-Model/` directory, no user-level state, nothing leaks across projects.

## Status

**Work in progress.** Restructure landed; later phases add the `super_lib` Python helpers, the 8 top-level `super-*` skills, the polyglot session-start hook, and the `super-mode-setup.py` install script. Target version: `v2.0.0`.

See `CHANGELOG.md` for the current state.

## Layout

```
Super-Model/
├─ .claude-plugin/          ← plugin + marketplace manifests
├─ agents/                  ← subagent type declarations
├─ docs/                    ← architecture + spec + windows notes
├─ hooks/                   ← SessionStart hook + polyglot wrapper
├─ schemas/                 ← JSON Schemas (config, frontmatter, cache marker)
├─ scripts/super_lib/       ← Python helpers (atomic writes, HMAC, cache, config, modules)
├─ skills/                  ← 15 skills total (8 super-* top-level + 5 helpers + 2 always-on policies)
└─ tests/foundation/        ← 17 foundation tests
```

## License

MIT — see `LICENSE`.
