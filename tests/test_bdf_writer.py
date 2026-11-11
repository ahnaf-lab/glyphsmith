import os
import tempfile
import unittest

from glyphsmith.bdf_writer import encode_bdf, write_bdf
from glyphsmith.raster import CANVAS_HEIGHT, CANVAS_WIDTH


class EncodeBdfTests(unittest.TestCase):
    def test_starts_and_ends_with_font_markers(self):
        text = encode_bdf("acme-corp", "AB")
        self.assertTrue(text.startswith("STARTFONT 2.1\n"))
        self.assertTrue(text.endswith("ENDFONT\n"))

    def test_chars_count_matches_distinct_requested_characters(self):
        text = encode_bdf("acme-corp", "ABA")
        self.assertIn("CHARS 2\n", text)
        self.assertEqual(text.count("STARTCHAR "), 2)
        self.assertEqual(text.count("ENDCHAR"), 2)

    def test_each_glyph_has_the_expected_bitmap_row_count_and_width(self):
        text = encode_bdf("acme-corp", "A")
        lines = text.splitlines()
        bitmap_start = lines.index("BITMAP") + 1
        bitmap_rows = lines[bitmap_start : bitmap_start + CANVAS_HEIGHT]
        self.assertEqual(len(bitmap_rows), CANVAS_HEIGHT)
        expected_hex_digits = ((CANVAS_WIDTH + 7) // 8) * 8 // 4
        for row in bitmap_rows:
            self.assertEqual(len(row), expected_hex_digits)
            int(row, 16)  # every row must be valid hex

    def test_punctuation_gets_a_named_glyph_not_a_literal_character(self):
        text = encode_bdf("acme-corp", ".")
        self.assertIn("STARTCHAR period\n", text)
        self.assertIn(f"ENCODING {ord('.')}\n", text)

    def test_same_seed_and_chars_are_byte_for_byte_reproducible(self):
        first = encode_bdf("acme-corp", "HELLO")
        second = encode_bdf("acme-corp", "HELLO")
        self.assertEqual(first, second)

    def test_different_seeds_diverge(self):
        first = encode_bdf("acme-corp", "A")
        second = encode_bdf("globex-inc", "A")
        self.assertNotEqual(first, second)

    def test_empty_chars_raises(self):
        with self.assertRaises(ValueError):
            encode_bdf("acme-corp", "")

    def test_seed_with_xlfd_breaking_characters_still_produces_valid_font(self):
        text = encode_bdf("my cool-project!", "A")
        self.assertTrue(text.startswith("STARTFONT 2.1\n"))
        font_line = next(line for line in text.splitlines() if line.startswith("FONT "))
        self.assertEqual(len(font_line.split("-")), 15)

    def test_write_bdf_writes_the_same_text_encode_bdf_returns(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, "font.bdf")
            write_bdf("acme-corp", "AB", path)
            with open(path, "r", encoding="ascii") as handle:
                written = handle.read()
            self.assertEqual(written, encode_bdf("acme-corp", "AB"))


if __name__ == "__main__":
    unittest.main()
