import contextlib
import io
import os
import tempfile
import unittest

from glyphsmith.cli import main


class CliTests(unittest.TestCase):
    def test_preview_renders_requested_characters(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            exit_code = main(["acme-corp", "--chars", "AB", "--preview"])
        self.assertEqual(exit_code, 0)
        output = out.getvalue()
        self.assertIn("-- 'A' --", output)
        self.assertIn("-- 'B' --", output)

    def test_preview_default_chars_cover_the_full_supported_set(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            main(["acme-corp", "--preview"])
        output = out.getvalue()
        self.assertIn("-- '0' --", output)
        self.assertIn("-- 'Z' --", output)

    def test_unsupported_character_exits_nonzero(self):
        out = io.StringIO()
        with self.assertRaises(SystemExit) as ctx:
            with contextlib.redirect_stderr(out):
                main(["acme-corp", "--chars", "@"])
        self.assertNotEqual(ctx.exception.code, 0)

    def test_same_seed_gives_identical_preview_across_runs(self):
        out1, out2 = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out1):
            main(["reproducible", "--chars", "Q", "--preview"])
        with contextlib.redirect_stdout(out2):
            main(["reproducible", "--chars", "Q", "--preview"])
        self.assertEqual(out1.getvalue(), out2.getvalue())

    def test_specimen_flag_prints_a_single_composed_sheet(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                exit_code = main(
                    [
                        "acme-corp",
                        "--chars",
                        "ABCD",
                        "--columns",
                        "2",
                        "--specimen",
                        "--out-dir",
                        tmp_dir,
                    ]
                )
            self.assertEqual(exit_code, 0)
            output = out.getvalue()
            self.assertNotIn("-- 'A' --", output)
            ascii_sheet = output.splitlines()[0]
            self.assertTrue(set(ascii_sheet) <= {"#", "."})

    def test_png_flag_writes_a_valid_png_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, "specimen.png")
            exit_code = main(["acme-corp", "--chars", "AB", "--png", path, "--out-dir", tmp_dir])
            self.assertEqual(exit_code, 0)
            with open(path, "rb") as handle:
                header = handle.read(8)
            self.assertEqual(header, b"\x89PNG\r\n\x1a\n")

    def test_bdf_flag_writes_a_loadable_bdf_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, "font.bdf")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                exit_code = main(["acme-corp", "--chars", "AB", "--bdf", path, "--out-dir", tmp_dir])
            self.assertEqual(exit_code, 0)
            with open(path, "r", encoding="ascii") as handle:
                content = handle.read()
            self.assertTrue(content.startswith("STARTFONT 2.1\n"))
            self.assertIn("CHARS 2\n", content)

    def test_invalid_columns_exits_nonzero(self):
        out = io.StringIO()
        with self.assertRaises(SystemExit) as ctx:
            with contextlib.redirect_stderr(out):
                main(["acme-corp", "--columns", "0"])
        self.assertNotEqual(ctx.exception.code, 0)

    def test_bare_invocation_writes_specimen_and_font_into_out_dir(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                exit_code = main(["my-repo-name", "--out-dir", tmp_dir])
            self.assertEqual(exit_code, 0)
            png_path = os.path.join(tmp_dir, "specimen.png")
            bdf_path = os.path.join(tmp_dir, "font.bdf")
            self.assertTrue(os.path.isfile(png_path))
            self.assertTrue(os.path.isfile(bdf_path))
            with open(png_path, "rb") as handle:
                self.assertEqual(handle.read(8), b"\x89PNG\r\n\x1a\n")
            with open(bdf_path, "r", encoding="ascii") as handle:
                self.assertTrue(handle.read().startswith("STARTFONT 2.1\n"))
            self.assertIn("specimen.png", out.getvalue())
            self.assertIn("font.bdf", out.getvalue())


if __name__ == "__main__":
    unittest.main()
