"""Exception types raised by :mod:`safepath`."""

from __future__ import annotations


class SafePathError(ValueError):
    """Base class for every error raised by this package.

    Inherits from :class:`ValueError` so callers that already treat invalid
    input as a value error keep working without importing this module.
    """


class InvalidNameError(SafePathError):
    """Raised when a single path component cannot be salvaged.

    This happens when the input is empty, only whitespace, ``.``, or ``..`` —
    there is no correct filename to derive from it.
    """


class UnsafePathError(SafePathError):
    """Raised when a path would escape its base directory.

    Typical causes: ``..`` segments that climb above the base, absolute
    paths, UNC paths, or Windows drive-relative paths such as ``C:evil``.
    """
