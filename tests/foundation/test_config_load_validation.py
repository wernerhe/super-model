"""HIGH-006: config validation on LOAD, not just on write.

A hand-edited bad config must be rejected at the resolve point with a
clear, actionable error message that includes the offending file path.
The resolver must NOT silently degrade to an empty / default config -
fail-fast is the contract.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.super_lib.config import resolve


def test_invalid_global_config_raises_with_path(tmp_project: Path, tmp_global_home: Path) -> None:
    super_model_dir = tmp_global_home / ".super-model"
    super_model_dir.mkdir(parents=True, exist_ok=True)
    # Schema-invalid: module entry is a string, not a dict.
    (super_model_dir / "config.json").write_text(
        json.dumps({"super-code-review": "not-a-dict"}),
        encoding="utf-8",
    )

    with pytest.raises(Exception) as exc_info:
        resolve("super-code-review", project_root=tmp_project)

    msg = str(exc_info.value)
    # The error must mention the global config file path so the user
    # knows what to fix.
    assert "config.json" in msg or "global" in msg.lower()


def test_invalid_project_config_raises_with_path(tmp_project: Path, tmp_global_home: Path) -> None:
    # Schema-invalid project config.
    (tmp_project / ".super" / "config.json").write_text(
        json.dumps({"super-code-review": "not-a-dict"}),
        encoding="utf-8",
    )

    with pytest.raises(Exception) as exc_info:
        resolve("super-code-review", project_root=tmp_project)

    msg = str(exc_info.value)
    assert "config.json" in msg or str(tmp_project) in msg


def test_resolver_does_not_silently_degrade(tmp_project: Path, tmp_global_home: Path) -> None:
    """A malformed project config must NOT produce an empty result; it
    must raise. Silent degradation hides the bug from the user."""
    (tmp_project / ".super" / "config.json").write_text("this is not json at all", encoding="utf-8")
    with pytest.raises((ValueError, RuntimeError, OSError)):
        resolve("super-code-review", project_root=tmp_project)
