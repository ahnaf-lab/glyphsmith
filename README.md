# glyphsmith

Deterministically forge a brand-new, fully legible bitmap typeface from any
seed string. Type a project name in, get a usable typeface out, byte-for-byte
reproducible: the same seed always produces the exact same glyphs.

This project implements a seeded stroke generator that draws bitmap glyphs
for `A`-`Z`, `0`-`9`, and basic punctuation (`. , - : ; ! ?`). Every
character has a fixed, hand-designed stroke skeleton that keeps it
recognizable; the seed only controls the stroke weight, slant, and small
per-point jitter layered on top, so different seeds produce visibly
different but still legible styles of the same letterforms.

The previous milestone added the specimen sheet: all requested glyphs for a
seed are composed onto one shared canvas (wrapping into rows) and can be
previewed as ASCII art or exported as a real PNG image, so a whole typeface
can be seen at a glance instead of one glyph at a time. The PNG is written
with a small hand-rolled encoder built on `struct` and `zlib` from the
standard library, so no image library dependency is needed.

This milestone adds a BDF (Glyph Bitmap Distribution Format) exporter: the
requested glyphs for a seed are written out as a plain-text `.bdf` bitmap
font file, the same format produced by classic X11 font tools. BDF is just
structured text, so the exporter is a small hand-rolled text writer with no
font-tooling dependency; the resulting file can be loaded directly by
terminal emulators, image/font editors (e.g. FontForge), and converters
like `bdftopcf` that expect a standard bitmap font.

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

Preview the whole typeface as one composed ASCII specimen sheet (glyphs wrap
into rows, `--columns` per row):

```
python3 -m glyphsmith "my-project-name" --specimen --columns 13
```

Export the specimen sheet as a PNG image instead, scaled up for visibility:

```
python3 -m glyphsmith "my-project-name" --png specimen.png --columns 13 --scale 8
```

Export the requested glyphs as a loadable BDF bitmap font file:

```
python3 -m glyphsmith "my-project-name" --bdf myfont.bdf
```

Or use it as a library:

```python
from glyphsmith import generate_glyph, render_glyph_ascii, compose_specimen, write_png, write_bdf

bitmap = generate_glyph("my-project-name", "A")
print(render_glyph_ascii(bitmap))

sheet = compose_specimen("my-project-name", "ABCDEFGHIJKLM", columns=13)
write_png(sheet, "specimen.png", scale=8)

write_bdf("my-project-name", "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", "myfont.bdf")
```

`generate_glyph(seed, char)` returns a 2D list of `0`/`1` pixels. The same
`(seed, char)` pair always returns the identical bitmap.
`compose_specimen(seed, chars, columns)` lays those glyph bitmaps out on one
larger 2D list of `0`/`1` pixels, which `render_specimen_ascii` or
`write_png`/`encode_png` can then turn into ASCII art or a `.png` file.
`write_bdf(seed, chars, path)`/`encode_bdf(seed, chars)` render those same
glyphs as the text of a standard BDF bitmap font file.

## Status

This project is built autonomously, milestone by milestone, and every
change is gated on its automated test suite passing. Run the tests with:

```
python3 -m unittest discover -s tests
```
