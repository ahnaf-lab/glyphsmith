"""Deterministic pseudo-random helpers derived from a seed string.

Every random decision in glyphsmith is traced back to the user-supplied
seed string so that the same seed always forges byte-for-byte the same
typeface, while different seeds diverge.
"""

from __future__ import annotations

import hashlib
import random


def _digest_to_int(key: str) -> int:
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def make_rng(seed: str, *parts: str) -> random.Random:
    """Return a Random instance deterministically derived from seed + parts.

    Using distinct `parts` (e.g. a role tag and a character) lets independent
    aspects of generation (overall style vs. a single glyph's jitter) draw
    from independent-looking but fully reproducible random streams.
    """
    key = "\x1f".join((seed, *parts))
    return random.Random(_digest_to_int(key))
