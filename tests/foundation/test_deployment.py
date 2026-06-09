"""Deployment classifier tests.

The classifier centralizes the env-signal detection the SessionStart hook does in
bash. Precedence mirrors the hook: Cursor is checked before Claude Code because a
Cursor session may also export CLAUDE_PLUGIN_ROOT.
"""

from __future__ import annotations

from scripts.super_lib.deployment import (
    CLAUDE_CODE,
    CURSOR,
    UNKNOWN,
    detect_deployment,
    is_claude_code,
)


def test_claude_code_detected():
    env = {"CLAUDE_PLUGIN_ROOT": "/plugins/claude"}
    assert detect_deployment(env) == CLAUDE_CODE
    assert is_claude_code(env)


def test_cursor_only():
    assert detect_deployment({"CURSOR_PLUGIN_ROOT": "/plugins/cursor"}) == CURSOR


def test_cursor_takes_precedence_over_claude():
    # A Cursor session may also set CLAUDE_PLUGIN_ROOT; Cursor must win (matches
    # hooks/session-start ordering), so the Claude-only policy never fires there.
    env = {"CURSOR_PLUGIN_ROOT": "/c", "CLAUDE_PLUGIN_ROOT": "/x"}
    assert detect_deployment(env) == CURSOR
    assert not is_claude_code(env)


def test_unknown_when_no_signal():
    assert detect_deployment({}) == UNKNOWN
    assert not is_claude_code({})
