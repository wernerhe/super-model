---
name: design-presentation
description: First hard approval gate. Walk the user through the high-level design verbally in chat. Wait for explicit "OK proceed" before writing any document. The gate exists to catch design errors at the cheapest possible point - before anything is committed.
---

# design-presentation

## What it does

The first hard gate. The model presents the design verbally in the chat:

- **Problem statement:** one paragraph the user agrees describes the problem.
- **Solution sketch:** the proposed approach in ~5-8 bullets.
- **Key tradeoffs:** what's being chosen over what; why.
- **Non-goals:** what is explicitly out of scope.
- **Risks:** the top 2-3 things that could go wrong.

Then asks: "Does this design match what you want? (yes / no / let's iterate)"

If yes -> proceed.
If no -> back to clarifying-questions or revise the design.
If iterate -> revise and re-present.

## Why verbal first

A committed design doc is harder to revise than a chat-paragraph. Catching mismatches before commit means cheaper iteration. The verbal presentation also forces the model to articulate the design in its own words - exposing handwaving.

## Hard rule

Do NOT skip this gate. Do NOT collapse it into write-design-doc as a "save time" optimization. The verbal presentation surfaces problems that disappear into the prose when you write the doc.

## Output

The user's explicit approval (recorded in chat history) plus the design sketch ready to be written up.

## Idempotency

Iterate-and-confirm. Each iteration re-presents the (possibly revised) design.
