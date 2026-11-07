"""Allow ``python -m safepath`` to behave like the ``safepath`` console script."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
