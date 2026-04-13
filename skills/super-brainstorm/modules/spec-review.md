---
name: spec-review
description: Review the just-written spec for placeholder text, contradictions, and coverage gaps. Catches TODO / fill-in-later sections, behaviors specified in one section that contradict another, and edge cases the user mentioned but the spec missed.
---

# spec-review

## What it does

Sweeps the committed spec for:

- **Placeholder text:** `TODO`, `TBD`, `???`, `<fill in>`. The spec is a contract; placeholders are unsigned blanks.
- **Internal contradictions:** section A says input must be > 0; section B says it can be zero. Surface and reconcile.
- **Coverage gaps vs design:** every design-doc bullet should be reflected in the spec. If a design promise has no spec backing, flag.
- **Test plan completeness:** every behavior in the spec needs at least one test in the test plan.

## Output

A short findings list. If empty -> proceed to user-approves-spec. If non-empty -> present and decide per finding (revise spec, accept gap with annotation, or push the gap to a future spec).

## Why this exists

Specs decay between the "let's draft this" and "let's commit this" cycles. A sweep catches the parts that didn't survive the editing pass. Cheap to run; expensive to skip.

## Idempotency

Read-only review. Revisions go through write-spec-doc.
