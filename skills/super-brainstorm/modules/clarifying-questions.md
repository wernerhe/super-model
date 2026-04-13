---
name: clarifying-questions
description: Ask one focused multi-choice question at a time to narrow scope and surface hidden requirements. Continues until the design has enough constraints to draft. Each question MUST include a "What do you think Claude" escape hatch when no clear recommendation exists.
---

# clarifying-questions

## What it does

Iterates a one-question-at-a-time clarification loop:

1. Read the user's initial description + approach profile.
2. Identify the highest-leverage unanswered question (the one whose answer constrains the most downstream decisions).
3. Ask it as a multi-choice with 3-5 options.
4. Wait for the answer.
5. If meaningful uncertainty remains, go back to step 2.
6. When the design space is well-constrained, stop and proceed to next module.

## UX rules

- **One question at a time.** Multiple-choice preferred over open-ended.
- **"What do you think Claude" escape hatch.** When no option has a clear recommendation, include a literal `What do you think Claude` option that makes the model think out loud, propose its pick, and confirm before proceeding.
- **Stop when constraint-rich.** Do not over-clarify trivial points to delay the design.

## When to stop

- The user can describe in one paragraph what the working version would look like.
- The user can list the 3-5 acceptance criteria.
- No remaining ambiguity blocks design choices.

## Idempotency

Loop of bounded iterations. Each iteration is a single Q+A exchange.
