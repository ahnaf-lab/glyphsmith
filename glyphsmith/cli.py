"""Command-line interface for previewing seeded glyphs."""

from __future__ import annotations

import argparse
from typing import List, Optional

from .bdf_writer import write_bdf
from .glyphs import SUPPORTED_CHARS, generate_glyph, render_glyph_ascii
from .png_writer import write_png
from .specimen import compose_specimen, render_specimen_ascii


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="glyphsmith",
        description="Deterministically forge stroke-based bitmap glyphs from a seed string.",
    )
    parser.add_argument("seed", help="seed string that determines the generated typeface")
    parser.add_argument(
        "--chars",
        default="".join(SUPPORTED_CHARS),
        help="characters to render (default: the full supported set)",
    )
    parser.add_argument("--on", default="#", help="character used for an inked pixel")
    parser.add_argument("--off", default=".", help="character used for an empty pixel")
    parser.add_argument(
        "--specimen",
        action="store_true",
        help="print one composed ASCII specimen sheet instead of per-glyph previews",
    )
    parser.add_argument(
        "--png",
        metavar="PATH",
        help="write the composed specimen sheet to PATH as a PNG image",
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
        "--bdf",
        metavar="PATH",
        help="write the glyphs for --chars to PATH as a loadable BDF bitmap font file",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    unsupported = sorted({c for c in args.chars if c not in SUPPORTED_CHARS})
    if unsupported:
        parser.error(f"unsupported character(s): {''.join(unsupported)!r}")

    if args.bdf:
        if not args.chars:
            parser.error("--bdf requires at least one character in --chars")
        write_bdf(args.seed, args.chars, args.bdf)

    if args.specimen or args.png or args.bdf:
        if args.specimen or args.png:
            if args.columns < 1:
                parser.error("--columns must be at least 1")
            if args.scale < 1:
                parser.error("--scale must be at least 1")

            sheet = compose_specimen(args.seed, args.chars, args.columns)

            if args.specimen:
                print(render_specimen_ascii(sheet, on=args.on, off=args.off))

            if args.png:
                write_png(sheet, args.png, scale=args.scale)

        return 0

    for char in args.chars:
        bitmap = generate_glyph(args.seed, char)
        print(f"-- {char!r} --")
        print(render_glyph_ascii(bitmap, on=args.on, off=args.off))
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
