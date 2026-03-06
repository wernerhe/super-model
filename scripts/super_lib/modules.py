"""Manifest reader and module-file frontmatter parser.

Used by the foundation tests (one per top-level skill) and by any skill
that wants to enumerate its own module list.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


def read_manifest(skill_dir: Path) -> dict[str, Any]:
    """Read <skill_dir>/manifest.json.

    Raises FileNotFoundError if the file is absent. Raises ValueError
    if the JSON is malformed or the root is not a dict.
    """
    manifest_path = skill_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"No manifest.json at {manifest_path}")
    try:
        parsed = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(
            f"manifest.json at {manifest_path} is malformed JSON: {e}"
        ) from e
    if not isinstance(parsed, dict):
        raise ValueError(
            f"manifest.json at {manifest_path} must be a JSON object, "
            f"got {type(parsed).__name__}"
        )
    return parsed


def list_modules(skill_dir: Path) -> list[str]:
    """Return module names in execution order.

    If every module entry declares an `order` field, sort by it.
    Otherwise preserve declaration order. Raises ValueError if any
    entry is missing the required `name` field or has a wrong shape.
    """
    manifest = read_manifest(skill_dir)
    entries = manifest.get("modules", [])
    if not isinstance(entries, list):
        raise ValueError(
            f"manifest.modules at {skill_dir} must be a list, "
            f"got {type(entries).__name__}"
        )
    collected: list[tuple[int | None, str]] = []
    all_have_order = True
    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ValueError(
                f"manifest.modules[{idx}] at {skill_dir} must be an object"
            )
        name = entry.get("name")
        if not isinstance(name, str):
            raise ValueError(
                f"manifest.modules[{idx}] at {skill_dir} missing required 'name'"
            )
        order = entry.get("order")
        if not isinstance(order, int):
            all_have_order = False
        collected.append((order, name))
    if all_have_order:
        return [name for _, name in sorted(collected, key=lambda pair: pair[0] or 0)]
    return [name for _, name in collected]


def parse_frontmatter(module_file: Path, validate: bool = True) -> dict[str, Any]:
    """Parse YAML frontmatter from a Markdown module file.

    Splits on the first two `---` delimiters and yaml.safe_load's the
    middle section.

    Rejects non-dict YAML at the frontmatter position. Without this
    check, a frontmatter that's a bare scalar (`---\\nfoo\\n---\\n`)
    parses to `"foo"` and would slip past schema validation that
    expects an object at the root.

    When `validate=True` (the default), the parsed dict is also
    validated against module-frontmatter.schema.json. Production code
    paths always validate; tests that fixture intentionally-malformed
    input pass `validate=False`.
    """
    text = module_file.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(
            f"No frontmatter delimiters (---) found in {module_file}"
        )
    try:
        parsed = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        raise ValueError(
            f"Invalid YAML frontmatter in {module_file}: {e}"
        ) from e
    if parsed is None:
        return {}
    if not isinstance(parsed, dict):
        raise ValueError(
            f"Frontmatter in {module_file} must be a YAML mapping (dict), "
            f"got {type(parsed).__name__}"
        )
    if validate:
        from .config import validate_module
        validate_module(parsed)
    return parsed
