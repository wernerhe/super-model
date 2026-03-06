"""Per-user HMAC for cache marker integrity.

The cache directory at <project>/.super/cache/ holds verdicts from
super-code-review that super-prepare-branch reads at the merge gate.
Without integrity protection, anyone (or any process) with write access
to that directory could plant a verdict that short-circuits the review.

The mitigation: every marker is signed with a per-user HMAC-SHA256 over
the canonical JSON of (purpose, key, data). The signing secret is a
single 32-byte file at ~/.super-model/cache-secret.bin (chmod 0600 on
POSIX). The secret never leaves the user's home directory.

Cross-user threat (shared CI / dev environments): User A's CI-generated
marker cannot be replayed in User B's checkout because they have
different per-user secrets.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
from pathlib import Path
from typing import Any


def _secret_path() -> Path:
    home = Path(os.environ.get("HOME") or os.environ.get("USERPROFILE") or "")
    if not home or not home.exists():
        raise RuntimeError("Cannot locate HOME / USERPROFILE for cache-secret storage.")
    return home / ".super-model" / "cache-secret.bin"


def _load_or_create_secret() -> bytes:
    """Read the per-user 32-byte HMAC secret, creating it lazily on first use.

    The secret is generated via secrets.token_bytes(32) and stored with
    POSIX 0600 mode. Subsequent calls just read the existing file.
    """
    path = _secret_path()
    if path.exists():
        return path.read_bytes()
    path.parent.mkdir(parents=True, exist_ok=True)
    secret = secrets.token_bytes(32)
    path.write_bytes(secret)
    if os.name != "nt":
        os.chmod(path, 0o600)
    return secret


def _payload_bytes(purpose: str, key: str, data: dict[str, Any]) -> bytes:
    """Produce canonical bytes for HMAC computation.

    sort_keys=True is essential: without it, dict reordering between
    writes would produce different bytes for the same logical payload,
    breaking verification.
    """
    canonical = json.dumps(
        {"purpose": purpose, "key": key, "data": data},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return canonical.encode("utf-8")


def compute_hmac(purpose: str, key: str, data: dict[str, Any]) -> str:
    """Compute hex HMAC-SHA256 of (purpose, key, data) using the per-user secret."""
    secret = _load_or_create_secret()
    return hmac.new(secret, _payload_bytes(purpose, key, data), hashlib.sha256).hexdigest()


def verify_hmac(purpose: str, key: str, data: dict[str, Any], expected: str) -> bool:
    """Constant-time comparison of expected HMAC vs computed HMAC.

    Returns False if `expected` is not a string. Constant-time comparison
    avoids timing side channels.
    """
    if not isinstance(expected, str):
        return False
    actual = compute_hmac(purpose, key, data)
    return hmac.compare_digest(actual, expected)
