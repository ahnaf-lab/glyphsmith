import unittest

from glyphsmith.glyphs import SUPPORTED_CHARS, generate_glyph, render_glyph_ascii
from glyphsmith.raster import CANVAS_HEIGHT, CANVAS_WIDTH


class GenerateGlyphTests(unittest.TestCase):
    def test_same_seed_and_char_is_byte_for_byte_reproducible(self):
        first = generate_glyph("acme-corp", "A")
        second = generate_glyph("acme-corp", "A")
        self.assertEqual(first, second)

    def test_bitmap_has_the_expected_canvas_shape(self):
        bitmap = generate_glyph("acme-corp", "A")
        self.assertEqual(len(bitmap), CANVAS_HEIGHT)
        for row in bitmap:
            self.assertEqual(len(row), CANVAS_WIDTH)

    def test_bitmap_values_are_binary(self):
        bitmap = generate_glyph("acme-corp", "B")
        values = {pixel for row in bitmap for pixel in row}
        self.assertTrue(values.issubset({0, 1}))

    def test_every_supported_char_renders_a_non_empty_glyph(self):
        for char in SUPPORTED_CHARS:
            bitmap = generate_glyph("legibility-check", char)
            lit_pixels = sum(sum(row) for row in bitmap)
            self.assertGreater(lit_pixels, 0, f"{char!r} produced a blank glyph")

    def test_unsupported_character_raises_key_error(self):
        with self.assertRaises(KeyError):
            generate_glyph("acme-corp", "@")

    def test_different_seeds_produce_different_typefaces(self):
        seeds = ["seed-one", "seed-two", "seed-three", "seed-four"]
        renderings = set()
        for seed in seeds:
            glyphs = tuple(tuple(tuple(row) for row in generate_glyph(seed, c)) for c in "AKS")
            renderings.add(glyphs)
        self.assertGreater(len(renderings), 1)

    def test_render_glyph_ascii_uses_requested_characters(self):
        bitmap = generate_glyph("acme-corp", "I")
        art = render_glyph_ascii(bitmap, on="X", off="o")
        self.assertIn("X", art)
        self.assertTrue(set(art) - {"\n"} <= {"X", "o"})


if __name__ == "__main__":
    unittest.main()
