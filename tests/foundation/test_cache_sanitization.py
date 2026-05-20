"""HIGH-004: cache filename sanitization (strict allowlist).

Cache marker filenames are built from `purpose` and `key`. Both must
go through `_sanitize_path_component`, which enforces a strict allowlist
to prevent path traversal, NTFS Alternate Data Streams, Windows reserved
device names, and Unicode look-alike confusables.
"""

from __future__ import annotations

import pytest

from scripts.super_lib.cache import _sanitize_path_component


def test_accepts_valid_alphanum_and_dash_underscore() -> None:
    assert _sanitize_path_component("code-review", "purpose") == "code-review"
    assert _sanitize_path_component("abc_123-DEF", "key") == "abc_123-DEF"


def test_rejects_empty() -> None:
    with pytest.raises(ValueError):
        _sanitize_path_component("", "purpose")


def test_rejects_null_byte() -> None:
    with pytest.raises(ValueError):
        _sanitize_path_component("ab\x00cd", "key")


def test_rejects_ntfs_alternate_data_stream() -> None:
    """Windows-specific: `name:stream` is an NTFS Alternate Data Stream
    reference that can be used to hide data behind a normal-looking file."""
    with pytest.raises(ValueError):
        _sanitize_path_component("foo:bar", "key")


def test_rejects_path_separators() -> None:
    with pytest.raises(ValueError):
        _sanitize_path_component("../escape", "key")
    with pytest.raises(ValueError):
        _sanitize_path_component("a/b", "key")
    with pytest.raises(ValueError):
        _sanitize_path_component("a\\b", "key")


@pytest.mark.parametrize(
    "reserved", ["CON", "con", "COM1", "Com1", "LPT9", "lpt9", "PRN", "NUL", "AUX"]
)
def test_rejects_windows_reserved_device_names(reserved: str) -> None:
    with pytest.raises(ValueError):
        _sanitize_path_component(reserved, "key")


def test_rejects_oversized() -> None:
    """Cap at 128 chars to keep filenames manageable across filesystems."""
    with pytest.raises(ValueError):
        _sanitize_path_component("a" * 200, "key")


def test_rejects_unicode_lookalike() -> None:
    """Cyrillic 'а' (U+0430) looks like Latin 'a' but is a different
    character. The allowlist must be ASCII-only to prevent confusables."""
    cyrillic_a = "\u0430"  # looks like 'a'
    with pytest.raises(ValueError):
        _sanitize_path_component(f"co{cyrillic_a}de-review", "purpose")


def test_rejects_dotfile() -> None:
    """Leading '.' would create a hidden file on POSIX - confusing semantics."""
    with pytest.raises(ValueError):
        _sanitize_path_component(".hidden", "key")
