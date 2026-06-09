# Claude-deployment model / effort / Ultracode policy

Super-Model runs under several AI coding IDEs (Claude Code, Cursor, Windsurf).
This document records a **Claude-only** policy: when a Claude Code deployment runs
the Super-Model workflow, `super-brainstorm` should run on the most current Opus at
the highest persistent reasoning effort, and `super-execute` should prefer
multi-agent execution (Ultracode / a parallel backend). The policy is owned by
Super-Model because it governs Super-Model's own skills; it is intentionally
scoped to Claude Code and does not touch Cursor or Windsurf.

## Why Claude-only

The horsepower knobs in question — the `model` alias, the `effortLevel` setting,
and the Ultracode session mode — are Claude Code constructs. They are meaningless
on other deployments. A Cursor session that also exports `CLAUDE_PLUGIN_ROOT` must
**not** trigger the policy, so the deployment classifier checks `CURSOR_PLUGIN_ROOT`
first (matching the SessionStart hook ordering).

## What is enforceable, and how

The policy is delivered through three mechanisms of decreasing strength. The split
is deliberate and honest — Super-Model does not claim to *force* Opus, xhigh, or
Ultracode.

1. **Configured (persistent).** `super-model-setup` seeds
   `.claude/settings.json` with `model: "opus"` and `effortLevel: "xhigh"`,
   **absent-only** (an architect-set value is preserved). These are the verified
   Claude Code keys (code.claude.com/docs model-config): the `opus` alias tracks
   the current Opus release, and `xhigh` is the highest *persistent* effort —
   `max` and `ultracode` are session-only and cannot be written to settings. The
   seed lives in Claude's own config file, so it runs as part of Claude Code setup
   regardless of which IDE invoked setup.

2. **LLM-followed (runtime).** `super-execute` reads
   `config.deployment_preferences("super-execute")` on a Claude deployment and is
   instructed to: prefer the configured backend (default `parallel-dispatch`)
   above a small-plan threshold; dispatch the implementer/reviewer subagents with
   `implementer_model` (default `opus`) rather than their hardcoded `model:
   sonnet`; and keep small plans on the inline backend to avoid wasted fan-out.
   `super-brainstorm` reads `config.deployment_preferences("super-brainstorm")`
   and surfaces a preflight nudge when the live model/effort is below target.

3. **Advisory (session-only).** Ultracode cannot be pinned anywhere. When it is
   off at execute time, `super-execute` surfaces a single line recommending
   `/effort ultracode`, then proceeds regardless.

## Where the pieces live

- `scripts/super_lib/deployment.py` — `detect_deployment` / `is_claude_code`, the
  single source of truth for the env-signal classification.
- `super-model-setup.py` — `_install_claude_model_effort`, the absent-only seed.
- `schemas/config.schema.json` — the `deployment_preferences` block
  (`claude-code` / `cursor` / `windsurf` → `{model, effort, backend,
  implementer_model}`), `additionalProperties: false`.
- `scripts/super_lib/config.py` — `deployment_preferences(skill_name, ...)`,
  resolving Layer-1 baked Claude defaults merged with project/global overrides and
  returning `{}` for non-Claude deployments.
- `skills/super-brainstorm/modules/approach-profile.md` — the preflight nudge.
- `skills/super-execute/SKILL.md` — the deployment-specific backend / model /
  Ultracode behavior.

## Overriding the defaults

The baked Claude defaults are Layer-1; a project (or the global config) overrides
them through the `deployment_preferences.claude-code` block in
`.super/config.json`. For example, to keep Sonnet for implementation on Claude:

```json
{
  "super-execute": {
    "deployment_preferences": { "claude-code": { "implementer_model": "sonnet" } }
  }
}
```

## Relationship to spyglass

This policy is the Super-Model half of a two-repo build. The spyglass half
(`barrow-systems/spyglass`) makes `spyglass bootstrap` render AI-assistant rule
files per tool. The two were kept separate on purpose: spyglass owns the portable
guardrails/persona it emits into every project, and Super-Model owns the
Claude-deployment horsepower policy that governs its own `super-brainstorm` /
`super-execute` workflow. Neither tool writes the other's content, which keeps a
single owner for each rule and avoids two writers fighting over `CLAUDE.md`.
