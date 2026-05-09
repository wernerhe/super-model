# super-execute backends: trade-offs

`super-execute` ships three backends. Exactly one is active per plan invocation. The choice trades speed against context isolation against parallelism. This doc explains when to pick which.

## The three backends

| Backend | Module | Dispatch model |
|---|---|---|
| Inline-batch (default) | `backend-inline-batch` | Controller LLM executes each step itself. |
| Subagent-driven | `backend-subagent-driven` | Each step dispatched to a fresh subagent. |
| Parallel-dispatch | `backend-parallel-dispatch` | Independent steps dispatched in parallel. |

## Decision matrix

| Concern | Inline-batch | Subagent-driven | Parallel-dispatch |
|---|---|---|---|
| Speed (small plan) | Fastest | Slower (dispatch overhead) | Slower (dispatch overhead) |
| Speed (large independent plan) | Bottleneck on controller | Slow but isolated | **Fastest** |
| Context budget | Heavy (all steps in controller) | Light (per-step) | Light (per-step) |
| Isolation between steps | None | Strong | Strong |
| Step-to-step memory | Strong | None | None |
| Merge-conflict risk | Zero | Zero | Possible if steps overlap files |

## When to pick inline-batch (default)

- Plan is small (under ~10 steps).
- Steps build on each other in non-obvious ways (the controller's memory of earlier steps helps).
- Context budget is not a concern (e.g., short files, narrow scope).
- You want the fastest possible execution and don't need step isolation.

This is the default for a reason - most plans fit this profile.

## When to pick subagent-driven

- Step has high blast radius (touching infrastructure, security boundaries, critical paths).
- Step is large enough that loading all file contents into the controller would balloon context.
- Step is independent of prior steps (fresh subagent context is a feature, not a loss).
- You want the controller LLM to stay focused on orchestration without diving into implementation details.

The dispatch overhead is real but small compared to the cost of a controller losing focus on a 50-step plan.

## When to pick parallel-dispatch

- Plan has many mutually-independent steps (e.g., "add 5 unrelated REST endpoints" or "convert 10 components from JS to TS").
- Wall-clock time matters (overnight runs, time-critical deliverables).
- Steps touch disjoint file sets so concurrent commits don't conflict.
- You're willing to pay multiple subagent dispatch overheads for the speedup.

**Do NOT use parallel-dispatch when:**

- Steps have implicit ordering not captured in `dependencies` (parallel execution will get the wrong sequence).
- Steps share state in subtle ways (later step needs an artifact produced by earlier step).
- Plan is for security-sensitive code (parallel commits are harder to review chronologically).

## DAG scheduling (parallel-dispatch only)

Plans for parallel-dispatch must declare explicit dependencies:

```yaml
steps:
  - id: 1
    description: "Add User model"
    files: ["src/models/user.py"]
    dependencies: []
  - id: 2
    description: "Add Post model"
    files: ["src/models/post.py"]
    dependencies: []         # parallel with step 1
  - id: 3
    description: "Add User-Post relation"
    files: ["src/models/user.py", "src/models/post.py"]
    dependencies: [1, 2]     # waits for both
```

The scheduler:

1. Identifies runnable steps (all dependencies satisfied).
2. Dispatches them as a batch.
3. When any completes, recomputes runnable set.
4. Repeats until done or any step fails.

## Conflict handling

If two parallel subagents produce diffs that touch the same file at the same lines:

- The scheduler stops the second dispatch.
- Serializes: waits for the first to commit.
- Re-dispatches the second against the post-commit state.

This is rare in practice (the user should declare overlapping file sets as dependencies), but the scheduler handles it gracefully.

## Configuration

Choose the backend in `.super/config.json`:

```json
{
  "super-execute": {
    "backend": "parallel-dispatch"
  }
}
```

Or via the `super-execute` manifest's `subagent` preset:

```
super-execute --preset subagent
```

The default preset uses `backend-inline-batch`.

## Policy independence

All three backends compose with all three policies (`policy-tdd-enforcement`, `policy-code-review-checkpoints`, `policy-design-fidelity`). The hook-point model means a switch from inline-batch to parallel-dispatch loses no TDD discipline. See `docs/architecture/hook-points.md`.
