---
name: review-cache-check
description: Read the HMAC-signed code-review cache marker for the current HEAD SHA. If present and HMAC-valid, trust the verdict and skip re-review. If absent or HMAC-mismatch, chain-fire super-code-review and wait for the fresh verdict.
---

# review-cache-check

## What it does

The fast path for merge-readiness. Concretely:

1. Compute the current HEAD SHA (`git rev-parse HEAD`).
2. Read `<project>/.super/cache/code-review-<sha>.json` via `super_lib.cache.read_marker`.
3. If `read_marker` returns a marker, inspect `data.verdict`:
   - `READY-TO-MERGE` -> downstream modules proceed.
   - `NEEDS-FIXES` -> stop and present the findings; user must fix and re-run.
4. If `read_marker` returns `None` (marker missing, HMAC-invalid, etc.):
   - Inform the user: "no fresh review found for HEAD; running super-code-review now."
   - Chain-fire `super-code-review` and wait for it to write a new marker.
   - Re-read the marker (now present).

## HMAC trust boundary

`super_lib.cache.read_marker` returns `None` for ANY of: file missing, JSON parse fail, missing hmac field, missing data field, or HMAC mismatch. The conservative-degradation pattern means a tampered marker looks like "no marker" - the response is "re-run the underlying check", which is always safe.

## Why cache-driven

Without the cache, every `super-prepare-branch` invocation would re-run the full 9-module code review. On a small change, that's redundant. With the cache, the second invocation in 30 seconds returns instantly because the SHA is the same.

## Idempotency

Read-only at this module; the chain-fire writes a marker if invoked.
