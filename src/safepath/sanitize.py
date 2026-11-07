"""Turn arbitrary strings into filenames that are legal on every platform.

The rules encoded here come from the intersection of what Windows, macOS and
Linux accept, so a name sanitized once stays valid after the file is copied to
another operating system.
"""

from __future__ import annotations

import re

from .errors import InvalidNameError

#: Characters rejected by NTFS. ``/`` and ``\\`` are treated as illegal on
#: every platform because they are separators somewhere and therefore act as
#: path traversal vectors.
FORBIDDEN_CHARS: frozenset = frozenset('<>:"/\\|?*')

#: Windows reserves these device names; opening ``CON.txt`` talks to a console
#: device rather than to a regular file.
RESERVED_NAMES: frozenset = frozenset(
    ["CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"]
    + ["COM%d" % i for i in range(1, 10)]
    + ["LPT%d" % i for i in range(1, 10)]
)

_CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")
_TRAILING_NOISE = " ."


def is_reserved_name(name: str) -> bool:
    """Return ``True`` when *name* (any extension) targets a Windows device."""
    if not isinstance(name, str):
        raise TypeError("name must be a str")
    return name.split(".")[0].strip().upper() in RESERVED_NAMES


def _truncate(name: str, max_length: int, keep_extension: bool) -> str:
    if not keep_extension:
        return name[:max_length]
    stem, dot, ext = name.rpartition(".")
    if not dot or not stem:
        return name[:max_length]
    budget = max_length - len(ext) - 1
    if budget <= 0:
        return name[:max_length]
    return stem[:budget] + "." + ext


def sanitize_filename(
    name: str,
    replacement: str = "_",
    max_length: int = 255,
    keep_extension: bool = True,
) -> str:
    """Return a filename derived from *name* that is safe on every platform.

    Args:
        name: Raw input, typically a document title or a downloaded filename.
        replacement: Inserted in place of every illegal character.
        max_length: Maximum length of the returned name in characters.
        keep_extension: When truncating, keep the trailing extension intact.

    Raises:
        InvalidNameError: if nothing usable is left (empty, whitespace only,
            ``.`` or ``..``).
        TypeError: if *name* is not a string.
        ValueError: if *max_length* is not positive.

    Examples:
        >>> sanitize_filename('a/b:c?.txt')
        'a_b_c_.txt'
        >>> sanitize_filename('CON.txt')
        '_CON.txt'
        >>> sanitize_filename('report.md ')
        'report.md'
    """
    if not isinstance(name, str):
        raise TypeError("name must be a str, got %r" % (type(name).__name__,))
    if max_length <= 0:
        raise ValueError("max_length must be positive")

    cleaned = _CONTROL_RE.sub(replacement, name)
    for char in FORBIDDEN_CHARS:
        cleaned = cleaned.replace(char, replacement)
    cleaned = cleaned.rstrip(_TRAILING_NOISE)

    if cleaned in ("", ".", ".."):
        raise InvalidNameError("no usable filename in %r" % (name,))

    if is_reserved_name(cleaned):
        cleaned = (replacement or "_") + cleaned

    if len(cleaned) > max_length:
        cleaned = _truncate(cleaned, max_length, keep_extension).rstrip(_TRAILING_NOISE)
        if not cleaned:
            raise InvalidNameError("cannot shorten %r into a usable filename" % (name,))

    return cleaned
