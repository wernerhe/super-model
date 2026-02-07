# Security Policy

## Reporting a vulnerability

Open a GitHub Security Advisory on this repository, or email `hwerner2014@gmail.com` with the subject line `[super-model security]`.

Please do not file public GitHub issues for security concerns. Coordinated disclosure preferred.

## Threat model summary

Super-Model is a per-project skills library that does not bundle MCP server code, does not maintain user-level state beyond a single opaque 32-byte secret, and validates every JSON file (config, cache marker, plugin manifest) against a schema on load.

Key invariants:

- Atomic JSON writes with file locking (no torn config files under concurrent writers).
- HMAC-signed cache markers (tampered or hand-edited markers are treated as missing, not trusted).
- Cache filename sanitization (strict allowlist; Windows reserved-name rejection).
- SessionStart hook verifies canonical path and rejects oversized SKILL.md files.
- Install-approval policy adds 20 canonical Bash patterns to `permissions.ask` for package-manager commands.

Detailed architectural notes arrive in `docs/architecture/` and `docs/security/`.
