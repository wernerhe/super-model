"""Manifest reader + frontmatter parser tests.

Covers `read_manifest`, `list_modules`, and `parse_frontmatter` with the
expected error paths (missing files, malformed JSON, missing required
schema fields, scalar/list frontmatter rejection per MED-005).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.super_lib.modules import list_modules, parse_frontmatter, read_manifest


def _make_skill(tmp_path: Path, manifest: dict, modules: dict[str, str]) -> Path:
    skill = tmp_path / "fake-skill"
    skill.mkdir()
    (skill / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    if modules:
        (skill / "modules").mkdir()
        for name, body in modules.items():
            (skill / "modules" / "{}.md".format(name)).write_text(body, encoding="utf-8")
    return skill


def test_read_manifest_returns_dict(tmp_path: Path) -> None:
    skill = _make_skill(tmp_path, {"skill": "x", "modules": []}, {})
    parsed = read_manifest(skill)
    assert parsed["skill"] == "x"


def test_read_manifest_missing_raises(tmp_path: Path) -> None:
    with pytest.raises((FileNotFoundError, OSError)):
        read_manifest(tmp_path / "does-not-exist")


def test_read_manifest_malformed_raises(tmp_path: Path) -> None:
    skill = tmp_path / "bad"
    skill.mkdir()
    (skill / "manifest.json").write_text("not-json", encoding="utf-8")
    with pytest.raises((ValueError, json.JSONDecodeError)):
        read_manifest(skill)


def test_list_modules_respects_order(tmp_path: Path) -> None:
    skill = _make_skill(
        tmp_path,
        {
            "skill": "x",
            "modules": [
                {"name": "b", "order": 2},
                {"name": "a", "order": 1},
                {"name": "c", "order": 3},
            ],
        },
        {},
    )
    assert list_modules(skill) == ["a", "b", "c"]


def test_list_modules_missing_name_raises(tmp_path: Path) -> None:
    skill = _make_skill(
        tmp_path,
        {"skill": "x", "modules": [{"order": 1}]},
        {},
    )
    with pytest.raises((KeyError, ValueError)):
        list_modules(skill)


def test_parse_frontmatter_validates_schema(tmp_path: Path) -> None:
    module = tmp_path / "ok.md"
    module.write_text(
        "---\nname: ok\ndescription: A valid description string here\n---\n\nbody\n",
        encoding="utf-8",
    )
    fm = parse_frontmatter(module, validate=True)
    assert fm["name"] == "ok"


def test_parse_frontmatter_rejects_missing_required(tmp_path: Path) -> None:
    module = tmp_path / "bad.md"
    module.write_text(
        "---\ndescription: missing the name field\n---\n\nbody\n",
        encoding="utf-8",
    )
    with pytest.raises((ValueError, Exception)):
        parse_frontmatter(module, validate=True)


def test_parse_frontmatter_no_delimiter_raises(tmp_path: Path) -> None:
    module = tmp_path / "no-fm.md"
    module.write_text("body without frontmatter\n", encoding="utf-8")
    with pytest.raises((ValueError, Exception)):
        parse_frontmatter(module, validate=True)


def test_parse_frontmatter_rejects_scalar_yaml(tmp_path: Path) -> None:
    """MED-005: scalar (string) frontmatter must be rejected."""
    module = tmp_path / "scalar.md"
    module.write_text("---\nsome bare scalar string\n---\n\nbody\n", encoding="utf-8")
    with pytest.raises((ValueError, Exception)):
        parse_frontmatter(module, validate=True)


def test_parse_frontmatter_rejects_list_yaml(tmp_path: Path) -> None:
    """MED-005: list frontmatter must be rejected."""
    module = tmp_path / "list.md"
    module.write_text("---\n- one\n- two\n---\n\nbody\n", encoding="utf-8")
    with pytest.raises((ValueError, Exception)):
        parse_frontmatter(module, validate=True)


def test_parse_frontmatter_validate_false_skips_schema(tmp_path: Path) -> None:
    module = tmp_path / "loose.md"
    module.write_text("---\nname: ok\n---\n\nbody\n", encoding="utf-8")
    fm = parse_frontmatter(module, validate=False)
    assert fm["name"] == "ok"
