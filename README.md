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

The previous milestone added a BDF (Glyph Bitmap Distribution Format)
exporter: the requested glyphs for a seed are written out as a plain-text
`.bdf` bitmap font file, the same format produced by classic X11 font
tools. BDF is just structured text, so the exporter is a small hand-rolled
text writer with no font-tooling dependency; the resulting file can be
loaded directly by terminal emulators, image/font editors (e.g. FontForge),
and converters like `bdftopcf` that expect a standard bitmap font.

This milestone adds golden-file tests: for a fixed seed, the exact glyph
bitmap arrays and the exact BDF file bytes are pinned against values
committed under `tests/golden/` (and one inline literal), so a future
change to the generator, rasterizer, or BDF writer that silently shifts
output for an existing seed gets caught even though nothing in those tests
calls the code twice to compare against itself.

This milestone polishes the CLI into a one-liner: running `glyphsmith
"my-repo-name"` with no other flags now writes `specimen.png` and
`font.bdf` for that seed directly, instead of requiring `--png`/`--bdf` to
opt in to each file. A `glyphsmith` console command is registered so the
tool is runnable by name after installing the package, not just via
`python3 -m glyphsmith`. The old per-glyph ASCII dump is still available,
now behind an explicit `--preview` flag, and `--out-dir` controls where the
default `specimen.png`/`font.bdf` land.

## Install

Requires Python 3.9+. glyphsmith has no runtime dependencies — everything
is built on the standard library (`random`, `hashlib`, `argparse`, `zlib`).

```
git clone <this-repository>
cd glyphsmith
pip install -e .
```

This registers a `glyphsmith` command. You can also skip installing and
run it as `python3 -m glyphsmith` from the repository root.

## Usage

The one-liner: forge a typeface for a seed and write both a specimen image
and a loadable font file into the current directory:

```
glyphsmith "my-repo-name"
```

This writes `specimen.png` (a rendered sheet of every supported glyph) and
`font.bdf` (the same glyphs as a BDF bitmap font) and prints the paths it
wrote. Write them somewhere else with `--out-dir`:

```
glyphsmith "my-repo-name" --out-dir build/
```

Render only a subset of characters:

```
glyphsmith "my-repo-name" --chars "ABC123"
```

Override the specimen/font paths individually, and tune the specimen
layout (`--columns` per row) and PNG pixel scale:

```
glyphsmith "my-repo-name" --png build/specimen.png --bdf build/myfont.bdf --columns 13 --scale 8
```

Also print the composed specimen sheet as ASCII art alongside writing the
files:

```
glyphsmith "my-repo-name" --specimen
```

Print each glyph as a separate ASCII art block instead of writing any
files, customizing the ink/blank characters used:

```
glyphsmith "my-repo-name" --chars "HELLO" --preview --on "X" --off " "
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
