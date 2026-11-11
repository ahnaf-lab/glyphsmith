import string
import unittest

from glyphsmith.strokes import MAX_X, MAX_Y, STROKES

EXPECTED_CHARS = set(string.ascii_uppercase) | set(string.digits) | set(".,-:;!?")


class StrokeTemplateTests(unittest.TestCase):
    def test_covers_letters_digits_and_basic_punctuation(self):
        self.assertEqual(set(STROKES.keys()), EXPECTED_CHARS)

    def test_every_glyph_has_at_least_one_stroke(self):
        for char, strokes in STROKES.items():
            self.assertTrue(strokes, f"{char!r} has no strokes")

    def test_all_points_are_within_the_design_grid(self):
        for char, strokes in STROKES.items():
            for stroke in strokes:
                for x, y in stroke:
                    self.assertTrue(0 <= x <= MAX_X, f"{char!r} x={x} out of range")
                    self.assertTrue(0 <= y <= MAX_Y, f"{char!r} y={y} out of range")

    def test_strokes_are_non_empty_polylines(self):
        for char, strokes in STROKES.items():
            for stroke in strokes:
                self.assertGreaterEqual(len(stroke), 1, f"{char!r} has an empty stroke")


if __name__ == "__main__":
    unittest.main()
