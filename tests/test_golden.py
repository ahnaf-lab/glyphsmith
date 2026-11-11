"""Golden-file tests: a fixed seed must forge the exact same bytes forever.

Unlike the reproducibility checks elsewhere (which only compare two fresh
calls to each other), these tests pin the output of a fixed seed against
values captured once and committed to disk or inline. If the generator,
rasterizer, or BDF writer ever changes in a way that shifts output for an
existing seed, these tests catch it even though nothing here calls the
code twice.
"""

import json
import os
import unittest

from glyphsmith.bdf_writer import encode_bdf
from glyphsmith.glyphs import generate_glyph

GOLDEN_DIR = os.path.join(os.path.dirname(__file__), "golden")
GOLDEN_SEED = "glyphsmith-golden"

# Captured once from glyphsmith.glyphs.generate_glyph(GOLDEN_SEED, "2") and
# pinned here as a literal so a regression shows up as a readable diff.
GOLDEN_GLYPH_2 = [
    [0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 1, 1, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 1, 1, 1],
    [0, 0, 0, 1, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]


class GoldenGlyphBitmapTests(unittest.TestCase):
    def test_glyph_a_matches_committed_golden_bitmap(self):
        with open(os.path.join(GOLDEN_DIR, "glyphsmith_golden_glyph_A.json")) as handle:
            expected = json.load(handle)
        actual = generate_glyph(GOLDEN_SEED, "A")
        self.assertEqual(actual, expected)

    def test_glyph_2_matches_inline_golden_bitmap(self):
        actual = generate_glyph(GOLDEN_SEED, "2")
        self.assertEqual(actual, GOLDEN_GLYPH_2)


class GoldenBdfBytesTests(unittest.TestCase):
    def test_bdf_text_matches_committed_golden_file_byte_for_byte(self):
        golden_path = os.path.join(GOLDEN_DIR, "glyphsmith_golden.bdf")
        with open(golden_path, "r", encoding="ascii") as handle:
            expected_text = handle.read()
        expected_bytes = expected_text.encode("ascii")

        actual_text = encode_bdf(GOLDEN_SEED, "AB2.")
        actual_bytes = actual_text.encode("ascii")

        self.assertEqual(actual_bytes, expected_bytes)

    def test_bdf_bitmap_rows_are_valid_hex_of_the_expected_byte_width(self):
        golden_path = os.path.join(GOLDEN_DIR, "glyphsmith_golden.bdf")
        with open(golden_path, "r", encoding="ascii") as handle:
            lines = handle.read().splitlines()

        bitmap_start = lines.index("BITMAP") + 1
        first_row = lines[bitmap_start]
        self.assertEqual(len(first_row), 4)
        int(first_row, 16)  # must be valid hex


if __name__ == "__main__":
    unittest.main()
