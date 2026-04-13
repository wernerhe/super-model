---
name: super-visual-debug
description: Iterate on a visual bug or visual improvement using a capture / propose / apply / recapture loop. Uses available screenshot or browser-control MCPs; remembers capabilities across invocations so it doesn't re-probe each session.
---

# super-visual-debug

The visual fix-or-improve loop. Optimized for the common pattern: "this page / widget / chart looks wrong, iterate until it doesn't."

## When to use

- A UI bug needs fixing (alignment, color, broken layout).
- A visual improvement is being shipped (polish a chart, redesign a page).
- A regression is suspected against a known-good baseline screenshot.

## The 6-module loop

1. `capability-probe` - check what visual tools are available (browser MCPs, screenshot CLIs, image inspection). Skipped if `capability-memory` already has fresh entries.
2. `initial-capture` - capture the current state, possibly from multiple angles / viewport sizes / states.
3. `fix-proposal` - based on the captures and the user's stated intent, propose a specific fix.
4. `apply-and-recapture` - apply the fix in code, then re-capture from the same angles.
5. `compare-iterations` - compare before / after captures; surface remaining diffs.
6. `capability-memory` - persist discovered tools / endpoints to `<project>/.super/cache/visual-capabilities-*.json` so future invocations skip the probe.

The loop continues (modules 3-5 repeat) until the user is satisfied or the diff is within the requested tolerance.

## Multi-angle capture

For non-trivial UIs, single-angle captures miss layout regressions. Default angles:

- Desktop viewport (1440x900).
- Mobile viewport (375x667).
- Component in isolation if the bug is local.
- Component in context if the bug is about interaction with surrounding elements.

## Capability memory

The probe is moderately expensive (timing out on missing MCPs, etc.). Caching what's available per-project means subsequent invocations are instant. Cache entries are HMAC-signed via `super_lib.cache`; tampering invalidates them and triggers a re-probe.

## Hard rules

- NEVER claim "fixed" without re-capturing AFTER the fix and verifying visually.
- NEVER batch multiple fix attempts into one apply-and-recapture cycle. One change per iteration.
- If the iteration count exceeds 5 without convergence, stop and ask the user whether to continue or re-scope.

## Verify after running

- The fix produces the user-described visual change (compared to initial capture).
- No new regressions in the multi-angle suite.
- `<project>/.super/cache/visual-capabilities-*.json` has fresh HMAC-signed entries for next time.
