"""Write glyphs out as a BDF (Glyph Bitmap Distribution Format) font file.

BDF is a plain-text bitmap font format understood by terminals, image
editors, and font tools (e.g. `bdftopcf`, FontForge). It is just structured
text, so writing it is plain string formatting and needs no font-tooling
dependency.
"""

from __future__ import annotations

import re
from typing import Dict, List, Sequence

from .glyphs import generate_glyph
from .raster import Bitmap, CANVAS_HEIGHT, CANVAS_WIDTH

# Names for punctuation glyphs, following the Adobe Glyph List convention
# that most BDF-consuming tools expect for STARTCHAR names.
_PUNCTUATION_NAMES = {
    ".": "period",
    ",": "comma",
    "-": "hyphen",
    ":": "colon",
    ";": "semicolon",
    "!": "exclam",
    "?": "question",
}

_XLFD_SAFE = re.compile(r"[^A-Za-z0-9]+")


def _glyph_name(char: str) -> str:
    """Return a BDF STARTCHAR-safe glyph name for `char`."""
    if char.isalnum():
        return char
    return _PUNCTUATION_NAMES.get(char, f"uni{ord(char):04X}")


def _xlfd_safe_seed(seed: str) -> str:
    """Collapse non-alphanumeric characters so the seed fits in the FONT XLFD name.

    The FONT field is a dash-separated XLFD name; a seed containing dashes
    or spaces would otherwise split into the wrong number of fields.
    """
    collapsed = _XLFD_SAFE.sub("_", seed).strip("_")
    return collapsed or "seed"


def _bitmap_to_hex_rows(bitmap: Bitmap) -> List[str]:
    """Encode each bitmap row as the padded hex digits BDF's BITMAP section expects.

    BDF pads every row to a whole number of bytes (8 pixels) with zero bits
    on the right, then writes each byte as two uppercase hex digits.
    """
    rows = []
    for row in bitmap:
        padded_width = ((len(row) + 7) // 8) * 8
        bits = "".join("1" if pixel else "0" for pixel in row).ljust(padded_width, "0")
        hex_row = "".join(f"{int(bits[i : i + 8], 2):02X}" for i in range(0, padded_width, 8))
        rows.append(hex_row)
    return rows


def encode_bdf(seed: str, chars: Sequence[str]) -> str:
    """Render the glyphs for `chars` under `seed` as the text of a BDF font file.

    The same `(seed, chars)` pair always produces the identical BDF text,
    since every glyph bitmap comes from the deterministic generator in
    :mod:`glyphsmith.glyphs`.
    """
    if not chars:
        raise ValueError("chars must not be empty")

    ordered_unique: List[str] = []
    for char in chars:
        if char not in ordered_unique:
            ordered_unique.append(char)

    glyphs: Dict[str, Bitmap] = {char: generate_glyph(seed, char) for char in ordered_unique}

    point_size = CANVAS_HEIGHT
    xlfd_seed = _xlfd_safe_seed(seed)
    lines = [
        "STARTFONT 2.1",
        "FONT -glyphsmith-{}-medium-r-normal--{}-{}-75-75-c-{}-iso10646-1".format(
            xlfd_seed, point_size, point_size * 10, CANVAS_WIDTH * 10
        ),
        f"SIZE {point_size} 75 75",
        f"FONTBOUNDINGBOX {CANVAS_WIDTH} {CANVAS_HEIGHT} 0 0",
        "STARTPROPERTIES 2",
        f"FONT_ASCENT {CANVAS_HEIGHT}",
        "FONT_DESCENT 0",
        "ENDPROPERTIES",
        f"CHARS {len(ordered_unique)}",
    ]

    for char in ordered_unique:
        lines.append(f"STARTCHAR {_glyph_name(char)}")
        lines.append(f"ENCODING {ord(char)}")
        lines.append("SWIDTH 0 0")
        lines.append(f"DWIDTH {CANVAS_WIDTH} 0")
        lines.append(f"BBX {CANVAS_WIDTH} {CANVAS_HEIGHT} 0 0")
        lines.append("BITMAP")
        lines.extend(_bitmap_to_hex_rows(glyphs[char]))
        lines.append("ENDCHAR")

    lines.append("ENDFONT")
    return "\n".join(lines) + "\n"


def write_bdf(seed: str, chars: Sequence[str], path: str) -> None:
    """Write the BDF font file for `chars` under `seed` to `path`."""
    with open(path, "w", encoding="ascii") as handle:
        handle.write(encode_bdf(seed, chars))
