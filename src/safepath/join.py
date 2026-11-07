"""Join path parts without ever escaping the base directory.

``os.path.join`` is a foot-gun for untrusted input: any absolute component
silently discards everything joined before it, and ``..`` segments walk up the
tree. The helpers below keep the result inside a stated base or fail loudly.
"""

from __future__ import annotations

import os
import re

from .errors import UnsafePathError

_DRIVE_RE = re.compile(r"^[A-Za-z]:")


def is_within(base: str, target: str) -> bool:
    """Return ``True`` when *target* resolves inside *base*.

    Both sides are resolved with :func:`os.path.abspath`, so relative inputs are
    interpreted against the current working directory. Paths on different
    Windows drives never count as contained.
    """
    base_abs = os.path.abspath(os.fspath(base))
    target_abs = os.path.abspath(os.fspath(target))
    try:
        return os.path.commonpath([base_abs, target_abs]) == base_abs
    except ValueError:
        return False


def safe_join(base: str, *parts: str, allow_absolute: bool = False) -> str:
    """Join *parts* onto *base*, refusing anything that leaves *base*.

    Args:
        base: Directory that the result must stay inside.
        *parts: Path components, either relative fragments or single names.
        allow_absolute: Permit absolute components (still containment-checked).

    Raises:
        UnsafePathError: on ``..`` escapes, NUL bytes, absolute components,
            Windows UNC paths, or drive-relative components such as ``C:evil``.

    Notes:
        Drive-relative components are rejected on *every* platform, not just on
        Windows. That keeps validation deterministic: a path that passes here
        on Linux cannot suddenly become dangerous when the same data is
        processed on Windows later.

    Examples:
        >>> safe_join('/srv/data', 'reports', 'q1.csv')
        '/srv/data/reports/q1.csv'
        >>> safe_join('/srv/data', '../etc/passwd')
        Traceback (most recent call last):
        ...
        safepath.errors.UnsafePathError: component '../etc/passwd' escapes base '/srv/data'
    """
    base_text = os.fspath(base)
    if "\x00" in base_text:
        raise UnsafePathError("base contains a NUL byte")

    checked = []
    for part in parts:
        text = os.fspath(part)
        if "\x00" in text:
            raise UnsafePathError("component contains a NUL byte")
        if not allow_absolute:
            if os.path.isabs(text) or _DRIVE_RE.match(text) or text.startswith("\\\\"):
                raise UnsafePathError(
                    "component %r must be relative to base %r" % (text, base_text)
                )
        checked.append(text)

    candidate = os.path.normpath(os.path.join(base_text, *checked))
    if not is_within(base_text, candidate):
        raise UnsafePathError(
            "resolved path %r escapes base %r" % (candidate, base_text)
        )
    return candidate
