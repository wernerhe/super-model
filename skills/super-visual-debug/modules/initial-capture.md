---
name: initial-capture
description: Capture the current state of the visual target from multiple angles (desktop / mobile viewports, isolation vs context) before any fix is applied. Stores captures for the compare-iterations step.
---

# initial-capture

## What it does

Captures the visual target's current state using the best available tool from `capability-probe`. Multi-angle by default:

- Desktop viewport (1440x900).
- Mobile viewport (375x667).
- Component in isolation (if the bug is local).
- Component in context (if the bug is about interaction).

Stores the captures under a temp directory keyed by the iteration index (`iter-0/`).

## Why multi-angle

A single-viewport capture misses layout bugs that only manifest at specific sizes. A single-state capture misses interaction bugs. The default 4-angle suite catches ~80% of regressions without being heavy.

## Output

A list of (angle, file-path) tuples consumed by `compare-iterations`.

## Idempotency

Captures are temporary and keyed by iteration index. Re-running with the same iteration index would overwrite, but the loop driver always increments index.
