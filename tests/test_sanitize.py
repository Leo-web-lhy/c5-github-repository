"""Tests for :mod:`safepath.sanitize`."""

import unittest

from safepath.errors import InvalidNameError
from safepath.sanitize import is_reserved_name, sanitize_filename


class SanitizeForbiddenCharTests(unittest.TestCase):
    def test_each_forbidden_char_is_replaced(self):
        for char in '<>:"/\\|?*':
            with self.subTest(char=char):
                self.assertEqual(sanitize_filename("a%sb" % char), "a_b")

    def test_path_separators_cannot_survive(self):
        self.assertEqual(sanitize_filename("../../etc/passwd"), ".._.._etc_passwd")

    def test_control_characters_are_replaced(self):
        self.assertEqual(sanitize_filename("a\x00b\x1fc\x7fd"), "a_b_c_d")

    def test_custom_replacement(self):
        self.assertEqual(sanitize_filename("a:b?c", replacement="-"), "a-b-c")


class SanitizeReservedNameTests(unittest.TestCase):
    def test_reserved_devices_are_prefixed(self):
        for raw in ("CON", "con.txt", "NUL", "COM1.log", "LPT9"):
            with self.subTest(raw=raw):
                self.assertTrue(sanitize_filename(raw).startswith("_"))

    def test_reserved_names_are_flagged_by_helper(self):
        self.assertTrue(is_reserved_name("aux.tar.gz"))
        self.assertTrue(is_reserved_name("  con  "))
        self.assertFalse(is_reserved_name("console.txt"))
        self.assertFalse(is_reserved_name("COM10.log"))

    def test_lookalike_names_are_untouched(self):
        self.assertEqual(sanitize_filename("CONSOLE.txt"), "CONSOLE.txt")


class SanitizeTrailingNoiseTests(unittest.TestCase):
    def test_trailing_dots_and_spaces_are_stripped(self):
        self.assertEqual(sanitize_filename("report.md "), "report.md")
        self.assertEqual(sanitize_filename("report.md..."), "report.md")
        self.assertEqual(sanitize_filename("report.md . . "), "report.md")

    def test_leading_spaces_are_kept_because_they_are_legal(self):
        self.assertEqual(sanitize_filename(" lead.txt"), " lead.txt")


class SanitizeRejectionTests(unittest.TestCase):
    def test_nothing_usable_raises(self):
        for raw in ("", "   ", ".", "..", ". ", " ... "):
            with self.subTest(raw=raw):
                with self.assertRaises(InvalidNameError):
                    sanitize_filename(raw)

    def test_non_string_raises_type_error(self):
        with self.assertRaises(TypeError):
            sanitize_filename(None)

    def test_non_positive_max_length_raises(self):
        with self.assertRaises(ValueError):
            sanitize_filename("a.txt", max_length=0)


class SanitizeLengthTests(unittest.TestCase):
    def test_extension_is_preserved_when_truncating(self):
        result = sanitize_filename("a" * 300 + ".txt", max_length=255)
        self.assertEqual(len(result), 255)
        self.assertTrue(result.endswith(".txt"))

    def test_long_name_without_extension_is_cut(self):
        result = sanitize_filename("a" * 400, max_length=64)
        self.assertEqual(len(result), 64)

    def test_extension_larger_than_budget_falls_back_to_plain_cut(self):
        result = sanitize_filename("x." + "y" * 200, max_length=32)
        self.assertEqual(len(result), 32)

    def test_short_names_are_untouched(self):
        self.assertEqual(sanitize_filename("a.txt", max_length=255), "a.txt")


class SanitizeUnicodeTests(unittest.TestCase):
    def test_chinese_names_survive(self):
        self.assertEqual(sanitize_filename("交付物 说明.md"), "交付物 说明.md")

    def test_emoji_names_survive(self):
        self.assertEqual(sanitize_filename("report-✅.md"), "report-✅.md")

    def test_idempotent(self):
        once = sanitize_filename("a:b?c")
        self.assertEqual(sanitize_filename(once), once)


if __name__ == "__main__":
    unittest.main()
