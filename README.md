# Super-Model

**Per-project agentic skills library for AI coding IDEs** - Claude Code, Cursor, Windsurf, and VS Code + Cline.

Forked from [`obra/superpowers`](https://github.com/obra/superpowers) v3.4.1 and rebuilt around a per-project distribution model. Each project gets its own self-contained `<project>/Super-Model/` directory. No user-level state. Nothing leaks across projects.

---

## What is Super-Model

A library of 15 skills that an AI coding agent can invoke to do real work:

- 8 top-level skills exposed as `/super-*` slash commands (brainstorm, code review, prepare branch, delete branch, mode setup, visual debug, MCP builder, plus the chain-fired execute).
- 7 supporting helper / always-on skills (using-super-model, writing-skills, TDD, systematic-debugging, etc.) that the top-levels compose.
- A polyglot SessionStart hook that injects the always-on policy into every Claude Code conversation.
- A Python foundation (`super_lib`) for atomic writes, HMAC-signed cache markers, config cascade, and module loading.
- A `super-mode-setup.py` install script that turns any project into a Super-Model-equipped project in one command.

---

## Quickstart

Drop Super-Model into a project and run setup:

```sh
cd /path/to/my-project
git clone https://github.com/<your-fork>/super-model.git Super-Model
python Super-Model/super-mode-setup.py
```

Setup is idempotent. Re-running picks up new skills, new install-approval rules, or new slash commands without clobbering your edits.

After setup, restart your IDE. The 7 slash commands appear:

- `/super-brainstorm` - design + spec + plan workflow before any code is written
- `/super-code-review` - comprehensive review at a milestone (writes an HMAC-signed verdict cache)
- `/super-prepare-branch` - merge-readiness gate (reads the cache; chain-fires review if missing)
- `/super-delete-branch` - safety-checked branch deletion (value-check before any `-D`)
- `/super-mode-setup` - re-run install (idempotent)
- `/super-visual-debug` - visual fix/improve loop with capability memory between iterations
- `/super-mcp-builder` - discover, install, alter, or build MCP servers for the project

`/super-execute` is chain-fired only from `/super-brainstorm` so the hard approval gates cannot be bypassed.

---

## Layout

```
Super-Model/
- .claude-plugin/           plugin + marketplace manifests
- commands/                 7 slash-command shim files
- docs/architecture/        architecture notes (config cascade, hook points, cache markers, ...)
- hooks/                    SessionStart hook + polyglot run-hook.cmd wrapper
- schemas/                  JSON Schemas for config, module frontmatter, cache markers
- scripts/super_lib/        Python helpers (_io, _hmac, cache, config, modules)
- skills/                   15 skills (8 super-* top-level + 7 helpers / always-on)
- tests/foundation/         17 foundation tests (104 assertions)
- super-mode-setup.py       install script (Python 3.11+, 3.6-compat version guard)
- super-mode-setup.bat      Windows wrapper
- super-mode-setup.sh       POSIX wrapper
```

---

## Philosophy

### Per-project, not per-user

Most skill libraries live in `~/.config/something/`. Super-Model lives in `<project>/Super-Model/`. The tradeoff:

- **Pro:** every project pins its own version. A repo that worked yesterday works the same way next year, regardless of what's in your home directory.
- **Pro:** sharing a project means sharing the full toolchain.
- **Pro:** experimenting in one project never breaks another.
- **Con:** more disk usage if you have many projects.

This is a deliberate choice for reproducibility. See `docs/architecture/config-cascade.md`.

### Three hard approval gates in brainstorm

`super-brainstorm` enforces three gates before any code is written:

1. **Verbal design approval** in chat (before the design doc is committed).
2. **Written approval of the committed design doc.**
3. **Written approval of the committed spec doc.**

Only then does the plan get written and chain-fire `super-execute`. Skipping any gate is explicitly forbidden. See the `<HARD-GATE>` block in `skills/super-brainstorm/SKILL.md`.

### HMAC-signed caches with conservative degradation

`super-code-review` writes a verdict cache marker. `super-prepare-branch` reads it. The marker is HMAC-signed with a per-user secret at `~/.super-model/cache-secret.bin`. If the HMAC mismatches for any reason (file edited, key changed, copied across users), the read returns `None` and the consumer falls back to re-running the underlying check. Tampering is never silently trusted. See `docs/architecture/cache-markers.md`.

### Idempotent install

Every step of `super-mode-setup.py` is idempotent. Re-running produces no diffs unless the source ships new content. User edits to `CLAUDE.md`, `.super/config.json`, and the slash command bodies are preserved. See `docs/architecture/idempotency-model.md`.

---

## Architecture deep dives

- [`docs/architecture/config-cascade.md`](docs/architecture/config-cascade.md) - global / project layering + load-time validation.
- [`docs/architecture/hook-points.md`](docs/architecture/hook-points.md) - `super-execute` backend + policy composition.
- [`docs/architecture/cache-markers.md`](docs/architecture/cache-markers.md) - HMAC-signed cache integrity model.
- [`docs/architecture/idempotency-model.md`](docs/architecture/idempotency-model.md) - install script preservation guarantees.
- [`docs/architecture/super-execute-backends.md`](docs/architecture/super-execute-backends.md) - backend trade-offs (inline-batch vs subagent vs parallel-dispatch).

---

## Development

Set up a dev environment:

```sh
python -m venv .venv
.venv\Scripts\activate                # Windows
source .venv/bin/activate             # POSIX
pip install -r requirements-dev.txt
pytest tests/foundation/ -v
```

The full foundation suite is 104 assertions across 17 test files. All must pass for release.

---

## License

MIT - see `LICENSE`.

---

## Lineage

Forked from [`obra/superpowers`](https://github.com/obra/superpowers) v3.4.1. The upstream skill bodies that survived (TDD, systematic-debugging, writing-skills, using-git-worktrees, verification-before-completion, receiving-code-review) are kept in spirit with targeted edits for Super-Model's per-project namespace. The 8 top-level `super-*` skills, the polyglot hook wrapper, the `super_lib` Python foundation, and the install script are Super-Model originals. See `CHANGELOG.md` for the phase-by-phase rewrite history.
