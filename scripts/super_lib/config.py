"""Configuration cascade resolver and schema validator.

Every Super-Model skill that consults configuration goes through
config.resolve(skill_name, project_root=...). The resolver covers
layers 1-3 of the full 5-layer cascade described in the architecture
docs:

    Layer 1: defaults baked into the SKILL.md / manifest
    Layer 2: ~/.super-model/config.json (user-level global)
    Layer 3: <project>/.super/config.json (per-project)
    Layer 4: per-invocation flag (--no-X, etc.)  [caller-applied]
    Layer 5: per-step plan annotation              [caller-applied]

Higher layers override lower, with dict values deep-merging.

Both global and project configs are validated against
config.schema.json on load (not only on write). A tampered or
hand-edited file is rejected at the resolve point with the file path
embedded in the error, instead of slipping through and failing later
with an opaque field-access error.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import jsonschema

from ._io import atomic_write_json

_GLOBAL_CONFIG_DIR = ".super-model"
_GLOBAL_CONFIG_FILENAME = "config.json"
_PROJECT_CONFIG_RELATIVE = Path(".super") / "config.json"

_SCHEMAS_DIR = Path(__file__).resolve().parent.parent.parent / "schemas"
_CONFIG_SCHEMA_PATH = _SCHEMAS_DIR / "config.schema.json"
_MODULE_FRONTMATTER_SCHEMA_PATH = _SCHEMAS_DIR / "module-frontmatter.schema.json"


def _global_config_path() -> Path:
    """Resolve ~/.super-model/config.json, honoring HOME then USERPROFILE."""
    home = os.environ.get("HOME") or os.environ.get("USERPROFILE")
    if not home:
        raise RuntimeError("Cannot locate HOME / USERPROFILE for global Super-Model config.")
    return Path(home) / _GLOBAL_CONFIG_DIR / _GLOBAL_CONFIG_FILENAME


def _load_json_schema(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Schema not found at {path}; reinstall Super-Model?")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"Schema at {path} is malformed JSON: {e}") from e


def _load_json_or_empty(path: Path) -> dict[str, Any]:
    """Load a config file or return {} if absent. Raises if malformed."""
    if not path.exists():
        return {}
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as e:
        raise RuntimeError(f"Cannot read config at {path}: {e}") from e
    if not raw.strip():
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Config at {path} is malformed JSON: {e}") from e
    if not isinstance(parsed, dict):
        raise ValueError(f"Config at {path} must be a JSON object, got {type(parsed).__name__}")
    return parsed


def _validate_loaded_config(config_dict: dict[str, Any], source_path: Path) -> None:
    """Validate a loaded config against the schema with source path in errors.

    Validating on load (not only on write) prevents a hand-edited or
    tampered file from passing through resolve() with arbitrary content
    and failing later at field-access with an opaque error.
    """
    try:
        validate(config_dict)
    except jsonschema.ValidationError as e:
        error_path = "/".join(str(p) for p in e.absolute_path) or "(root)"
        raise RuntimeError(
            f"Config file at {source_path} is schema-invalid:\n"
            f"  Path: {error_path}\n"
            f"  Error: {e.message}"
        ) from e


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    """Deep-merge two dicts.

    Both sides are dicts at the same key -> recurse.
    Either side is a non-dict -> overlay wins wholesale.
    Returns a new dict; does not mutate inputs.
    """
    result = dict(base)
    for key, overlay_value in overlay.items():
        if key in result and isinstance(result[key], dict) and isinstance(overlay_value, dict):
            result[key] = _deep_merge(result[key], overlay_value)
        else:
            result[key] = overlay_value
    return result


def resolve(skill_name: str, *, project_root: Path | None = None) -> dict[str, Any]:
    """Resolve effective config for a skill via global -> project cascade.

    Reads (and validates) ~/.super-model/config.json (global) and
    <project_root>/.super/config.json (per-project, if project_root
    given), extracts the [skill_name] section from each, and deep-merges
    project over global.
    """
    global_path = _global_config_path()
    global_config = _load_json_or_empty(global_path)
    if global_config:
        _validate_loaded_config(global_config, global_path)
    project_config: dict[str, Any] = {}
    if project_root is not None:
        project_path = project_root / _PROJECT_CONFIG_RELATIVE
        project_config = _load_json_or_empty(project_path)
        if project_config:
            _validate_loaded_config(project_config, project_path)
    global_skill_section = global_config.get(skill_name, {})
    project_skill_section = project_config.get(skill_name, {})
    if not isinstance(global_skill_section, dict):
        global_skill_section = {}
    if not isinstance(project_skill_section, dict):
        project_skill_section = {}
    return _deep_merge(global_skill_section, project_skill_section)


def validate(config_dict: dict[str, Any]) -> None:
    """Validate a full config dict against config.schema.json.

    Raises jsonschema.ValidationError on schema violation.
    """
    schema = _load_json_schema(_CONFIG_SCHEMA_PATH)
    jsonschema.validate(instance=config_dict, schema=schema)


def validate_module(frontmatter: dict[str, Any]) -> None:
    """Validate module YAML frontmatter against module-frontmatter.schema.json.

    Raises jsonschema.ValidationError on schema violation.
    """
    schema = _load_json_schema(_MODULE_FRONTMATTER_SCHEMA_PATH)
    jsonschema.validate(instance=frontmatter, schema=schema)


def write_project_config(project_root: Path, config_dict: dict[str, Any]) -> None:
    """Validate config_dict, then atomically write to <project>/.super/config.json.

    Whole-file write; callers that want to patch a single field must
    read the existing config, modify in-memory, and pass the full
    updated dict back to this function.
    """
    validate(config_dict)
    atomic_write_json(project_root / _PROJECT_CONFIG_RELATIVE, config_dict)
