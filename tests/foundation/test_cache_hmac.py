"""MED-016: HMAC-signed cache markers.

Conservative degradation: ANY HMAC mismatch causes read_marker to
return None. Callers should never see a tampered marker as valid -
that would silently corrupt downstream decisions (e.g., skipping a
real code review because the marker says READY-TO-MERGE).
"""

from __future__ import annotations

import json
import os
import stat
import sys
from pathlib import Path

import pytest

from scripts.super_lib.cache import read_marker, write_marker


def _find_marker_file(project_root: Path, purpose: str, key: str) -> Path:
    cache_dir = project_root / ".super" / "cache"
    files = list(cache_dir.glob(f"{purpose}-{key}*.json"))
    assert files, "marker not found on disk"
    return files[0]


def test_round_trip_hmac_matches(tmp_project: Path, tmp_global_home: Path) -> None:
    write_marker(tmp_project, "code-review", "k1", {"verdict": "ok"})
    assert read_marker(tmp_project, "code-review", "k1") is not None


def test_tampered_data_field_returns_none(tmp_project: Path, tmp_global_home: Path) -> None:
    write_marker(tmp_project, "code-review", "k2", {"verdict": "ok"})
    marker_path = _find_marker_file(tmp_project, "code-review", "k2")
    raw = json.loads(marker_path.read_text(encoding="utf-8"))
    # Tamper with the data field but leave the hmac alone.
    if isinstance(raw.get("data"), dict):
        raw["data"]["verdict"] = "READY-TO-MERGE"  # attacker upgrades verdict
    marker_path.write_text(json.dumps(raw), encoding="utf-8")
    # The verification must fail and read_marker must return None.
    assert read_marker(tmp_project, "code-review", "k2") is None


def test_tampered_hmac_field_returns_none(tmp_project: Path, tmp_global_home: Path) -> None:
    write_marker(tmp_project, "code-review", "k3", {"verdict": "ok"})
    marker_path = _find_marker_file(tmp_project, "code-review", "k3")
    raw = json.loads(marker_path.read_text(encoding="utf-8"))
    if "hmac" in raw:
        # Flip a few hex chars - any change breaks verification.
        raw["hmac"] = "0" * len(raw["hmac"])
    marker_path.write_text(json.dumps(raw), encoding="utf-8")
    assert read_marker(tmp_project, "code-review", "k3") is None


def test_legacy_unsigned_marker_treated_as_missing(
    tmp_project: Path, tmp_global_home: Path
) -> None:
    """A marker file from a pre-MED-016 release (no hmac field) must
    read as None - we cannot trust unsigned legacy data."""
    cache_dir = tmp_project / ".super" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    (cache_dir / "code-review-legacy.json").write_text(
        json.dumps({"data": {"verdict": "ok"}}),  # no "hmac"
        encoding="utf-8",
    )
    assert read_marker(tmp_project, "code-review", "legacy") is None


def test_cross_user_hmac_isolation(
    tmp_project: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Write a marker under HOME=A; switch to HOME=B; the marker must
    be unreadable. Different per-user secret = different HMAC."""
    home_a = tmp_path / "home-a"
    home_a.mkdir()
    monkeypatch.setenv("HOME", str(home_a))
    monkeypatch.setenv("USERPROFILE", str(home_a))
    write_marker(tmp_project, "code-review", "shared", {"verdict": "ok"})
    assert read_marker(tmp_project, "code-review", "shared") is not None

    # Switch to a different user-home; secret differs; HMAC differs.
    home_b = tmp_path / "home-b"
    home_b.mkdir()
    monkeypatch.setenv("HOME", str(home_b))
    monkeypatch.setenv("USERPROFILE", str(home_b))
    assert read_marker(tmp_project, "code-review", "shared") is None


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX-only chmod")
def test_secret_file_permissions(tmp_project: Path, tmp_global_home: Path) -> None:
    """The per-user secret file must be 0600 on POSIX so other accounts
    on the same machine cannot read it and forge markers."""
    # Trigger secret creation.
    write_marker(tmp_project, "code-review", "perms", {"verdict": "ok"})
    secret = tmp_global_home / ".super-model" / "cache-secret.bin"
    if secret.exists():
        mode = os.stat(secret).st_mode & 0o777
        assert mode == 0o600, f"expected 0600 on secret, got {mode:o}"
