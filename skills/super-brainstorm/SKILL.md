---
name: super-brainstorm
description: Turn an idea into a committed design, written spec, and implementation plan via a 14-module flow with 3 hard approval gates. Chain-fires super-execute at the end to implement the plan. The headline skill of Super-Model.
---

# super-brainstorm

The flagship skill. Designed to be the FIRST thing the user runs for any non-trivial work. Turns rough ideas into shipped code via a calibrated design -> spec -> plan -> execute flow with three hard approval gates.

<HARD-GATE>
Do NOT invoke any implementation skill, write any code, scaffold any
project, or take any implementation action until you have presented a
design and the user has approved both the design AND the written spec.
This applies to EVERY project regardless of perceived simplicity.
</HARD-GATE>

## When to use

- The user describes a new feature, bug fix, or refactor in informal terms.
- A `/super-brainstorm` slash command was invoked.
- ANY non-trivial work request. If you find yourself thinking "this is too simple to need brainstorm," that thought IS the failure mode the hard gate exists to prevent.

## The 14 modules + 3 gates

| # | Module | TodoWrite label | Gate |
|---|---|---|---|
| 1 | `approach-profile` | Design | |
| 2 | `clarifying-questions` | Design | |
| 3 | `mcp-tool-config` (conditional) | Design | |
| 4 | `autonomous-mode-config` (conditional) | Design | |
| 5 | `design-presentation` | Design | **GATE #1** verbal |
| 6 | `write-design-doc` | Design Review | |
| 7 | `audit-evaluation` | Design Review | |
| 8 | `implementation-plan-review` | Design Review | |
| 9 | `user-approves-design` | Design Review | **GATE #2** written |
| 10 | `write-spec-doc` | Spec Review | |
| 11 | `spec-review` | Spec Review | |
| 12 | `user-approves-spec` | Spec Review | **GATE #3** written |
| 13 | `write-implementation-plan` | Plan | |
| 14 | `execute-implementation-plan` | Execute | chains -> `super-execute` |

The TodoWrite labels collapse 14 internal modules into 5 user-facing checkpoints. Internal kebab-case identifiers MUST NOT appear in the user-facing todo list.

## The 3 hard approval gates

- **Gate #1 - design-presentation (verbal):** walk the user through the high-level design in chat; wait for "OK proceed" before writing any document.
- **Gate #2 - user-approves-design (written):** wait for written approval of the COMMITTED design doc before writing the spec.
- **Gate #3 - user-approves-spec (written):** wait for written approval of the COMMITTED detailed spec before writing the plan.

NOT 2 gates. NOT 4 gates. Three is calibrated.

## Conditional modules

`mcp-tool-config` and `autonomous-mode-config` are `enabled_by_default: false`. The full preset enables them, but each only runs if the chosen approach profile demands it (e.g., approach profile "MCP integration" enables mcp-tool-config).

## Presets

- `full` (default) - all 14 modules; suitable for any substantial work.
- `fast` - shorter modules; skips MCP / autonomous config; same 3 gates.
- `spec-only` - skips the design phase, jumps to spec writing; assumes the user already has a designed solution and just needs the formal write-up.

## UX rules

- **"One question at a time" during clarifying-questions.** Multiple-choice preferred over open-ended.
- **"What do you think Claude" escape hatch.** When a multi-choice question has no recommended option, include an extra option literally labeled `What do you think Claude`. Selecting it makes the model think out loud, propose its pick, and ask before proceeding.
- **NEVER expose internal kebab-case identifiers** in the user-facing todo list. Use the 5 TodoWrite labels.

## Output artifacts

- `docs/design/<topic>.md` - the high-level design doc.
- `docs/specs/<topic>.md` - the detailed spec.
- A plan file (path varies by project convention; default `docs/plans/<topic>.yaml`).
- A chain-fire into `super-execute` at module 14 that consumes the plan.

## Verify after running

- Three gates fired and were approved.
- Design doc, spec doc, plan file all committed to the repo.
- `super-execute` was chain-fired and completed (or stopped at a checkpoint).
- Final code-review verdict is READY-TO-MERGE (or NEEDS-FIXES with surfaced findings).
