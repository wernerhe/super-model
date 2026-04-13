---
name: audit-evaluation
description: Run a quick audit of the just-written design doc against the verbal design from Gate #1. Flag drift, lost detail, contradictions. Catches "the doc says something different than what we agreed verbally."
---

# audit-evaluation

## What it does

Compares:

- The verbal sketch from `design-presentation` (in the chat).
- The committed design doc from `write-design-doc`.

Looks for:

- **Lost detail:** the verbal had specific commitments that the doc skipped.
- **Drift:** the doc made different decisions than the verbal.
- **Internal contradictions:** one section of the doc says X, another says NOT X.
- **Handwaving:** a phrase like "we'll figure that out later" where the verbal had a specific plan.

## Output

A short findings list. If empty -> proceed to implementation-plan-review. If non-empty -> present to user; decide per finding whether to revise the doc or accept the deviation.

## Why this matters

Writing-up always loses some information. A quick audit-while-still-warm catches the lossy parts before they become tomorrow's "I thought we decided X" confusion.

## Idempotency

Read-only audit. The doc revision (if needed) is a separate destructive action handled by re-running write-design-doc.
