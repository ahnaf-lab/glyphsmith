"""Seeded stroke generator: turns a seed string into bitmap glyphs."""

from __future__ import annotations

from typing import Tuple

from .prng import make_rng
from .raster import Bitmap, rasterize
from .strokes import STROKES

SUPPORTED_CHARS: Tuple[str, ...] = tuple(STROKES.keys())

THICKNESS_CHOICES = (1, 2)
SLANT_CHOICES = (-0.1, 0.0, 0.1)


def font_style(seed: str) -> Tuple[int, float]:
    """Derive the whole-typeface style (stroke weight, slant) from a seed.

    Keeping this derived from the seed alone (not the character) gives a
    single seed one consistent typeface weight/slant across all its glyphs.
    """
    rng = make_rng(seed, "style")
    thickness = rng.choice(THICKNESS_CHOICES)
    slant = rng.choice(SLANT_CHOICES)
    return thickness, slant


def generate_glyph(seed: str, char: str) -> Bitmap:
    """Deterministically forge the bitmap for one character under a seed."""
    if char not in STROKES:
        raise KeyError(f"no stroke template for character {char!r}")
    thickness, slant = font_style(seed)
    jitter_rng = make_rng(seed, "glyph", char)
    return rasterize(STROKES[char], thickness, jitter_rng, slant)


def render_glyph_ascii(bitmap: Bitmap, on: str = "#", off: str = ".") -> str:
    """Render a bitmap as a block of ASCII art for terminal preview."""
    return "\n".join("".join(on if pixel else off for pixel in row) for row in bitmap)
