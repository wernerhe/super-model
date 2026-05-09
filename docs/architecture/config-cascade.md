# Config cascade

Super-Model resolves configuration through a 2-layer cascade: a global layer at `~/.super-model/config.json` and a per-project layer at `<project>/.super/config.json`. The project layer overrides the global layer; nested dicts merge key-by-key.

## Resolution algorithm

`super_lib.config.resolve(skill_name, project_root=...)` is the public surface. It:

1. Loads the global config from `~/.super-model/config.json` (or `{}` if absent).
2. Validates the global config against `schemas/config.schema.json`. **Invalid configs raise at load time**, not at field access. The error message includes the file path and the JSON-pointer location of the failure.
3. Loads the project config from `<project_root>/.super/config.json` (or `{}` if absent).
4. Validates the project config (same fail-fast semantics).
5. Deep-merges global -> project (project wins on conflicts; nested dicts merge per-key; non-dict values replace wholesale).
6. Returns the resolved value for the requested `skill_name` (or `{}` if no entry).

## Merge semantics

```
Global:  {"super-code-review": {"preset": "default", "modules": {"complexity": {"threshold": 10}}}}
Project: {"super-code-review": {"preset": "fast",    "modules": {"complexity": {"threshold": 20}}}}

Resolved:
  {"super-code-review": {"preset": "fast", "modules": {"complexity": {"threshold": 20}}}}
```

Lists replace wholesale (no element-wise merge):

```
Global:  {"super-execute": {"backends": ["inline-batch"]}}
Project: {"super-execute": {"backends": ["subagent-driven"]}}

Resolved:
  {"super-execute": {"backends": ["subagent-driven"]}}
```

## Why two layers, not three

Super-Model deliberately does NOT support per-skill `.super/skills/<name>/config.json` overlays. The 2-layer cascade is enough:

- **Global** holds your personal preferences (your favorite preset, your IDE-specific tweaks).
- **Project** holds project-specific overrides (this project needs the strict TDD policy; this one needs the parallel backend).

A third layer would invite "what wins?" confusion without solving a real problem. Per-skill config goes in the project layer's nested dict.

## Why fail-fast on load

HIGH-006 hardening. A historical bug pattern: validation only on write means a hand-edited bad config silently degrades to defaults at the first field access, producing a confusing "why isn't my setting being respected?" symptom. The current contract:

- Load -> validate -> use.
- If load OR validate fails, raise with file path + JSON-pointer.
- The resolver does NOT silently degrade to `{}`.

This means a typo'd config breaks the next operation visibly rather than mysteriously.

## Why per-project state at all

The user-level / global config exists for personal preferences. But the per-project layer is the canonical state location, for the same reason the rest of Super-Model is per-project: reproducibility. A teammate cloning the repo should see the same skill behavior you see.

If you find yourself wanting a setting in the global layer, ask: would a teammate need this too? If yes, it belongs in the project layer.
