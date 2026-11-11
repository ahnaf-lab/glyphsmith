import struct
import unittest
import zlib

from glyphsmith.png_writer import OFF_COLOR, ON_COLOR, encode_png


def _decode_png(data: bytes):
    """Minimal PNG decoder, just enough to check what encode_png wrote back."""
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    offset = 8
    chunks = {}
    while offset < len(data):
        (length,) = struct.unpack(">I", data[offset : offset + 4])
        tag = data[offset + 4 : offset + 8]
        payload = data[offset + 8 : offset + 8 + length]
        chunks.setdefault(tag, b"")
        chunks[tag] += payload
        offset += 8 + length + 4  # length + tag + payload + crc

    width, height, bit_depth, color_type = struct.unpack(">IIBB", chunks[b"IHDR"][:10])
    assert bit_depth == 8 and color_type == 2

    raw = zlib.decompress(chunks[b"IDAT"])
    stride = 1 + width * 3
    pixels = []
    for y in range(height):
        scanline = raw[y * stride : (y + 1) * stride]
        assert scanline[0] == 0  # filter type none
        row = []
        for x in range(width):
            start = 1 + x * 3
            row.append(tuple(scanline[start : start + 3]))
        pixels.append(row)
    return width, height, pixels


class EncodePngTests(unittest.TestCase):
    def test_header_magic_bytes(self):
        png = encode_png([[1, 0], [0, 1]])
        self.assertEqual(png[:8], b"\x89PNG\r\n\x1a\n")

    def test_dimensions_match_bitmap(self):
        bitmap = [[1, 0, 1], [0, 1, 0]]
        png = encode_png(bitmap)
        width, height, _ = _decode_png(png)
        self.assertEqual((width, height), (3, 2))

    def test_pixel_colors_round_trip(self):
        bitmap = [[1, 0], [0, 1]]
        png = encode_png(bitmap)
        _, _, pixels = _decode_png(png)
        self.assertEqual(pixels[0][0], ON_COLOR)
        self.assertEqual(pixels[0][1], OFF_COLOR)
        self.assertEqual(pixels[1][0], OFF_COLOR)
        self.assertEqual(pixels[1][1], ON_COLOR)

    def test_scale_upscales_each_pixel_into_a_block(self):
        bitmap = [[1, 0]]
        png = encode_png(bitmap, scale=3)
        width, height, pixels = _decode_png(png)
        self.assertEqual((width, height), (6, 3))
        for row in pixels:
            self.assertEqual(row[:3], [ON_COLOR] * 3)
            self.assertEqual(row[3:], [OFF_COLOR] * 3)

    def test_invalid_scale_raises(self):
        with self.assertRaises(ValueError):
            encode_png([[1]], scale=0)


if __name__ == "__main__":
    unittest.main()
