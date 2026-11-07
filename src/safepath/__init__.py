"""safepath — cross-platform safe path handling.

Four problems, one small dependency-free library:

* :func:`~safepath.sanitize.sanitize_filename` — arbitrary text to legal filename
* :func:`~safepath.join.safe_join` — traversal-proof path joining
* :func:`~safepath.collision.find_collisions` — case / Unicode collisions
* :func:`~safepath.fsops.atomic_replace` — replace files despite the Windows
  read-only attribute
"""

from .collision import find_collisions, fold_name
from .errors import InvalidNameError, SafePathError, UnsafePathError
from .fsops import WIN_MAX_PATH, atomic_replace, check_path_length, clear_readonly
from .join import is_within, safe_join
from .sanitize import (
    FORBIDDEN_CHARS,
    RESERVED_NAMES,
    is_reserved_name,
    sanitize_filename,
)

__version__ = "1.0.0"

__all__ = [
    "FORBIDDEN_CHARS",
    "InvalidNameError",
    "RESERVED_NAMES",
    "SafePathError",
    "UnsafePathError",
    "WIN_MAX_PATH",
    "__version__",
    "atomic_replace",
    "check_path_length",
    "clear_readonly",
    "find_collisions",
    "fold_name",
    "is_reserved_name",
    "is_within",
    "safe_join",
    "sanitize_filename",
]
