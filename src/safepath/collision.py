"""Detect filenames that collide only after case or Unicode folding.

Silent data loss on case-insensitive filesystems (Windows, default macOS) and
on filesystems that normalize Unicode differently is a recurring bug: two
entries look distinct in the listing yet map to one inode. This module reports
those groups before anything is written.
"""

from __future__ import annotations

import unicodedata
from typing import Dict, Iterable, List

from .errors import SafePathError

_FORM_CHOICES = ("NFC", "NFD", "NFKC", "NFKD")


def fold_name(
    name: str,
    case_sensitive: bool = False,
    normalize: bool = True,
    form: str = "NFC",
) -> str:
    """Return the comparison key used to decide whether two names collide.

    Args:
        name: Filename or path component.
        case_sensitive: Keep letter case when ``True``.
        normalize: Apply Unicode normalization when ``True``.
        form: One of ``NFC``, ``NFD``, ``NFKC``, ``NFKD``.

    Raises:
        TypeError: if *name* is not a string.
        SafePathError: if *form* is not a supported normalization form.
    """
    if not isinstance(name, str):
        raise TypeError("name must be a str")
    if form not in _FORM_CHOICES:
        raise SafePathError("unsupported normalization form %r" % (form,))

    folded = unicodedata.normalize(form, name) if normalize else name
    if not case_sensitive:
        folded = folded.casefold()
    return folded


def find_collisions(
    names: Iterable[str],
    case_sensitive: bool = False,
    normalize: bool = True,
    form: str = "NFC",
) -> Dict[str, List[str]]:
    """Group *names* by folded key and return only the groups with 2+ entries.

    The returned mapping is ordered by key and each group keeps the original
    input order, so output is stable across runs.

    Examples:
        >>> find_collisions(['README.md', 'readme.md'])
        {'readme.md': ['README.md', 'readme.md']}
    """
    groups: Dict[str, List[str]] = {}
    for name in names:
        key = fold_name(name, case_sensitive=case_sensitive, normalize=normalize, form=form)
        groups.setdefault(key, []).append(name)
    return {key: groups[key] for key in sorted(groups) if len(groups[key]) > 1}
