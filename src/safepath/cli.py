"""Command line interface for :mod:`safepath`."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from . import __version__
from .collision import find_collisions
from .errors import SafePathError
from .fsops import WIN_MAX_PATH, check_path_length
from .join import safe_join
from .sanitize import sanitize_filename

EXIT_OK = 0
EXIT_FINDING = 1
EXIT_INVALID = 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="safepath",
        description="Cross-platform safe path utilities (sanitize, join, collide, length).",
        epilog="Exit codes: 0 ok, 1 finding reported, 2 invalid input.",
    )
    parser.add_argument("--version", action="version", version="safepath " + __version__)
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("sanitize", help="turn arbitrary strings into safe filenames")
    p.add_argument("names", nargs="+", help="one or more raw names")
    p.add_argument("--replacement", default="_", help="character used for illegal ones")
    p.add_argument("--max-length", type=int, default=255, help="length cap per name")

    p = sub.add_parser("join", help="join path parts, refusing to escape the base")
    p.add_argument("base", help="base directory that must contain the result")
    p.add_argument("parts", nargs="+", help="relative path fragments")

    p = sub.add_parser("collide", help="report names colliding after case/Unicode folding")
    p.add_argument("names", nargs="+", help="names to compare")
    p.add_argument("--case-sensitive", action="store_true", help="keep letter case")
    p.add_argument("--no-normalize", action="store_true", help="skip Unicode normalization")

    p = sub.add_parser("length", help="check a path against a MAX_PATH-style budget")
    p.add_argument("path", help="path to measure")
    p.add_argument("--limit", type=int, default=WIN_MAX_PATH, help="character budget")
    return parser


def _run_sanitize(args: argparse.Namespace) -> int:
    results = [
        sanitize_filename(name, replacement=args.replacement, max_length=args.max_length)
        for name in args.names
    ]
    if args.json:
        print(json.dumps({"sanitized": results}, ensure_ascii=False))
    else:
        for name in results:
            print(name)
    return EXIT_OK


def _run_join(args: argparse.Namespace) -> int:
    joined = safe_join(args.base, *args.parts)
    if args.json:
        print(json.dumps({"joined": joined}, ensure_ascii=False))
    else:
        print(joined)
    return EXIT_OK


def _run_collide(args: argparse.Namespace) -> int:
    groups = find_collisions(
        args.names,
        case_sensitive=args.case_sensitive,
        normalize=not args.no_normalize,
    )
    if args.json:
        print(json.dumps({"collisions": groups}, ensure_ascii=False))
    elif not groups:
        print("no collisions")
    else:
        for key in groups:
            print("%s: %s" % (key, ", ".join(groups[key])))
    return EXIT_FINDING if groups else EXIT_OK


def _run_length(args: argparse.Namespace) -> int:
    info = check_path_length(args.path, limit=args.limit)
    if args.json:
        print(json.dumps(info, ensure_ascii=False))
    else:
        state = "ok" if info["ok"] else "over budget"
        print("%d/%d %s" % (info["length"], info["limit"], state))
        if info.get("suggested"):
            print("suggested: %s" % info["suggested"])
    return EXIT_OK if info["ok"] else EXIT_FINDING


_HANDLERS = {
    "sanitize": _run_sanitize,
    "join": _run_join,
    "collide": _run_collide,
    "length": _run_length,
}


def main(argv: Optional[List[str]] = None) -> int:
    """Entry point; returns a process exit code instead of raising."""
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = _HANDLERS[args.command]
    try:
        return handler(args)
    except SafePathError as exc:
        print("safepath: %s" % exc, file=sys.stderr)
        return EXIT_INVALID


if __name__ == "__main__":
    raise SystemExit(main())
