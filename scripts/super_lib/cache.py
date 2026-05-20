"""Cache marker read/write with HMAC integrity protection.

A "cache marker" is a small JSON file under <project>/.super/cache/
that records the outcome of a long-running check (typically a
super-code-review pass) so a later skill (typically super-prepare-branch)
can short-circuit re-running the check when nothing has changed.

Marker filename layout:

    <project>/.super/cache/<purpose>-<key>.json

where `purpose` identifies what the marker is for (e.g., "code-review")
and `key` is the invalidation key (typically a commit SHA). One file per
(purpose, key) tuple; no subdirectories.

Threat surface:

- Without filename sanitization, an attacker-controlled purpose or key
  could escape the cache directory (e.g., "../../etc/passwd") or
  collide with Windows reserved device names (CON, PRN, NUL, etc.).
- Without HMAC integrity, anyone with write access to .super/cache/
  could plant a "verdict: READY-TO-MERGE" marker that bypasses review.

Mitigations live in this module:

- _sanitize_path_component enforces an allowlist regex
  (^[a-zA-Z0-9_-]{1,128}$) AND rejects Windows reserved device names
  case-insensitively.
- write_marker calls compute_hmac and embeds the hex HMAC in the
  payload. read_marker verifies it; any mismatch returns None.

Conservative degradation: ANY uncertainty on read (missing file, bad
JSON, missing hmac field, missing data field, HMAC mismatch) returns
None. The caller falls back to re-running the underlying check. A
single bad cache file cannot break downstream flows.
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ._hmac import compute_hmac, verify_hmac
from ._io import atomic_write_json

_CACHE_KEY_RE = re.compile(r"^[a-zA-Z0-9_-]{1,128}$")

_WINDOWS_RESERVED = frozenset(
    {"CON", "PRN", "AUX", "NUL"}
    | {f"COM{i}" for i in range(1, 10)}
    | {f"LPT{i}" for i in range(1, 10)}
)


def _sanitize_path_component(value: Any, label: str) -> str:
    """Validate that a string is safe to embed in a cache filename.

    Two checks, both must pass:

    1. Match the allowlist regex ^[a-zA-Z0-9_-]{1,128}$. This rejects
       null bytes, path separators (/, \\), NTFS alternate-data-stream
       colons, dots (so no .. traversal), Unicode look-alikes, and
       anything else outside [A-Za-z0-9_-]. Length cap at 128.

    2. Not be a Windows reserved device name (case-insensitive):
       CON, PRN, AUX, NUL, COM1-COM9, LPT1-LPT9. These produce
       undefined behavior when used as filenames on Windows.

    Failures raise ValueError BEFORE any filesystem operation.
    """
    if not isinstance(value, str):
        raise ValueError(f"Cache {label} must be a string, got {type(value).__name__}")
    if not _CACHE_KEY_RE.fullmatch(value):
        raise ValueError(
            f"Cache {label} {value!r} contains characters outside the allowed "
            f"set [a-zA-Z0-9_-] or exceeds 128 characters."
        )
    if value.upper() in _WINDOWS_RESERVED:
        raise ValueError(
            f"Cache {label} {value!r} matches a Windows reserved device name; choose another."
        )
    return value


def _marker_path(project_root: Path, purpose: str, key: str) -> Path:
    """Compose the on-disk path for a cache marker, with both components sanitized."""
    purpose_clean = _sanitize_path_component(purpose, "purpose")
    key_clean = _sanitize_path_component(key, "key")
    return project_root / ".super" / "cache" / f"{purpose_clean}-{key_clean}.json"


def _utc_now_iso() -> str:
    """UTC ISO-8601 timestamp with Z suffix instead of +00:00."""
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def read_marker(project_root: Path, purpose: str, key: str) -> dict[str, Any] | None:
    """Read a cache marker, verifying its HMAC integrity.

    On success: returns the full marker dict (including the hmac field).
    Otherwise returns None for ANY of:

    - Sanitization rejected the purpose or key.
    - File does not exist.
    - File read failed (permission, etc.).
    - JSON parse failure.
    - Root value is not a dict.
    - Missing or non-string 'hmac' field. Legacy unsigned markers (from
      before HMAC integrity landed) are treated as missing so the next
      write produces a fresh integrity-protected marker.
    - Missing or non-dict 'data' field.
    - HMAC mismatch (tamper or hand-edit).

    The conservative-degradation pattern means a bad marker cannot
    break the flow; it just looks like a cache miss to the caller.
    """
    try:
        path = _marker_path(project_root, purpose, key)
    except ValueError:
        return None
    if not path.exists():
        return None
    try:
        raw_text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        return None
    expected_hmac = parsed.get("hmac")
    if not isinstance(expected_hmac, str):
        return None
    data = parsed.get("data")
    if not isinstance(data, dict):
        return None
    if not verify_hmac(purpose, key, data, expected_hmac):
        return None
    return parsed


def write_marker(
    project_root: Path,
    purpose: str,
    key: str,
    data: dict[str, Any],
    ttl_seconds: int | None = None,
) -> None:
    """Write a cache marker with HMAC integrity protection.

    Filename components (purpose, key) go through _sanitize_path_component
    before any filesystem operation. The payload is:

    - purpose: the cache purpose identifier
    - key: the invalidation key (typically a commit SHA)
    - timestamp: UTC ISO-8601 timestamp at write
    - data: caller-provided payload (must be a dict)
    - hmac: hex HMAC-SHA256 over canonical JSON of (purpose, key, data)
    - ttl_seconds: optional non-negative integer time-to-live

    The actual write goes through atomic_write_json so the file is
    lock-serialized, fsync'd, and POSIX-0600 before rename.
    """
    if not isinstance(data, dict):
        raise ValueError(f"Cache marker data must be a dict, got {type(data).__name__}")
    path = _marker_path(project_root, purpose, key)
    payload: dict[str, Any] = {
        "purpose": purpose,
        "key": key,
        "timestamp": _utc_now_iso(),
        "data": data,
        "hmac": compute_hmac(purpose, key, data),
    }
    if ttl_seconds is not None:
        if not isinstance(ttl_seconds, int) or ttl_seconds < 0:
            raise ValueError(f"ttl_seconds must be a non-negative int, got {ttl_seconds!r}")
        payload["ttl_seconds"] = ttl_seconds
    atomic_write_json(path, payload)
