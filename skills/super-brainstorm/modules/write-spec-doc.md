---
name: write-spec-doc
description: After Gate #2 (design approved), write the detailed spec to docs/specs/<topic>.md. The spec is the contract between design (what / why) and implementation (how). Specific behaviors, signatures, error conditions, edge cases.
---

# write-spec-doc

## What it does

Composes the detailed spec building on the approved design. Sections:

- **Behavior contract:** for each touch-point (function, endpoint, schema), the exact input/output shape and error conditions.
- **Edge cases:** empty input, malformed input, partial failure, retries.
- **Invariants:** what must always be true regardless of inputs.
- **Performance budget:** if relevant, the expected latency / throughput / memory.
- **Test plan:** which tests will be written, what they assert.

Writes to `docs/specs/<topic>.md`. Commits as `Add spec: <topic>`.

## Format

Markdown. ≥ 200 lines for non-trivial specs. Cross-reference back to the design doc with `See docs/design/<topic>.md`.

## Why spec is separate from design

Design is "what and why"; spec is "how, exactly". Keeping them separate lets the user approve them at different granularities. The spec is the artifact that the implementation plan directly consumes; the design is the higher-level rationale.

## Idempotency

If the spec already exists, ASK before overwriting. Iteration produces a new commit, not a silent rewrite.
