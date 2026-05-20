"""Heavyweight behavioral suite for super-model-setup.py.

Asserts the full install-script contract from first-install through
re-run idempotency, drift detection, and CLAUDE.md / config / gitignore
preservation. The script is invoked via subprocess so we test what
users actually experience (not the importable surface).
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SUPER_ROOT = Path(__file__).resolve().parents[2]
SETUP_SCRIPT = SUPER_ROOT / "super-model-setup.py"


def _run_setup(target: Path, env_overrides: dict | None = None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)
    return subprocess.run(
        [sys.executable, str(SETUP_SCRIPT), str(target)],
        capture_output=True,
        text=True,
        env=env,
    )


# ---------------------------------------------------------------------------
# First-install behaviors
# ---------------------------------------------------------------------------


def test_first_install_creates_expected_artifacts(tmp_path: Path) -> None:
    result = _run_setup(tmp_path)
    assert result.returncode == 0, f"stderr: {result.stderr}"

    assert (tmp_path / "CLAUDE.md").exists()
    assert (tmp_path / ".super" / "config.json").exists()
    assert (tmp_path / ".gitignore").exists()
    assert (tmp_path / ".mcp.json").exists()
    assert (tmp_path / ".claude" / "settings.json").exists()


def test_first_install_writes_seven_slash_commands_per_ide(tmp_path: Path) -> None:
    _run_setup(tmp_path)
    for ide_dir in [
        tmp_path / ".claude" / "commands",
        tmp_path / ".windsurf" / "workflows",
        tmp_path / ".clinerules" / "workflows",
    ]:
        files = list(ide_dir.glob("super-*.md"))
        assert len(files) == 7, f"expected 7 files in {ide_dir}, got {len(files)}"


def test_first_install_writes_always_on_rule_per_ide(tmp_path: Path) -> None:
    _run_setup(tmp_path)
    assert (tmp_path / ".windsurf" / "rules" / "super-model.md").exists()
    assert (tmp_path / ".clinerules" / "super-model.md").exists()


# ---------------------------------------------------------------------------
# Idempotency
# ---------------------------------------------------------------------------


def test_rerun_is_idempotent(tmp_path: Path) -> None:
    _run_setup(tmp_path)
    # Re-run: every module should report "already present" / similar -
    # the install is fully idempotent.
    result = _run_setup(tmp_path)
    assert result.returncode == 0
    # Files that did NOT change should preserve mtime; the script reports
    # "already present" for each module on re-run.
    assert (
        "already present" in result.stdout
        or "already configured" in result.stdout
        or "no changes" in result.stdout.lower()
        or "already installed" in result.stdout
    )


# ---------------------------------------------------------------------------
# Preservation guarantees
# ---------------------------------------------------------------------------


def test_existing_claude_md_preserved(tmp_path: Path) -> None:
    """Pre-existing CLAUDE.md with user content must NOT be clobbered.
    The Installation Policy section is appended only if missing."""
    user_content = "# My Custom Guidance\n\nUser-specific rules here.\n"
    (tmp_path / "CLAUDE.md").write_text(user_content, encoding="utf-8")

    _run_setup(tmp_path)

    final = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "My Custom Guidance" in final, "user content was clobbered"
    # Installation Policy may have been appended.


def test_existing_super_config_preserved(tmp_path: Path) -> None:
    super_dir = tmp_path / ".super"
    super_dir.mkdir(parents=True)
    user_config = {"super-code-review": {"preset": "fast"}}
    (super_dir / "config.json").write_text(json.dumps(user_config), encoding="utf-8")

    _run_setup(tmp_path)

    final = json.loads((super_dir / "config.json").read_text(encoding="utf-8"))
    assert final == user_config, "user-edited config was overwritten"


def test_gitignore_dedups(tmp_path: Path) -> None:
    """Pre-existing canonical entries should not be duplicated."""
    (tmp_path / ".gitignore").write_text(
        ".super/cache/\n.worktrees/\nnode_modules/\n", encoding="utf-8"
    )
    _run_setup(tmp_path)
    text = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    assert text.count(".super/cache/") == 1
    assert text.count(".worktrees/") == 1
    assert "node_modules/" in text  # user entries preserved


# ---------------------------------------------------------------------------
# Drift detection
# ---------------------------------------------------------------------------


def test_user_edited_slash_command_preserved(tmp_path: Path) -> None:
    """If the user edits the BODY of a slash command shim, re-running
    setup must NOT clobber the user's edit. The drift-detection heuristic
    compares body past frontmatter."""
    _run_setup(tmp_path)
    shim = tmp_path / ".claude" / "commands" / "super-brainstorm.md"
    original = shim.read_text(encoding="utf-8")
    # User edits the body.
    edited = original.replace(
        "Use the super-brainstorm skill",
        "Use the super-brainstorm skill -- USER EDIT HERE --",
    )
    shim.write_text(edited, encoding="utf-8")

    _run_setup(tmp_path)

    after = shim.read_text(encoding="utf-8")
    assert "USER EDIT HERE" in after, "user edit was clobbered by re-install"


# ---------------------------------------------------------------------------
# Drive-root refusal
# ---------------------------------------------------------------------------


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX root test")
def test_drive_root_refusal_posix() -> None:
    """POSIX: invoking with target=/ must fail fast."""
    result = subprocess.run(
        [sys.executable, str(SETUP_SCRIPT), "/"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "root" in (result.stdout + result.stderr).lower()


@pytest.mark.skipif(sys.platform != "win32", reason="Windows root test")
def test_drive_root_refusal_windows() -> None:
    """Windows: invoking with target=C:\\ must fail fast."""
    result = subprocess.run(
        [sys.executable, str(SETUP_SCRIPT), "C:\\"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    combined = (result.stdout + result.stderr).lower()
    assert "root" in combined


# ---------------------------------------------------------------------------
# settings.json merge semantics
# ---------------------------------------------------------------------------


def test_settings_json_merge_preserves_existing_hooks(tmp_path: Path) -> None:
    """Pre-existing hooks must not be removed when we add ours."""
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir(parents=True)
    pre_existing = {
        "hooks": {
            "SessionStart": [
                {
                    "matcher": "startup",
                    "hooks": [{"type": "command", "command": "my-custom-hook"}],
                }
            ]
        }
    }
    (claude_dir / "settings.json").write_text(json.dumps(pre_existing), encoding="utf-8")

    _run_setup(tmp_path)

    final = json.loads((claude_dir / "settings.json").read_text(encoding="utf-8"))
    # Custom hook must still be there.
    found_custom = False
    for entry in final.get("hooks", {}).get("SessionStart", []):
        for h in entry.get("hooks", []):
            if h.get("command") == "my-custom-hook":
                found_custom = True
    assert found_custom, "user's pre-existing SessionStart hook was removed"


# ---------------------------------------------------------------------------
# Output format
# ---------------------------------------------------------------------------


def test_output_includes_source_and_target_paths(tmp_path: Path) -> None:
    """Summary output starts with source: and target: lines so users can
    confirm the install is going to the right place."""
    result = _run_setup(tmp_path)
    assert "source:" in result.stdout
    assert "target:" in result.stdout
    assert str(tmp_path) in result.stdout
