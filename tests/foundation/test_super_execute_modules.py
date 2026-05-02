"""super-execute: manifest <-> backends + policies consistency."""
from __future__ import annotations

from pathlib import Path

from scripts.super_lib.modules import parse_frontmatter, read_manifest

SKILL = "super-execute"


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
    for preset_name, preset in (manifest.get("presets") or {}).items():
        for module_name in preset.get("modules_enabled", []):
            assert module_name in declared


def test_has_backends_and_policies(super_root: Path) -> None:
    """super-execute must include at least one backend (provides
    per-step-execute hook) and at least one policy."""
    skill_dir = super_root / "skills" / SKILL
    manifest = read_manifest(skill_dir)
    names = [entry["name"] for entry in manifest["modules"]]
    backends = [n for n in names if n.startswith("backend-")]
    policies = [n for n in names if n.startswith("policy-")]
    assert len(backends) >= 1, "no backend modules found"
    assert len(policies) >= 1, "no policy modules found"
