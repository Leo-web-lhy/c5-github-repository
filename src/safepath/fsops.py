"""Filesystem operations that behave the same on Windows and POSIX.

Motivation: on Windows a read-only attribute — which ``.git`` object files and
many extracted archives carry — makes ``os.replace`` fail with
``PermissionError`` (errno 13 / EPERM). POSIX has no such attribute and the
same code path silently succeeds, so the bug only shows up on one platform.
``atomic_replace`` closes that gap.
"""

from __future__ import annotations

import os
import stat
import time
from typing import Dict, Optional

#: Usable character budget of a legacy Windows path, terminator excluded.
WIN_MAX_PATH = 260


def clear_readonly(path: str) -> bool:
    """Make *path* writable when it exists and is currently read-only.

    Returns ``True`` when the attribute was changed, ``False`` when nothing had
    to be done (missing file or already writable). The write bit of a
    directory is required to create or delete entries inside it, so the same
    helper also unblocks directory cleanup.
    """
    text = os.fspath(path)
    if not os.path.exists(text):
        return False
    mode = os.stat(text).st_mode
    if mode & stat.S_IWRITE:
        return False
    os.chmod(text, mode | stat.S_IWRITE | stat.S_IREAD)
    return True


def atomic_replace(
    src: str,
    dst: str,
    retries: int = 3,
    delay: float = 0.05,
) -> str:
    """Replace *dst* with *src* atomically, tolerating the Windows read-only bit.

    Args:
        src: Existing source file.
        dst: Destination path, replaced in one step.
        retries: Total attempts; values below 1 are treated as 1.
        delay: Seconds to sleep between attempts.

    Returns:
        The destination path.

    Raises:
        PermissionError: the last permission error, when every attempt failed.
    """
    src_text = os.fspath(src)
    dst_text = os.fspath(dst)
    attempts = max(1, int(retries))
    clear_readonly(dst_text)

    last_error: Optional[PermissionError] = None
    for attempt in range(attempts):
        try:
            os.replace(src_text, dst_text)
            return dst_text
        except PermissionError as exc:
            last_error = exc
            clear_readonly(dst_text)
            if attempt + 1 < attempts:
                time.sleep(delay)

    if last_error is not None:
        raise last_error
    raise PermissionError("replace failed without an error object: %r" % (dst_text,))


def check_path_length(path: str, limit: int = WIN_MAX_PATH) -> Dict[str, object]:
    """Report whether the absolute form of *path* fits a MAX_PATH budget.

    The check uses a strict ``<`` comparison because the terminator occupies
    the final slot of the documented 260-character limit.

    Returns a mapping with ``path``, ``length``, ``limit``, ``ok`` and, when the
    budget is exceeded on Windows, a ``suggested`` long-path form. On POSIX the
    value of ``suggested`` is ``None`` because there is no such prefix.
    """
    absolute = os.path.abspath(os.fspath(path))
    length = len(absolute)
    result: Dict[str, object] = {
        "path": absolute,
        "length": length,
        "limit": limit,
        "ok": length < limit,
        "suggested": None,
    }
    if not result["ok"] and os.name == "nt" and not absolute.startswith("\\\\?\\"):
        result["suggested"] = "\\\\?\\" + absolute
    return result
