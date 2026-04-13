---
name: write-implementation-plan
description: After Gate #3 (spec approved), write the implementation plan file consumed by super-execute. The plan is a structured step list with file targets, test targets, dependencies, and any policy overrides. Default location docs/plans/<topic>.yaml.
---

# write-implementation-plan

## What it does

Composes the implementation plan from the approved spec + the implementation-plan-review preview:

```yaml
plan_id: "<topic>-2026-MM-DD"
design_ref: "docs/design/<topic>.md"
spec_ref: "docs/specs/<topic>.md"
backend: "inline-batch"   # or subagent-driven / parallel-dispatch
policies:
  tdd-enforcement: enabled
  code-review-checkpoints:
    enabled: true
    batch_size: 5
  design-fidelity: enabled
steps:
  - id: 1
    description: "..."
    files: ["..."]
    tests: ["..."]
    dependencies: []
  - id: 2
    ...
```

## Format

YAML for human-readability + tool-readability. JSON is acceptable if the project's tooling prefers it.

## Idempotency

Single-file write. If a plan with the same `plan_id` exists, ASK before overwriting.

## Output

The plan file path, ready to be passed to `super-execute` at the next module.
