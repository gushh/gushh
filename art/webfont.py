#!/usr/bin/env python3
"""Turns the hand-drawn bitmap font into a real webfont (WOFF).

    pip install fonttools
    python3 art/webfont.py

One font pixel = 100 units, the cap height is 700 and accents reach 1000,
so at font-size 10px every pixel lands on exactly one screen pixel.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fontTools.fontBuilder import FontBuilder  # noqa: E402
from fontTools.pens.ttGlyphPen import TTGlyphPen  # noqa: E402

from fonts import FONTS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PX = 100
CAP = 7


def rects(top, rows):
    """Merge inked pixels into as few rectangles as possible (rows, then columns)."""
    runs = []
    for j, row in enumerate(rows):
        x = 0
        while x < len(row):
            if row[x] == "#":
                s = x
                while x < len(row) and row[x] == "#":
                    x += 1
                runs.append([s, x, top + j, top + j + 1])
            else:
                x += 1
    merged = []
    for r in runs:
        for m in merged:
            if m[0] == r[0] and m[1] == r[1] and m[3] == r[2]:
                m[3] = r[3]
                break
        else:
            merged.append(r)
    return merged


def build(font_key, family, out):
    f = FONTS[font_key]
    glyphs = f["glyphs"]
    order = [".notdef", "space"]
    cmap = {32: "space"}
    names = {}
    for ch in glyphs:
        name = "u%04X" % ord(ch)
        order.append(name)
        cmap[ord(ch)] = name
        names[name] = ch
    cap = f["cap"]
    track = f["tracking"]

    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    glyf, metrics = {}, {}

    empty = TTGlyphPen(None)
    glyf[".notdef"] = empty.glyph()
    glyf["space"] = TTGlyphPen(None).glyph()
    metrics[".notdef"] = ((f["space"] + track) * PX, 0)
    metrics["space"] = ((f["space"] + track) * PX, 0)
    for name, ch in names.items():
        top, rows = glyphs[ch]
        pen = TTGlyphPen(None)
        for x0, x1, y0, y1 in rects(top, rows):
            # rows grow downward; font units grow upward from the baseline
            bx0, bx1 = x0 * PX, x1 * PX
            by0, by1 = (cap - y1) * PX, (cap - y0) * PX
            pen.moveTo((bx0, by0))
            pen.lineTo((bx0, by1))
            pen.lineTo((bx1, by1))
            pen.lineTo((bx1, by0))
            pen.closePath()
        glyf[name] = pen.glyph()
        metrics[name] = ((len(rows[0]) + track) * PX, 0)

    asc, desc = (cap + 3) * PX, -2 * PX
    fb.setupGlyf(glyf)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=asc, descent=desc)
    fb.setupNameTable({"familyName": family, "styleName": "Regular"})
    fb.setupOS2(sTypoAscender=asc, sTypoDescender=desc, sTypoLineGap=0,
                usWinAscent=asc, usWinDescent=-desc, sxHeight=5 * PX, sCapHeight=cap * PX)
    fb.setupPost()
    # fixed timestamps keep the output byte-identical between runs
    fb.font["head"].created = fb.font["head"].modified = 3900000000
    fb.font.recalcTimestamp = False
    fb.font.flavor = "woff"
    fb.save(out)
    return out


if __name__ == "__main__":
    out_dir = os.path.join(ROOT, "site", "gen")
    os.makedirs(out_dir, exist_ok=True)
    print(build("big", "Gus Pixel", os.path.join(out_dir, "gus-pixel.woff")))
    print(build("small", "Gus Pixel Mini", os.path.join(out_dir, "gus-pixel-mini.woff")))
