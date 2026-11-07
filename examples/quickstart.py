#!/usr/bin/env python3
"""Quickstart: the four things safepath does, run end to end.

Run from the repo root:

    python examples/quickstart.py

The script writes only ASCII status lines to the console on purpose: on some
Windows consoles, printing non-ASCII text from Python can abort the process
with 0xC0000005 before any traceback is raised. File contents stay UTF-8.
"""

from __future__ import annotations

import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from safepath import (  # noqa: E402
    UnsafePathError,
    atomic_replace,
    check_path_length,
    find_collisions,
    safe_join,
    sanitize_filename,
)


def step(title):
    print("== " + title)


def main():
    step("1. sanitize: any string -> a legal filename")
    raw_names = [
        "../../etc/passwd",
        "CON.txt",
        "?? report ...",
        "a" * 300 + ".csv",
    ]
    for raw in raw_names:
        print("   %-24s -> %s" % (ascii(raw), ascii(sanitize_filename(raw))[:60]))

    step("2. join: keep the result inside the base directory")
    base = os.path.join(tempfile.gettempdir(), "safepath_export")
    print("   inside : %s" % ascii(safe_join(base, "2026", "q1.csv")))
    try:
        safe_join(base, "../../etc/passwd")
    except UnsafePathError as exc:
        print("   escape : blocked (%s)" % type(exc).__name__)

    step("3. collide: find names that would overwrite each other")
    groups = find_collisions(["README.md", "readme.md", "data.csv", "DATA.csv", "notes.md"])
    for key, names in sorted(groups.items()):
        print("   %-10s -> %s" % (ascii(key), ascii(names)))
    print("   %d group(s), exit code would be %d" % (len(groups), 1 if groups else 0))

    step("4. fsops: replace a read-only destination atomically")
    workdir = tempfile.mkdtemp(prefix="safepath_quick_")
    src = os.path.join(workdir, "q1.csv.tmp")
    dst = os.path.join(workdir, "q1.csv")
    with open(src, "w", encoding="utf-8") as fh:
        fh.write("new,1\n")
    with open(dst, "w", encoding="utf-8") as fh:
        fh.write("old,1\n")
    os.chmod(dst, 0o444)
    print("   before : %s" % ascii(_tail(dst)))
    atomic_replace(src, dst, retries=3, delay=0.05)
    print("   after  : %s" % ascii(_tail(dst)))

    step("5. length: stay inside the Windows MAX_PATH budget")
    print("   250 chars -> ok=%s" % check_path_length("C:\\" + "x" * 247)["ok"])
    print("   261 chars -> ok=%s" % check_path_length("C:\\" + "x" * 258)["ok"])
    print("done")


def _tail(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read().strip()


if __name__ == "__main__":
    main()
