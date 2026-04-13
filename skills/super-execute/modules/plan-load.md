---
name: plan-load
description: Read and validate the implementation plan file produced by super-brainstorm. Confirms the plan_id, design_ref, spec_ref, and the steps list have the expected shape before any execution begins.
---

# plan-load

## What it does

1. Receives the plan file path (argument from the chain-fire).
2. Reads and parses the YAML / JSON plan file.
3. Validates:
   - `plan_id` present and matches kebab-case.
   - `design_ref` and `spec_ref` paths exist on disk.
   - `steps` is a non-empty list with each step having `id`, `description`, `files`, optional `tests`.
4. Loads referenced design and spec into the controller's context so subsequent modules can consult them.

## Why validation up front

Catching a malformed plan at load time prevents partial execution (some steps committed, then a parser error). The plan is either fully loadable or the skill refuses to start.

## Idempotency

Read-only.
