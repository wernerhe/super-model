---
name: project-type-detection
description: Detect the project's primary language / build system from manifest files (pyproject.toml, package.json, Cargo.toml, go.mod, etc.). Records findings for downstream modules; does not modify the project.
---

# project-type-detection

## What it does

Reads the target project root and looks for manifest files in priority order:

1. `pyproject.toml` -> Python (modern packaging)
2. `setup.py` / `setup.cfg` -> Python (legacy packaging)
3. `package.json` -> Node.js / TypeScript
4. `Cargo.toml` -> Rust
5. `go.mod` -> Go
6. `pom.xml` / `build.gradle` -> JVM
7. (fallback) -> unknown

Records the detected type for downstream modules (e.g., `mcp-wiring` may pick different MCPs based on project type).

## Why

Some setup decisions depend on language - e.g., a Python project benefits from a Python-aware code-review module configuration; a Node project benefits from npm-aware install-approval rules.

## Idempotency

Read-only. This module never modifies the project.
