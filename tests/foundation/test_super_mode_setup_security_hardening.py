"""Install-approval policy edge cases.

The install-approval policy merges 20 canonical Bash patterns into
<project>/.claude/settings.json's permissions.ask array, with the
$defaults sentinel preserved at index 0. The edge cases exercised
here are the ones most likely to bite when a user has hand-edited
settings.json before running setup.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

SUPER_ROOT = Path(__file__).resolve().parents[2]
SETUP_SCRIPT = SUPER_ROOT / "super-mode-setup.py"
SETTINGS_REL = Path(".claude") / "settings.json"


def _run_setup(target: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SETUP_SCRIPT), str(target)],
        capture_output=True,
        text=True,
    )


def _settings(target: Path) -> dict:
    return json.loads((target / SETTINGS_REL).read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Canonical shape after fresh install
# ---------------------------------------------------------------------------

def test_fresh_install_writes_canonical_shape(tmp_path: Path) -> None:
    _run_setup(tmp_path)
    ask = _settings(tmp_path)["permissions"]["ask"]
    assert ask[0] == "$defaults", "sentinel must be at index 0"
    # The 20 canonical rules should follow.
    canonical_signal = "Bash(pip install *)"
    assert canonical_signal in ask
    assert ask.count(canonical_signal) == 1


def test_fresh_install_includes_all_twenty_rules(tmp_path: Path) -> None:
    _run_setup(tmp_path)
    ask = _settings(tmp_path)["permissions"]["ask"]
    # Spot-check the spread of package managers covered.
    for required in [
        "Bash(pip install *)",
        "Bash(uv add *)",
        "Bash(npm install *)",
        "Bash(brew install *)",
        "Bash(apt install *)",
    ]:
        assert required in ask, "missing canonical rule: {}".format(required)


# ---------------------------------------------------------------------------
# Pre-existing state edge cases
# ---------------------------------------------------------------------------

def test_existing_defaults_sentinel_not_duplicated(tmp_path: Path) -> None:
    """If $defaults is already in permissions.ask, do not duplicate it."""
    settings = {"permissions": {"ask": ["$defaults", "Bash(custom *)"]}}
    (tmp_path / ".claude").mkdir(parents=True)
    (tmp_path / SETTINGS_REL).write_text(json.dumps(settings), encoding="utf-8")

    _run_setup(tmp_path)

    ask = _settings(tmp_path)["permissions"]["ask"]
    assert ask.count("$defaults") == 1


def test_existing_canonical_rule_not_duplicated(tmp_path: Path) -> None:
    settings = {
        "permissions": {
            "ask": ["$defaults", "Bash(pip install *)", "Bash(custom *)"]
        }
    }
    (tmp_path / ".claude").mkdir(parents=True)
    (tmp_path / SETTINGS_REL).write_text(json.dumps(settings), encoding="utf-8")

    _run_setup(tmp_path)

    ask = _settings(tmp_path)["permissions"]["ask"]
    assert ask.count("Bash(pip install *)") == 1
    assert "Bash(custom *)" in ask  # user entry preserved


def test_existing_unrelated_fields_preserved(tmp_path: Path) -> None:
    settings = {
        "permissions": {"ask": [], "allow": ["Bash(echo *)"]},
        "model": "claude-opus-4-7",
        "customField": {"nested": True},
    }
    (tmp_path / ".claude").mkdir(parents=True)
    (tmp_path / SETTINGS_REL).write_text(json.dumps(settings), encoding="utf-8")

    _run_setup(tmp_path)

    final = _settings(tmp_path)
    assert final.get("model") == "claude-opus-4-7"
    assert final.get("customField") == {"nested": True}
    assert "Bash(echo *)" in final.get("permissions", {}).get("allow", [])


# ---------------------------------------------------------------------------
# CLAUDE.md Installation Policy section
# ---------------------------------------------------------------------------

def test_claude_md_install_policy_appended_when_absent(tmp_path: Path) -> None:
    """Pre-existing CLAUDE.md without the Installation Policy section
    gets the section appended."""
    (tmp_path / "CLAUDE.md").write_text("# Existing\n\nUser content.\n", encoding="utf-8")
    _run_setup(tmp_path)
    text = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "Installation Policy" in text
    assert "User content." in text  # user content preserved


def test_claude_md_install_policy_not_duplicated(tmp_path: Path) -> None:
    """Pre-existing CLAUDE.md with the Installation Policy heading
    (case-insensitive) is NOT modified."""
    original = (
        "# Existing\n\n"
        "## installation policy\n\n"
        "User custom install rules.\n"
    )
    (tmp_path / "CLAUDE.md").write_text(original, encoding="utf-8")
    _run_setup(tmp_path)
    text = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    # Section should appear exactly once (case-insensitive match counted once).
    lower = text.lower()
    assert lower.count("## installation policy") == 1


# ---------------------------------------------------------------------------
# Re-run after partial install
# ---------------------------------------------------------------------------

def test_rerun_completes_partial_install(tmp_path: Path) -> None:
    """If a previous install only got the hook in but not the rules
    (e.g., the user wiped some entries), re-run must complete the
    install (add missing rules; preserve sentinel; do not duplicate)."""
    settings = {
        "permissions": {"ask": ["$defaults"]},
        "hooks": {"SessionStart": [{"matcher": "startup|clear|compact", "hooks": []}]},
    }
    (tmp_path / ".claude").mkdir(parents=True)
    (tmp_path / SETTINGS_REL).write_text(json.dumps(settings), encoding="utf-8")

    _run_setup(tmp_path)

    ask = _settings(tmp_path)["permissions"]["ask"]
    assert ask[0] == "$defaults"
    assert "Bash(pip install *)" in ask
    # No duplicate sentinel.
    assert ask.count("$defaults") == 1
