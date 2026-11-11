import unittest

from glyphsmith.glyphs import generate_glyph
from glyphsmith.raster import CANVAS_HEIGHT, CANVAS_WIDTH
from glyphsmith.specimen import GUTTER, compose_specimen, render_specimen_ascii


class ComposeSpecimenTests(unittest.TestCase):
    def test_sheet_dimensions_match_rows_and_columns(self):
        sheet = compose_specimen("acme-corp", "ABCDE", columns=3)
        expected_width = 3 * CANVAS_WIDTH + 2 * GUTTER
        expected_height = 2 * CANVAS_HEIGHT + GUTTER  # 5 chars, 3 cols -> 2 rows
        self.assertEqual(len(sheet[0]), expected_width)
        self.assertEqual(len(sheet), expected_height)

    def test_single_row_when_columns_cover_all_chars(self):
        sheet = compose_specimen("acme-corp", "AB", columns=5)
        self.assertEqual(len(sheet), CANVAS_HEIGHT)
        self.assertEqual(len(sheet[0]), 5 * CANVAS_WIDTH + 4 * GUTTER)

    def test_same_seed_is_byte_for_byte_reproducible(self):
        first = compose_specimen("acme-corp", "HELLO", columns=4)
        second = compose_specimen("acme-corp", "HELLO", columns=4)
        self.assertEqual(first, second)

    def test_first_glyph_block_matches_standalone_glyph(self):
        sheet = compose_specimen("acme-corp", "AB", columns=2)
        standalone = generate_glyph("acme-corp", "A")
        cropped = [row[:CANVAS_WIDTH] for row in sheet[:CANVAS_HEIGHT]]
        self.assertEqual(cropped, standalone)

    def test_empty_chars_produces_empty_sheet(self):
        self.assertEqual(compose_specimen("acme-corp", "", columns=5), [])

    def test_invalid_columns_raises(self):
        with self.assertRaises(ValueError):
            compose_specimen("acme-corp", "AB", columns=0)

    def test_render_specimen_ascii_uses_requested_characters(self):
        sheet = compose_specimen("acme-corp", "AB", columns=2)
        art = render_specimen_ascii(sheet, on="X", off="o")
        self.assertIn("X", art)
        self.assertTrue(set(art) - {"\n"} <= {"X", "o"})


if __name__ == "__main__":
    unittest.main()
