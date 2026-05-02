"""Shared fixtures for the foundation test suite.

Two patterns appear pervasively:

- `tmp_project` - an empty project root with a `.super/` directory ready
  for `cache.write_marker` / `cache.read_marker` / `config.resolve`.
- `tmp_global_home` - HOME / USERPROFILE redirected to a temp directory
  so the HMAC secret and global config never touch the user's real home.

The `super_root` fixture points at the repo root so the skill manifest
tests can locate `skills/<name>/manifest.json`.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    """Create an empty `.super/` directory inside a temp project root."""
    (tmp_path / ".super").mkdir()
    return tmp_path


@pytest.fixture
def tmp_global_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Override HOME / USERPROFILE so secrets + global config land in temp.

    Without this, every test that touches `~/.super-model/cache-secret.bin`
    would leave artifacts in the real user home - and worse, cross-test
    state would leak between runs.
    """
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
    return home


@pytest.fixture
def super_root() -> Path:
    """Absolute path to the Super-Model repo root.

    Test file lives at tests/foundation/conftest.py; the repo root is two
    parents up.
    """
    return Path(__file__).resolve().parents[2]


def write_json(path: Path, payload: dict) -> None:
    """Helper: write a JSON object to path, creating parents as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
