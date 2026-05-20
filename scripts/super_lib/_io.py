"""Shared I/O helpers for Super-Model scripts."""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from typing import Any

from filelock import FileLock


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write a JSON object atomically (write-temp-then-rename).

    Uses a 10-second file lock to serialize concurrent writers, calls
    os.fsync() on the temp file before rename so a power loss cannot
    leave the file renamed-into-place with stale contents, and sets
    POSIX 0600 mode on the temp file before rename so configs do not
    leak to other users on multi-user systems. On Windows the chmod is
    a no-op; ACLs inherit from the parent directory.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_suffix(path.suffix + ".lock")
    with FileLock(str(lock_path), timeout=10):
        tmp = path.with_suffix(f".json.tmp.{uuid.uuid4().hex[:8]}")
        text = json.dumps(payload, indent=2) + "\n"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        if os.name != "nt":
            os.chmod(tmp, 0o600)
        tmp.replace(path)
