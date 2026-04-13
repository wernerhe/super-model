---
name: dependency-health
description: Vet new dependencies added in the diff. Check for abandoned packages, lax version pinning, unusual licenses, or known-problematic supply-chain history.
---

# dependency-health

## What it does

For each new dependency added in `pyproject.toml` / `package.json` / `Cargo.toml`:

- **Last release date:** packages unmaintained for >2 years are flagged.
- **Version pinning:** unpinned (`*`) or wildcard major (`^x`) pins are flagged for libraries where breakage is common.
- **License:** non-permissive or unknown licenses are flagged.
- **Supply-chain history:** check against known typosquatting patterns and recent compromise alerts.
- **Maintainer count:** single-maintainer packages with high downstream impact get a "bus-factor" flag.

## Severity

- `important` for abandoned packages or non-permissive licenses in a permissive-license project.
- `minor` for lax pinning and bus-factor concerns.

## Fix policy

`suggest_only` - dependency choice is a project-level decision. The module surfaces facts; the human decides whether the tradeoff is acceptable.

## Idempotency

Read-only.
