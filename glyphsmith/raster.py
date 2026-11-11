"""Rasterizes stroke polylines onto a small bitmap canvas."""

from __future__ import annotations

import random
from typing import List, Sequence, Tuple

from .strokes import MAX_X, MAX_Y, Stroke

SCALE = 2
PAD = 1

CANVAS_WIDTH = MAX_X * SCALE + 2 * PAD
CANVAS_HEIGHT = MAX_Y * SCALE + 2 * PAD

Bitmap = List[List[int]]
PixelPoint = Tuple[int, int]


def _set_pixel(canvas: Bitmap, x: int, y: int) -> None:
    if 0 <= y < len(canvas) and 0 <= x < len(canvas[0]):
        canvas[y][x] = 1


def _draw_thick_pixel(canvas: Bitmap, x: int, y: int, thickness: int) -> None:
    _set_pixel(canvas, x, y)
    if thickness > 1:
        _set_pixel(canvas, x + 1, y)
        _set_pixel(canvas, x, y + 1)


def _draw_line(canvas: Bitmap, p0: PixelPoint, p1: PixelPoint, thickness: int) -> None:
    x0, y0 = p0
    x1, y1 = p1
    dx = x1 - x0
    dy = y1 - y0
    steps = max(abs(dx), abs(dy), 1)
    for i in range(steps + 1):
        t = i / steps
        x = round(x0 + dx * t)
        y = round(y0 + dy * t)
        _draw_thick_pixel(canvas, x, y, thickness)


def _plot_blob(canvas: Bitmap, center: PixelPoint, thickness: int) -> None:
    cx, cy = center
    radius = thickness
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            if dx * dx + dy * dy <= radius * radius + 1:
                _set_pixel(canvas, cx + dx, cy + dy)


def _transform_point(point: Tuple[int, int], rng: random.Random, slant: float) -> PixelPoint:
    x, y = point
    px = x * SCALE + PAD
    py = y * SCALE + PAD
    px += rng.randint(-1, 1)
    py += rng.randint(-1, 1)
    px += round(slant * y)
    px = min(max(px, 0), CANVAS_WIDTH - 1)
    py = min(max(py, 0), CANVAS_HEIGHT - 1)
    return px, py


def rasterize(
    strokes: Sequence[Stroke],
    thickness: int,
    jitter_rng: random.Random,
    slant: float = 0.0,
) -> Bitmap:
    """Draw a list of design-space strokes onto a fresh pixel bitmap."""
    canvas: Bitmap = [[0] * CANVAS_WIDTH for _ in range(CANVAS_HEIGHT)]
    for stroke in strokes:
        points = [_transform_point(p, jitter_rng, slant) for p in stroke]
        if len(points) == 1:
            _plot_blob(canvas, points[0], thickness)
        else:
            for p0, p1 in zip(points, points[1:]):
                _draw_line(canvas, p0, p1, thickness)
    return canvas
