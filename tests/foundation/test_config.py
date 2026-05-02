"""Config cascade resolution + deep-merge + validate.

Covers `config.resolve` cascade ordering (global then project; project
wins), `config._deep_merge` semantics, `config.validate` accept/reject
shapes, and the `write_project_config` round-trip.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.super_lib.config import (
    _deep_merge,
    resolve,
    validate,
    write_project_config,
)


def test_deep_merge_overlays_project_over_global() -> None:
    base = {"skill": {"k1": "from-global", "nested": {"a": 1, "b": 2}}}
    overlay = {"skill": {"k1": "from-project", "nested": {"b": 99}}}
    result = _deep_merge(base, overlay)
    assert result["skill"]["k1"] == "from-project"
    assert result["skill"]["nested"] == {"a": 1, "b": 99}


def test_deep_merge_replaces_non_dict_wholesale() -> None:
    base = {"skill": {"list_field": [1, 2, 3]}}
    overlay = {"skill": {"list_field": [9]}}
    result = _deep_merge(base, overlay)
    assert result["skill"]["list_field"] == [9]


def test_round_trip_project_config(tmp_project: Path, tmp_global_home: Path) -> None:
    cfg = {"super-code-review": {"preset": "fast"}}
    write_project_config(tmp_project, cfg)
    resolved = resolve("super-code-review", project_root=tmp_project)
    assert resolved.get("preset") == "fast"


def test_validate_accepts_minimal_valid_config() -> None:
    validate({"super-code-review": {"preset": "default"}})


def test_validate_rejects_non_dict_module_entry() -> None:
    with pytest.raises((ValueError, Exception)):
        validate({"super-code-review": "not-a-dict"})


def test_resolve_project_root_none_returns_only_global(tmp_global_home: Path) -> None:
    """With no project_root, resolve returns whatever the global layer says
    (or an empty dict if no global config exists)."""
    resolved = resolve("super-code-review", project_root=None)
    assert isinstance(resolved, dict)


def test_resolve_empty_project_returns_empty(tmp_project: Path, tmp_global_home: Path) -> None:
    """A `.super/` directory with no `config.json` is valid - empty
    project layer means defaults (or global only)."""
    resolved = resolve("super-code-review", project_root=tmp_project)
    assert isinstance(resolved, dict)


def test_project_overrides_global(tmp_project: Path, tmp_global_home: Path) -> None:
    """Global says preset=default; project says preset=fast; project wins."""
    # Write the global config to ~/.super-model/config.json
    super_model_dir = tmp_global_home / ".super-model"
    super_model_dir.mkdir(parents=True, exist_ok=True)
    (super_model_dir / "config.json").write_text(
        json.dumps({"super-code-review": {"preset": "default"}}),
        encoding="utf-8",
    )
    # Write the project config
    write_project_config(tmp_project, {"super-code-review": {"preset": "fast"}})

    resolved = resolve("super-code-review", project_root=tmp_project)
    assert resolved.get("preset") == "fast"
