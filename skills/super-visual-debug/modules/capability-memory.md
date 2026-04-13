---
name: capability-memory
description: At the end of the loop, persist the capability-probe result to <project>/.super/cache/ so future invocations of super-visual-debug skip the probe step. HMAC-signed; tampered entries trigger re-probe.
---

# capability-memory

## What it does

Writes the discovered capability record (from `capability-probe`) to a per-project cache marker:

```
<project>/.super/cache/visual-capabilities-<fingerprint>.json
```

Where `<fingerprint>` encodes the project type + key dependency versions, so capability cache stays valid until those change.

The marker uses `super_lib.cache.write_marker`, which embeds an HMAC-SHA256 signed by the per-user secret. Tampering with the marker (or any HMAC mismatch on read) causes the next `super-visual-debug` invocation to treat the marker as missing and re-probe.

## TTL

Default TTL: 7 days. Capabilities don't change daily, but they do change as users install new MCPs or upgrade browsers. A week-long TTL balances probe cost against staleness.

## Why HMAC-signed

The cache marker drives a real behavioral decision: skip the probe and trust the cached tool list. Without integrity protection, a bad cache could cause the loop to call a no-longer-available tool and fail mysteriously. HMAC + conservative degradation (treat as missing on any uncertainty) keeps the loop safe.

## Idempotency

Last-write-wins. Re-running with identical capabilities is a no-op (same payload -> same HMAC -> same file).
