---
name: fix-proposal
description: Given the initial capture and the user's stated intent, propose ONE specific code change. Never batch multiple fix attempts; one change per loop iteration.
---

# fix-proposal

## What it does

Synthesizes:

- The user's stated intent ("the chart axis labels are clipped", "this button color is wrong", etc.).
- The initial-capture output (or the previous iteration's captures).
- Code context (the file/files that produce the visual target).

Produces ONE specific code-change proposal with:

- File path + line range.
- Exact before / after diff.
- A predicted visual outcome.

## Hard rule: one change per iteration

NEVER bundle multiple fix attempts into a single iteration. Bundled fixes mean you cannot tell which change produced which visual effect - and worse, you cannot easily undo just the change that caused a regression.

## Output

A structured proposal:

```json
{
  "file": "src/components/Chart.tsx",
  "line_range": "42-44",
  "diff": "-  fontSize: 10\n+  fontSize: 12",
  "expected_outcome": "axis labels increase in size; no clipping at desktop viewport."
}
```

## Idempotency

Read-only proposal. No code change applied at this step.
