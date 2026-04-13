---
name: implementation-plan-review
description: Sketch the implementation plan structure (step count, ordering, dependency graph) BEFORE writing it. Lets the user see the plan shape and challenge it cheaply before the formal write-implementation-plan module commits to specific text.
---

# implementation-plan-review

## What it does

A preview of what the implementation plan will look like, BEFORE writing it as a file. The model presents:

- **Estimated step count.**
- **High-level grouping** of steps into phases.
- **Critical-path analysis:** which steps must serialize, which can parallelize.
- **Risk-weighted ordering:** typically risky steps first (catch problems early), safe polish last.

The user can challenge:

- "Can step 4 happen before step 3?"
- "Do we really need steps 7-9, or can they be one combined step?"
- "I think step 10 should be split."

## Why preview before write

A written plan is a specific commitment. The preview lets the user reshape the plan at the structural level before any specific text is committed. Cheaper iteration.

## Output

The user's approval of the plan shape, ready to be written by `write-implementation-plan` (after Gates #2 and #3).

## Idempotency

Read-only preview + iterate. No files written.
