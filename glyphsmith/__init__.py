"""glyphsmith: forge a deterministic bitmap typeface from a seed string."""

from .glyphs import SUPPORTED_CHARS, font_style, generate_glyph, render_glyph_ascii
from .png_writer import encode_png, write_png
from .raster import CANVAS_HEIGHT, CANVAS_WIDTH
from .specimen import compose_specimen, render_specimen_ascii

__all__ = [
    "SUPPORTED_CHARS",
    "font_style",
    "generate_glyph",
    "render_glyph_ascii",
    "CANVAS_WIDTH",
    "CANVAS_HEIGHT",
    "compose_specimen",
    "render_specimen_ascii",
    "encode_png",
    "write_png",
]

__version__ = "0.1.0"
