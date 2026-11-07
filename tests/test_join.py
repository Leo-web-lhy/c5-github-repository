"""Tests for :mod:`safepath.join`."""

import os
import unittest

from safepath.errors import UnsafePathError
from safepath.join import is_within, safe_join


class SafeJoinHappyPathTests(unittest.TestCase):
    def test_single_fragment(self):
        expected = os.path.join(os.sep + "srv", "data", "q1.csv") if os.name != "nt" else None
        result = safe_join("/srv/data", "q1.csv")
        if expected is not None:
            self.assertEqual(result, expected)
        self.assertTrue(result.endswith("q1.csv"))

    def test_multiple_fragments(self):
        result = safe_join("base", "reports", "2026", "q1.csv")
        self.assertEqual(
            result,
            os.path.normpath(os.path.join("base", "reports", "2026", "q1.csv")),
        )

    def test_dot_segments_are_harmless(self):
        self.assertEqual(safe_join("base", "a", ".", "b.txt"), safe_join("base", "a", "b.txt"))

    def test_no_parts_returns_base(self):
        self.assertEqual(safe_join("base"), "base")


class SafeJoinEscapeTests(unittest.TestCase):
    def test_parent_escape_raises(self):
        with self.assertRaises(UnsafePathError):
            safe_join("base", "..")

    def test_deep_escape_raises(self):
        with self.assertRaises(UnsafePathError):
            safe_join("base", "sub", "..", "..", "evil")

    def test_embedded_traversal_raises(self):
        with self.assertRaises(UnsafePathError):
            safe_join("base", "../../etc/passwd")

    def test_absolute_component_raises(self):
        with self.assertRaises(UnsafePathError):
            safe_join("base", os.path.abspath(os.sep + "etc"))

    def test_drive_relative_component_raises_everywhere(self):
        with self.assertRaises(UnsafePathError):
            safe_join("base", "C:evil")

    def test_unc_component_raises(self):
        with self.assertRaises(UnsafePathError):
            safe_join("base", r"\\server\share\file")

    def test_nul_byte_raises(self):
        with self.assertRaises(UnsafePathError):
            safe_join("base", "a\x00b")

    def test_allow_absolute_still_enforces_containment(self):
        outside = os.path.abspath(os.sep + "etc")
        with self.assertRaises(UnsafePathError):
            safe_join("base", outside, allow_absolute=True)


class IsWithinTests(unittest.TestCase):
    def test_child_is_within(self):
        self.assertTrue(is_within("base", os.path.join("base", "sub", "f.txt")))

    def test_self_is_within(self):
        self.assertTrue(is_within("base", "base"))

    def test_sibling_prefix_is_not_within(self):
        self.assertFalse(is_within("base", os.path.join("base", "..", "base2")))

    def test_sibling_prefix_string_trap(self):
        self.assertFalse(is_within("base", "base_evil"))


if __name__ == "__main__":
    unittest.main()
