# glyphsmith

Deterministically forge a brand-new, fully legible bitmap typeface from any
seed string. Type a project name in, get a usable typeface out, byte-for-byte
reproducible: the same seed always produces the exact same glyphs.

This milestone implements the glyph generator: a seeded stroke generator
that draws bitmap glyphs for `A`-`Z`, `0`-`9`, and basic punctuation
(`. , - : ; ! ?`). Every character has a fixed, hand-designed stroke
skeleton that keeps it recognizable; the seed only controls the stroke
weight, slant, and small per-point jitter layered on top, so different
seeds produce visibly different but still legible styles of the same
letterforms.

## Install

Requires Python 3.9+. glyphsmith has no runtime dependencies — everything
is built on the standard library (`random`, `hashlib`, `argparse`).

```
git clone <this-repository>
cd glyphsmith
```

No build or install step is required to run it.

## Usage

Preview the glyphs a seed generates, as ASCII art, from the command line:

```
python3 -m glyphsmith "my-project-name"
```

Render only a subset of characters:

```
python3 -m glyphsmith "my-project-name" --chars "ABC123"
```

Customize the ink/blank characters used in the preview:

```
python3 -m glyphsmith "my-project-name" --chars "HELLO" --on "X" --off " "
```

Or use it as a library:

```python
from glyphsmith import generate_glyph, render_glyph_ascii

bitmap = generate_glyph("my-project-name", "A")
print(render_glyph_ascii(bitmap))
```

`generate_glyph(seed, char)` returns a 2D list of `0`/`1` pixels. The same
`(seed, char)` pair always returns the identical bitmap.

## Status

This project is built autonomously, milestone by milestone, and every
change is gated on its automated test suite passing. Run the tests with:

```
python3 -m unittest discover -s tests
```
