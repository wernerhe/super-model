"""super-mcp-builder: manifest <-> module files <-> presets consistency."""

from __future__ import annotations

from pathlib import Path

from scripts.super_lib.modules import parse_frontmatter, read_manifest

SKILL = "super-mcp-builder"


def test_manifest_entries_have_module_files(super_root: Path) -> None:
    skill_dir = super_root / "skills" / SKILL
    manifest = read_manifest(skill_dir)
    declared = {entry["name"] for entry in manifest["modules"]}
    on_disk = {p.stem for p in (skill_dir / "modules").glob("*.md")}
    assert declared == on_disk


def test_every_module_has_valid_frontmatter(super_root: Path) -> None:
    skill_dir = super_root / "skills" / SKILL
    for module_path in (skill_dir / "modules").glob("*.md"):
        fm = parse_frontmatter(module_path, validate=True)
        assert fm["name"] == module_path.stem


def test_preset_modules_exist_in_manifest(super_root: Path) -> None:
    skill_dir = super_root / "skills" / SKILL
    manifest = read_manifest(skill_dir)
    declared = {entry["name"] for entry in manifest["modules"]}
    for _preset_name, preset in (manifest.get("presets") or {}).items():
        for module_name in preset.get("modules_enabled", []):
            assert module_name in declared


def test_module_count_matches_canonical(super_root: Path) -> None:
    """super-mcp-builder has 4 modules: discover-mcps, install-upstream,
    alter-config, build-new."""
    manifest = read_manifest(super_root / "skills" / SKILL)
    assert len(manifest["modules"]) == 4
