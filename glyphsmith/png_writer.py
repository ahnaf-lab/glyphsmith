"""Minimal, dependency-free PNG encoder for 1-bit bitmaps.

Writing PNG by hand with `struct` and `zlib` (both standard library) avoids
pulling in an image library just to emit a specimen sheet as a picture.
"""

from __future__ import annotations

import struct
import zlib

from .raster import Bitmap

ON_COLOR = (17, 17, 17)
OFF_COLOR = (255, 255, 255)


def _chunk(tag: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def encode_png(
    bitmap: Bitmap,
    scale: int = 1,
    on_color=ON_COLOR,
    off_color=OFF_COLOR,
) -> bytes:
    """Encode a 0/1 bitmap as the bytes of an 8-bit RGB PNG file."""
    if scale < 1:
        raise ValueError("scale must be at least 1")

    height = len(bitmap)
    width = len(bitmap[0]) if height else 0
    out_width = width * scale
    out_height = height * scale

    raw = bytearray()
    for y in range(out_height):
        raw.append(0)  # PNG filter type 0 (none) for this scanline
        src_row = bitmap[y // scale]
        for x in range(out_width):
            color = on_color if src_row[x // scale] else off_color
            raw.extend(color)

    ihdr = struct.pack(">IIBBBBB", out_width, out_height, 8, 2, 0, 0, 0)
    idat = zlib.compress(bytes(raw), 9)

    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", idat)
        + _chunk(b"IEND", b"")
    )


def write_png(bitmap: Bitmap, path: str, scale: int = 1) -> None:
    """Write a 0/1 bitmap to `path` as a PNG image, upscaled by `scale`."""
    with open(path, "wb") as handle:
        handle.write(encode_png(bitmap, scale=scale))
