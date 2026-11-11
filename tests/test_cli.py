import contextlib
import io
import os
import tempfile
import unittest

from glyphsmith.cli import main


class CliTests(unittest.TestCase):
    def test_renders_requested_characters(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            exit_code = main(["acme-corp", "--chars", "AB"])
        self.assertEqual(exit_code, 0)
        output = out.getvalue()
        self.assertIn("-- 'A' --", output)
        self.assertIn("-- 'B' --", output)

    def test_default_chars_cover_the_full_supported_set(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            main(["acme-corp"])
        output = out.getvalue()
        self.assertIn("-- '0' --", output)
        self.assertIn("-- 'Z' --", output)

    def test_unsupported_character_exits_nonzero(self):
        out = io.StringIO()
        with self.assertRaises(SystemExit) as ctx:
            with contextlib.redirect_stderr(out):
                main(["acme-corp", "--chars", "@"])
        self.assertNotEqual(ctx.exception.code, 0)

    def test_same_seed_gives_identical_output_across_runs(self):
        out1, out2 = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out1):
            main(["reproducible", "--chars", "Q"])
        with contextlib.redirect_stdout(out2):
            main(["reproducible", "--chars", "Q"])
        self.assertEqual(out1.getvalue(), out2.getvalue())

    def test_specimen_flag_prints_a_single_composed_sheet(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            exit_code = main(["acme-corp", "--chars", "ABCD", "--columns", "2", "--specimen"])
        self.assertEqual(exit_code, 0)
        output = out.getvalue()
        self.assertNotIn("-- 'A' --", output)
        self.assertTrue(set(output) - {"\n"} <= {"#", "."})

    def test_png_flag_writes_a_valid_png_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, "specimen.png")
            exit_code = main(["acme-corp", "--chars", "AB", "--png", path])
            self.assertEqual(exit_code, 0)
            with open(path, "rb") as handle:
                header = handle.read(8)
            self.assertEqual(header, b"\x89PNG\r\n\x1a\n")

    def test_invalid_columns_exits_nonzero(self):
        out = io.StringIO()
        with self.assertRaises(SystemExit) as ctx:
            with contextlib.redirect_stderr(out):
                main(["acme-corp", "--specimen", "--columns", "0"])
        self.assertNotEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
