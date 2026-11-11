"""Compose individual glyphs into a single specimen sheet bitmap.

A specimen sheet lays out every requested glyph for a seed on one shared
canvas, several glyphs per row, so the whole typeface can be previewed or
exported as a single image rather than one glyph at a time.
"""

from __future__ import annotations

from typing import List, Sequence

from .glyphs import generate_glyph
from .raster import Bitmap, CANVAS_HEIGHT, CANVAS_WIDTH

GUTTER = 2


def compose_specimen(seed: str, chars: Sequence[str], columns: int) -> Bitmap:
    """Lay out the glyphs for `chars` on one bitmap, `columns` glyphs per row.

    Rows wrap once `columns` glyphs have been placed, with a blank gutter
    between glyphs and between rows so individual letterforms stay visually
    separated on the sheet.
    """
    if columns < 1:
        raise ValueError("columns must be at least 1")
    if not chars:
        return []

    glyphs: List[Bitmap] = [generate_glyph(seed, char) for char in chars]
    rows_of_glyphs = [glyphs[i : i + columns] for i in range(0, len(glyphs), columns)]

    sheet_width = columns * CANVAS_WIDTH + (columns - 1) * GUTTER
    sheet_height = len(rows_of_glyphs) * CANVAS_HEIGHT + (len(rows_of_glyphs) - 1) * GUTTER
    sheet: Bitmap = [[0] * sheet_width for _ in range(sheet_height)]

    for row_index, row_glyphs in enumerate(rows_of_glyphs):
        y_offset = row_index * (CANVAS_HEIGHT + GUTTER)
        for col_index, glyph in enumerate(row_glyphs):
            x_offset = col_index * (CANVAS_WIDTH + GUTTER)
            for y, row in enumerate(glyph):
                for x, pixel in enumerate(row):
                    if pixel:
                        sheet[y_offset + y][x_offset + x] = 1
    return sheet


def render_specimen_ascii(sheet: Bitmap, on: str = "#", off: str = ".") -> str:
    """Render a specimen sheet bitmap as a block of ASCII art."""
    return "\n".join("".join(on if pixel else off for pixel in row) for row in sheet)
