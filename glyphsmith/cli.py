"""Command-line interface for previewing seeded glyphs."""

from __future__ import annotations

import argparse
from typing import List, Optional

from .glyphs import SUPPORTED_CHARS, generate_glyph, render_glyph_ascii


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
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    unsupported = sorted({c for c in args.chars if c not in SUPPORTED_CHARS})
    if unsupported:
        parser.error(f"unsupported character(s): {''.join(unsupported)!r}")

    for char in args.chars:
        bitmap = generate_glyph(args.seed, char)
        print(f"-- {char!r} --")
        print(render_glyph_ascii(bitmap, on=args.on, off=args.off))
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
