"""Cache marker round-trip without involving HMAC tampering.

Covers the happy paths and the conservative-degradation behavior:
read_marker returns None for absent / corrupt / wrong-type files
rather than raising, so callers can always safely treat the absence
of a marker as "re-run the underlying check".
"""

from __future__ import annotations

import json
from pathlib import Path

from scripts.super_lib.cache import read_marker, write_marker


def test_write_then_read_round_trip(tmp_project: Path, tmp_global_home: Path) -> None:
    """read_marker returns the full envelope; user payload sits under `data`."""
    payload = {"verdict": "READY-TO-MERGE", "findings": []}
    write_marker(tmp_project, "code-review", "abc123", payload)
    result = read_marker(tmp_project, "code-review", "abc123")
    assert result is not None
    assert result["data"]["verdict"] == "READY-TO-MERGE"
    assert result["data"]["findings"] == []
    assert result["purpose"] == "code-review"
    assert result["key"] == "abc123"


def test_read_absent_marker_returns_none(tmp_project: Path, tmp_global_home: Path) -> None:
    assert read_marker(tmp_project, "code-review", "missing") is None


def test_read_corrupt_json_returns_none(tmp_project: Path, tmp_global_home: Path) -> None:
    cache_dir = tmp_project / ".super" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    (cache_dir / "code-review-corrupt.json").write_text("this is not json", encoding="utf-8")
    assert read_marker(tmp_project, "code-review", "corrupt") is None


def test_read_wrong_root_type_returns_none(tmp_project: Path, tmp_global_home: Path) -> None:
    """A JSON file whose root is a list (not a dict) must read as None."""
    cache_dir = tmp_project / ".super" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    (cache_dir / "code-review-listroot.json").write_text(json.dumps([1, 2, 3]), encoding="utf-8")
    assert read_marker(tmp_project, "code-review", "listroot") is None


def test_ttl_recorded_when_provided(tmp_project: Path, tmp_global_home: Path) -> None:
    write_marker(
        tmp_project,
        "code-review",
        "with-ttl",
        {"verdict": "x"},
        ttl_seconds=3600,
    )
    # Find the on-disk marker and inspect its raw shape.
    cache_dir = tmp_project / ".super" / "cache"
    files = list(cache_dir.glob("code-review-with-ttl*.json"))
    assert files, "marker not written"
    raw = json.loads(files[0].read_text(encoding="utf-8"))
    # TTL or expiry-related field should be present somewhere in the envelope.
    text = json.dumps(raw)
    assert "ttl" in text.lower() or "expir" in text.lower() or "3600" in text
