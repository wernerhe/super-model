# Hook points: super-execute composition model

`super-execute` does NOT have a monolithic implementation. It has a fixed per-step lifecycle and lets backends + policies plug in at four hook points. This means a user can swap the execution backend without losing TDD enforcement, and vice versa.

## The 4 hook points

Per plan step:

```
pre-step-check  ->  per-step-execute  ->  post-step-check  ->  post-batch-complete
```

| Hook | Type | Who plugs in |
|---|---|---|
| `pre-step-check` | multi-consumer | Policies (e.g., `policy-tdd-enforcement`) - any can VETO the step. |
| `per-step-execute` | single-provider | The chosen backend (`backend-inline-batch`, `backend-subagent-driven`, or `backend-parallel-dispatch`). |
| `post-step-check` | multi-consumer | Policies (e.g., `policy-design-fidelity`) - verify the step output. |
| `post-batch-complete` | multi-consumer (periodic) | Policies (e.g., `policy-code-review-checkpoints`) at configured batch boundaries. |

## Why single-provider for execute

Exactly one backend can produce the per-step output. Allowing two backends would mean the step is committed twice with different content - incoherent. The single-provider constraint is enforced at manifest-load time.

## Why multi-consumer for the others

Policies are orthogonal concerns. TDD enforcement, design fidelity, and code-review checkpoints all want to inspect each step. They don't conflict because:

- `pre-step-check` consumers each return `proceed` or `veto`. The step proceeds only if ALL consumers say `proceed`.
- `post-step-check` consumers each emit findings. The orchestrator aggregates.
- `post-batch-complete` consumers each may trigger side effects (e.g., fire `super-code-review`). The orchestrator runs them in declared order.

## Declaration in module frontmatter

Backends declare what they provide; policies declare what they consume:

```yaml
# backend-inline-batch.md
---
name: backend-inline-batch
hooks_provided:
  - per-step-execute
---
```

```yaml
# policy-tdd-enforcement.md
---
name: policy-tdd-enforcement
hooks_consumed:
  pre-step-check: tdd_pre_check
  post-step-check: tdd_post_check
---
```

The `hooks_consumed` value maps each hook to a callable / message handler name.

## Validation at manifest load

`super_lib.modules` checks at load time:

- Exactly one module provides `per-step-execute` (single-provider hook).
- Any other hooks have zero or more providers (multi-consumer).
- Every `hooks_consumed` entry references a known hook name (no typos).

A manifest that violates these rules fails to load with a clear error - never silently runs with the wrong policy set.

## Why this matters

A pre-composition implementation would have to either:

- Hard-code the TDD check inside each backend (duplication), OR
- Have backends call a shared "policy checker" function (tight coupling, hard to extend).

The hook-point model lets a new policy (say, `policy-cost-tracking`) be added as a new module file with no changes to the backends. The orchestrator discovers it through the manifest.
