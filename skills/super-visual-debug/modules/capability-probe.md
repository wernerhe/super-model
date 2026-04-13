---
name: capability-probe
description: Discover what visual tools are available in the current environment - browser-control MCPs, screenshot CLIs, image inspection helpers. Skipped when capability-memory has a fresh cached probe.
---

# capability-probe

## What it does

Checks for the presence of visual-capture tools the loop can use:

- Browser-control MCPs (playwright-mcp, browser-use, puppeteer-mcp, etc.).
- Screenshot CLIs (`screencapture` on macOS, `import` on X11, Windows snipping APIs).
- Image-diff tools (`compare` from ImageMagick, `oxipng`, etc.).
- Visual-comparison MCPs.

For each, records:

- Tool name.
- Invocation pattern (command line, MCP tool name).
- Probe result: available / not-available / version-mismatch.

## Caching

If `<project>/.super/cache/visual-capabilities-<project-fingerprint>.json` exists and is fresh (per `capability-memory` policy), skip the probe and trust the cached result. Probe re-runs on cache miss, expiry, or HMAC mismatch (which is treated as a cache miss).

## Output

A capability record consumed by `initial-capture` and `apply-and-recapture` to pick the right tool.

## Idempotency

Read-only. Cache write happens in the `capability-memory` module at the end of the loop.
