"""Deployment classifier: which AI coding IDE drives this session.

A few Super-Model behaviors are deployment-specific — notably the Claude-only
model / effort / Ultracode policy. This module centralizes the environment-signal
detection that the SessionStart hook (``hooks/session-start``) performs in bash,
so Python tooling, the config resolver, and skill prose share one source of truth.

Precedence mirrors the hook: Cursor is checked before Claude Code because a Cursor
session may also export ``CLAUDE_PLUGIN_ROOT``. The Claude-only policy must not
fire under Cursor, so Cursor wins the tie.
"""

from __future__ import annotations

import os
from collections.abc import Mapping

CLAUDE_CODE = "claude-code"
CURSOR = "cursor"
UNKNOWN = "unknown"


def detect_deployment(env: Mapping[str, str] | None = None) -> str:
    """Classify the active deployment from environment signals.

    Returns ``"cursor"``, ``"claude-code"``, or ``"unknown"``. ``env`` defaults to
    ``os.environ``; pass an explicit mapping for testing.
    """
    env = os.environ if env is None else env
    if env.get("CURSOR_PLUGIN_ROOT"):
        return CURSOR
    if env.get("CLAUDE_PLUGIN_ROOT"):
        return CLAUDE_CODE
    return UNKNOWN


def is_claude_code(env: Mapping[str, str] | None = None) -> bool:
    """True only when the active deployment is Claude Code (gates the Claude policy)."""
    return detect_deployment(env) == CLAUDE_CODE
