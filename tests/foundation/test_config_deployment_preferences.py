"""deployment_preferences config block + resolver (Thread B step 13).

The schema gains a per-deployment preferences block; the resolver returns Layer-1
baked Claude defaults deep-merged with config overrides, and {} for non-Claude
deployments so the Claude-only policy never leaks to Cursor/Windsurf.
"""

from __future__ import annotations

import json

import jsonschema
import pytest

from scripts.super_lib.config import deployment_preferences, validate

CLAUDE_ENV = {"CLAUDE_PLUGIN_ROOT": "/x"}
CURSOR_ENV = {"CURSOR_PLUGIN_ROOT": "/c"}


# ---- schema ----


def test_schema_accepts_deployment_preferences_block():
    validate(
        {
            "super-execute": {
                "deployment_preferences": {
                    "claude-code": {"backend": "parallel-dispatch", "implementer_model": "opus"}
                }
            }
        }
    )


def test_schema_rejects_unknown_key_in_deployment_prefs():
    with pytest.raises(jsonschema.ValidationError):
        validate({"super-execute": {"deployment_preferences": {"claude-code": {"bogus": 1}}}})


def test_schema_rejects_unknown_deployment():
    with pytest.raises(jsonschema.ValidationError):
        validate({"super-execute": {"deployment_preferences": {"emacs": {"backend": "x"}}}})


# ---- resolver ----


def test_execute_claude_baked_defaults(tmp_global_home):
    prefs = deployment_preferences("super-execute", env=CLAUDE_ENV)
    assert prefs["backend"] == "parallel-dispatch"
    assert prefs["implementer_model"] == "opus"
    assert prefs["effort"] == "xhigh"


def test_brainstorm_claude_baked_defaults(tmp_global_home):
    assert deployment_preferences("super-brainstorm", env=CLAUDE_ENV) == {
        "model": "opus",
        "effort": "xhigh",
    }


def test_non_claude_deployment_returns_empty(tmp_global_home):
    assert deployment_preferences("super-execute", env=CURSOR_ENV) == {}


def test_project_config_overrides_baked_default(tmp_project, tmp_global_home):
    cfg = tmp_project / ".super" / "config.json"
    cfg.write_text(
        json.dumps(
            {
                "super-execute": {
                    "deployment_preferences": {"claude-code": {"implementer_model": "sonnet"}}
                }
            }
        ),
        encoding="utf-8",
    )
    prefs = deployment_preferences("super-execute", project_root=tmp_project, env=CLAUDE_ENV)
    assert prefs["implementer_model"] == "sonnet"  # project override wins
    assert prefs["backend"] == "parallel-dispatch"  # baked default still present
