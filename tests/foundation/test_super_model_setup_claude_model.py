"""Claude model/effort settings seed.

super-model-setup seeds `model` and `effortLevel` into <project>/.claude/
settings.json so a Claude deployment defaults to current Opus at the highest
persistent reasoning effort. The seed is absent-only: an architect-set value is
preserved. Verified Claude Code keys (code.claude.com): model alias "opus";
effortLevel "xhigh" (highest persistent; "max" is session-only).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SUPER_ROOT = Path(__file__).resolve().parents[2]
SETUP_SCRIPT = SUPER_ROOT / "super-model-setup.py"
SETTINGS_REL = Path(".claude") / "settings.json"


def _run_setup(target: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SETUP_SCRIPT), str(target)], capture_output=True, text=True
    )


def _settings(target: Path) -> dict:
    return json.loads((target / SETTINGS_REL).read_text(encoding="utf-8"))


def _seed_settings(target: Path, settings: dict) -> None:
    (target / ".claude").mkdir(parents=True)
    (target / SETTINGS_REL).write_text(json.dumps(settings), encoding="utf-8")


def test_fresh_install_seeds_model_and_effort(tmp_path: Path) -> None:
    _run_setup(tmp_path)
    s = _settings(tmp_path)
    assert s.get("model") == "opus"
    assert s.get("effortLevel") == "xhigh"


def test_existing_model_and_effort_preserved(tmp_path: Path) -> None:
    _seed_settings(tmp_path, {"model": "claude-opus-4-7", "effortLevel": "high"})
    _run_setup(tmp_path)
    s = _settings(tmp_path)
    assert s["model"] == "claude-opus-4-7"  # preserved, not overwritten
    assert s["effortLevel"] == "high"


def test_partial_existing_seeds_only_missing_key(tmp_path: Path) -> None:
    _seed_settings(tmp_path, {"model": "sonnet"})  # effortLevel absent
    _run_setup(tmp_path)
    s = _settings(tmp_path)
    assert s["model"] == "sonnet"  # preserved
    assert s["effortLevel"] == "xhigh"  # seeded


def test_seed_does_not_disturb_other_settings(tmp_path: Path) -> None:
    _seed_settings(tmp_path, {"permissions": {"allow": ["Bash(echo *)"]}})
    _run_setup(tmp_path)
    s = _settings(tmp_path)
    assert "Bash(echo *)" in s["permissions"]["allow"]
    assert s["model"] == "opus"
