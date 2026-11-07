"""Tests for :mod:`safepath.fsops`.

``test_atomic_replace_over_readonly_destination`` is the regression test for
the real failure this module was extracted from: on Windows, overwriting a
file that carries the read-only attribute raises ``PermissionError`` while the
same code succeeds on POSIX.
"""

import os
import shutil
import stat
import tempfile
import unittest
from unittest import mock

from safepath.fsops import (
    WIN_MAX_PATH,
    atomic_replace,
    check_path_length,
    clear_readonly,
)


class FsOpsTestCase(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="safepath-test-")

    def tearDown(self):
        clear_readonly(self.root)
        shutil.rmtree(self.root, ignore_errors=True)

    def path(self, name):
        return os.path.join(self.root, name)

    def write(self, name, text):
        target = self.path(name)
        with open(target, "w", encoding="utf-8") as handle:
            handle.write(text)
        return target


class ClearReadonlyTests(FsOpsTestCase):
    def test_missing_path_returns_false(self):
        self.assertFalse(clear_readonly(self.path("nope.txt")))

    def test_writable_file_returns_false(self):
        target = self.write("writable.txt", "x")
        self.assertFalse(clear_readonly(target))

    def test_readonly_file_is_unlocked(self):
        target = self.write("locked.txt", "x")
        os.chmod(target, stat.S_IREAD)
        self.assertTrue(clear_readonly(target))
        self.assertTrue(os.stat(target).st_mode & stat.S_IWRITE)

    def test_second_call_is_a_no_op(self):
        target = self.write("locked2.txt", "x")
        os.chmod(target, stat.S_IREAD)
        clear_readonly(target)
        self.assertFalse(clear_readonly(target))


class AtomicReplaceTests(FsOpsTestCase):
    def test_replaces_content(self):
        src = self.write("src.txt", "new")
        dst = self.write("dst.txt", "old")
        atomic_replace(src, dst)
        with open(dst, "r", encoding="utf-8") as handle:
            self.assertEqual(handle.read(), "new")
        self.assertFalse(os.path.exists(src))

    def test_creates_destination_when_missing(self):
        src = self.write("src.txt", "payload")
        dst = self.path("fresh.txt")
        atomic_replace(src, dst)
        self.assertTrue(os.path.exists(dst))

    def test_atomic_replace_over_readonly_destination(self):
        src = self.write("src.txt", "new")
        dst = self.write("dst.txt", "old")
        os.chmod(dst, stat.S_IREAD)
        atomic_replace(src, dst)
        with open(dst, "r", encoding="utf-8") as handle:
            self.assertEqual(handle.read(), "new")

    def test_retries_after_transient_permission_error(self):
        src = self.write("src.txt", "new")
        dst = self.write("dst.txt", "old")
        with mock.patch("os.replace", side_effect=[PermissionError(13, "locked"), None]) as spy:
            atomic_replace(src, dst, retries=3, delay=0)
        self.assertEqual(spy.call_count, 2)

    def test_exhausted_retries_raise_last_error(self):
        src = self.write("src.txt", "new")
        dst = self.write("dst.txt", "old")
        with mock.patch("os.replace", side_effect=PermissionError(13, "locked")) as spy:
            with self.assertRaises(PermissionError):
                atomic_replace(src, dst, retries=2, delay=0)
        self.assertEqual(spy.call_count, 2)

    def test_zero_retries_is_treated_as_one_attempt(self):
        src = self.write("src.txt", "new")
        dst = self.path("fresh.txt")
        atomic_replace(src, dst, retries=0)
        self.assertTrue(os.path.exists(dst))


class CheckPathLengthTests(FsOpsTestCase):
    def test_short_path_passes(self):
        info = check_path_length(self.path("a.txt"))
        self.assertTrue(info["ok"])
        self.assertEqual(info["limit"], WIN_MAX_PATH)
        self.assertIsNone(info["suggested"])

    def test_long_path_is_reported_with_length(self):
        long_name = "d" * 120 + os.sep + "f" * 120 + ".txt"
        info = check_path_length(self.path(long_name))
        self.assertFalse(info["ok"])
        self.assertEqual(info["length"], len(info["path"]))
        self.assertGreater(info["length"], info["limit"])

    def test_custom_limit(self):
        info = check_path_length(self.path("a.txt"), limit=10)
        self.assertFalse(info["ok"])
        self.assertEqual(info["limit"], 10)

    def test_suggestion_only_on_windows(self):
        info = check_path_length(self.path("e" * 300), limit=200)
        if os.name == "nt":
            self.assertTrue(str(info["suggested"]).startswith("\\\\?\\"))
        else:
            self.assertIsNone(info["suggested"])


if __name__ == "__main__":
    unittest.main()
