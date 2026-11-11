"""Command-line interface: forge a seed into a specimen sheet and font file."""

from __future__ import annotations

import argparse
import os
from typing import List, Optional

from .bdf_writer import write_bdf
from .glyphs import SUPPORTED_CHARS, generate_glyph, render_glyph_ascii
from .png_writer import write_png
from .specimen import compose_specimen, render_specimen_ascii

DEFAULT_PNG_NAME = "specimen.png"
DEFAULT_BDF_NAME = "font.bdf"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="glyphsmith",
        description=(
            "Deterministically forge a bitmap typeface from a seed string. "
            "With no output flags, writes a specimen.png and font.bdf for the seed."
        ),
    )
    parser.add_argument("seed", help="seed string that determines the generated typeface")
    parser.add_argument(
        "--chars",
        default="".join(SUPPORTED_CHARS),
        help="characters to render (default: the full supported set)",
    )
    parser.add_argument(
        "--out-dir",
        default=".",
        metavar="DIR",
        help="directory the default specimen.png/font.bdf are written to (default: current directory)",
    )
    parser.add_argument(
        "--png",
        metavar="PATH",
        help=f"write the composed specimen sheet to PATH as a PNG image (default: DIR/{DEFAULT_PNG_NAME})",
    )
    parser.add_argument(
        "--bdf",
        metavar="PATH",
        help=f"write the glyphs for --chars to PATH as a loadable BDF bitmap font file (default: DIR/{DEFAULT_BDF_NAME})",
    )
    parser.add_argument(
        "--columns",
        type=int,
        default=13,
        help="glyphs per row in the specimen sheet (default: 13)",
    )
    parser.add_argument(
        "--scale",
        type=int,
        default=8,
        help="pixel scale factor used when writing a PNG specimen sheet (default: 8)",
    )
    parser.add_argument(
        "--specimen",
        action="store_true",
        help="also print the composed specimen sheet as ASCII art to stdout",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="print each glyph in --chars as a separate ASCII art block instead of writing files",
    )
    parser.add_argument("--on", default="#", help="character used for an inked pixel in ASCII output")
    parser.add_argument("--off", default=".", help="character used for an empty pixel in ASCII output")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    unsupported = sorted({c for c in args.chars if c not in SUPPORTED_CHARS})
    if unsupported:
        parser.error(f"unsupported character(s): {''.join(unsupported)!r}")
    if not args.chars:
        parser.error("--chars must not be empty")

    if args.preview:
        for char in args.chars:
            bitmap = generate_glyph(args.seed, char)
            print(f"-- {char!r} --")
            print(render_glyph_ascii(bitmap, on=args.on, off=args.off))
            print()
        return 0

    if args.columns < 1:
        parser.error("--columns must be at least 1")
    if args.scale < 1:
        parser.error("--scale must be at least 1")

    png_path = args.png or os.path.join(args.out_dir, DEFAULT_PNG_NAME)
    bdf_path = args.bdf or os.path.join(args.out_dir, DEFAULT_BDF_NAME)

    sheet = compose_specimen(args.seed, args.chars, args.columns)
    write_png(sheet, png_path, scale=args.scale)
    write_bdf(args.seed, args.chars, bdf_path)

    if args.specimen:
        print(render_specimen_ascii(sheet, on=args.on, off=args.off))

    print(f"Wrote {png_path} and {bdf_path} ({len(args.chars)} glyphs, seed {args.seed!r})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
