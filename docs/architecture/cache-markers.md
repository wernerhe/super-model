# Cache markers: HMAC-signed integrity model

Cache markers let one skill skip work that another has already done. The integrity model is HMAC + conservative degradation: tampered markers look indistinguishable from "no marker" to the consumer, which then falls back to re-running the underlying check.

## The trust boundary

Consider the canonical case: `super-code-review` produces a verdict (READY-TO-MERGE / NEEDS-FIXES) and writes it as a marker. `super-prepare-branch` reads the marker and skips re-running review if the verdict is fresh.

The trust boundary: **the verdict drives a real behavioral decision (skip the check)**. Without integrity protection, a stale or tampered marker could:

- Cause super-prepare-branch to falsely report "ready to merge" on broken code.
- Be planted by a script that wants to bypass review gates.

Both failure modes are silent without an integrity check.

## HMAC construction

Marker filename: `<project>/.super/cache/<purpose>-<key>.json`

Marker payload:

```json
{
  "purpose": "code-review",
  "key": "<sanitized identifier, typically commit SHA>",
  "data": {
    "verdict": "READY-TO-MERGE",
    "findings": [],
    "...": "..."
  },
  "ttl_seconds": 86400,
  "created_at": "2026-05-20T14:30:00Z",
  "expires_at": "2026-05-21T14:30:00Z",
  "hmac": "<sha256 hex digest>"
}
```

The HMAC is computed as:

```
hmac = HMAC-SHA256(
  key = <per-user secret from ~/.super-model/cache-secret.bin>,
  msg = canonical-JSON of {purpose, key, data, ttl_seconds, created_at, expires_at}
)
```

The secret is generated on first use, 32 random bytes, stored at `~/.super-model/cache-secret.bin` with 0o600 permissions on POSIX.

## Conservative degradation

`cache.read_marker(project_root, purpose, key)` returns `None` for ALL of:

- The marker file does not exist.
- The file is not valid JSON.
- The root is not an object.
- The marker is missing required fields (`hmac`, `data`, ...).
- The HMAC does not verify.
- The marker has expired (per `expires_at` if set).

The consumer sees `None` and re-runs the underlying check. **No partial trust**. A marker is either fully verified or it doesn't exist as far as the consumer is concerned.

This is the right asymmetry: re-running a check costs time; trusting a bad marker costs correctness.

## Filename sanitization (HIGH-004)

`<purpose>` and `<key>` go through `cache._sanitize_path_component`, which enforces a strict ASCII allowlist:

- Allowed: `[a-zA-Z0-9_-]+`, 1-128 chars.
- Rejected: empty string, oversized, null bytes, path separators, NTFS Alternate Data Stream syntax (`:`), Windows reserved device names (`CON`, `COM1`, etc.), Unicode confusables, leading dots.

This prevents path traversal, hidden file creation, and confusables-driven attacks where a forged marker file masquerades as a legitimate one.

## Cross-user isolation

The HMAC secret is per-user (lives in the user's home directory). A marker written by user A cannot be verified by user B because their secrets differ. Crucially:

- Cloning a repo with cache markers and running `super-prepare-branch` does NOT trust the cloned markers. They appear as `None` and trigger re-review.
- Backup / restore across machines invalidates markers.
- This is by design - markers are a per-user optimization, not a cross-user trust artifact.

## What's NOT covered

- A user attacking their own secret file (writing a forged marker with the real secret). Out of scope - if an attacker has read access to your home directory, the secret is already lost.
- Cross-machine markers. Don't try to share markers between machines; they're throw-away.

## Hook into super_lib

```python
from scripts.super_lib import cache

cache.write_marker(project_root, "code-review", commit_sha, verdict_dict, ttl_seconds=86400)

marker = cache.read_marker(project_root, "code-review", commit_sha)
if marker is None:
    # No fresh trustworthy marker - run the underlying check.
    ...
else:
    verdict = marker["data"]
    ...
```
