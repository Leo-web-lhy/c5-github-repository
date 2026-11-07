"""Tests for :mod:`safepath.collision`."""

import unittest

from safepath.collision import find_collisions, fold_name
from safepath.errors import SafePathError

NFC = "caf\u00e9.md"          # é as one code point
NFD = "cafe\u0301.md"         # e + combining acute accent


class CaseCollisionTests(unittest.TestCase):
    def test_case_variants_collide_by_default(self):
        groups = find_collisions(["README.md", "readme.md"])
        self.assertEqual(len(groups), 1)
        self.assertEqual(list(groups.values())[0], ["README.md", "readme.md"])

    def test_case_sensitive_mode_reports_nothing(self):
        self.assertEqual(find_collisions(["README.md", "readme.md"], case_sensitive=True), {})

    def test_three_way_collision_keeps_input_order(self):
        groups = find_collisions(["A.txt", "a.txt", "A.TXT"])
        self.assertEqual(list(groups.values())[0], ["A.txt", "a.txt", "A.TXT"])

    def test_distinct_names_produce_no_groups(self):
        self.assertEqual(find_collisions(["a.md", "b.md", "c.md"]), {})

    def test_duplicate_identical_names_are_reported(self):
        groups = find_collisions(["same.md", "same.md"])
        self.assertEqual(len(groups), 1)


class UnicodeCollisionTests(unittest.TestCase):
    def test_nfc_and_nfd_forms_collide(self):
        groups = find_collisions([NFC, NFD], case_sensitive=True)
        self.assertEqual(len(groups), 1)

    def test_normalization_can_be_disabled(self):
        groups = find_collisions([NFC, NFD], case_sensitive=True, normalize=False)
        self.assertEqual(groups, {})

    def test_nfd_form_choice_is_honoured(self):
        groups = find_collisions([NFC, NFD], case_sensitive=True, form="NFD")
        self.assertEqual(len(groups), 1)


class FoldNameTests(unittest.TestCase):
    def test_casefold_handles_sharp_s(self):
        self.assertEqual(fold_name("STRASSE.md"), fold_name("stra\u00dfe.md"))

    def test_unsupported_form_raises(self):
        with self.assertRaises(SafePathError):
            fold_name("a.md", form="NFX")

    def test_non_string_raises(self):
        with self.assertRaises(TypeError):
            fold_name(123)

    def test_case_sensitive_keeps_case(self):
        self.assertEqual(fold_name("AbC", case_sensitive=True), "AbC")


if __name__ == "__main__":
    unittest.main()
