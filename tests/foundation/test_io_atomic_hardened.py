"""HIGH-005: atomic-write discipline (FileLock + fsync + 0600).

The contract:

- Concurrent writers serialize via FileLock; no data loss.
- POSIX result file is 0600 (owner-only read+write).
- fsync is called so the file is durable before atomic rename.
- A torn write cannot be observed at the final path - the temp file
  sits with a `.json.tmp.*` suffix until `os.replace()` commits.
"""
from __future__ import annotations

import os
import sys
import threading
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.super_lib._io import atomic_write_json


def test_round_trip(tmp_path: Path) -> None:
    target = tmp_path / "out.json"
    atomic_write_json(target, {"key": "value", "n": 7})
    assert target.exists()
    import json
    assert json.loads(target.read_text()) == {"key": "value", "n": 7}


def test_concurrent_writers_serialize(tmp_path: Path) -> None:
    """Two threads writing concurrently must produce a valid JSON file
    (one of them wins; both complete without exception; no torn write)."""
    target = tmp_path / "concurrent.json"
    errors: list[BaseException] = []

    def writer(payload: dict) -> None:
        try:
            atomic_write_json(target, payload)
        except BaseException as exc:
            errors.append(exc)

    threads = [
        threading.Thread(target=writer, args=({"writer": i, "value": i * 10},))
        for i in range(8)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, "concurrent writers raised: {}".format(errors)
    import json
    parsed = json.loads(target.read_text())
    assert "writer" in parsed
    assert 0 <= parsed["writer"] <= 7


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX-only chmod check")
def test_posix_mode_is_0600(tmp_path: Path) -> None:
    target = tmp_path / "secret.json"
    atomic_write_json(target, {"sensitive": True})
    mode = os.stat(target).st_mode & 0o777
    assert mode == 0o600, "expected 0600, got {:o}".format(mode)


def test_fsync_is_called(tmp_path: Path) -> None:
    """The atomic-write path must fsync before the rename so the data is
    durable on disk, not just in the page cache."""
    target = tmp_path / "synced.json"
    with patch("scripts.super_lib._io.os.fsync") as mock_fsync:
        atomic_write_json(target, {"durable": True})
        assert mock_fsync.called, "os.fsync was not called"


def test_no_tmp_file_left_behind(tmp_path: Path) -> None:
    """After a successful write, no .tmp.* sibling should remain."""
    target = tmp_path / "clean.json"
    atomic_write_json(target, {"clean": True})
    siblings = list(tmp_path.glob("clean.json.tmp.*"))
    assert siblings == [], "unexpected temp siblings: {}".format(siblings)
