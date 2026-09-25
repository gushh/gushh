"""Tiny pixel-art engine that writes crisp, compact, animated SVG.

Pixels are stored per layer as {(x, y): "#rrggbb"}. On export every layer
becomes one <g>, and every colour inside it one <path> made of merged
horizontal runs, so even busy scenes stay small.
"""

from fonts import FONTS


# --------------------------------------------------------------- colours

def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def hexc(r, g, b):
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(v))) for v in (r, g, b))


def mix(a, b, t):
    ra, rb = rgb(a), rgb(b)
    return hexc(*(ra[i] + (rb[i] - ra[i]) * t for i in range(3)))


def lighten(c, t):
    return mix(c, "#ffffff", t)


def darken(c, t):
    return mix(c, "#000000", t)


def luminance(c):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = rgb(c)
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def ramp(base):
    """Four-step shading ramp (highlight, light, base, shadow) for a colour."""
    return {"h": lighten(base, .55), "l": lighten(base, .25), "b": base, "d": darken(base, .35)}


# ----------------------------------------------------------------- layer

class Layer:
    def __init__(self, cls=None, attrs=None):
        self.px = {}
        self.cls = cls
        self.attrs = attrs or {}

    # primitives ---------------------------------------------------------
    def set(self, x, y, c):
        if c is None:
            self.px.pop((x, y), None)
        else:
            self.px[(x, y)] = c

    def get(self, x, y):
        return self.px.get((x, y))

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def hline(self, x, y, w, c):
        self.rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.rect(x, y, 1, h, c)

    def disc(self, cx, cy, r, c):
        for yy in range(int(cy - r) - 1, int(cy + r) + 2):
            for xx in range(int(cx - r) - 1, int(cx + r) + 2):
                if (xx + .5 - cx) ** 2 + (yy + .5 - cy) ** 2 <= r * r:
                    self.set(xx, yy, c)

    def sprite(self, x, y, art, pal, flip=False, scale=1):
        rows = art if isinstance(art, list) else [r for r in art.strip("\n").split("\n")]
        w = max(len(r) for r in rows)
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                c = pal.get(ch)
                if c is None:
                    continue
                ii = (w - 1 - i) if flip else i
                self.rect(x + ii * scale, y + j * scale, scale, scale, c)

    def merge(self, other, dx=0, dy=0):
        for (x, y), c in other.px.items():
            self.set(x + dx, y + dy, c)

    # export -------------------------------------------------------------
    def paths(self):
        by_colour = {}
        for (x, y), c in self.px.items():
            by_colour.setdefault(c, {}).setdefault(y, []).append(x)
        out = []
        for c in sorted(by_colour):
            rows = by_colour[c]
            d = []
            for y in sorted(rows):
                xs = sorted(rows[y])
                start = prev = xs[0]
                for x in xs[1:] + [None]:
                    if x is not None and x == prev + 1:
                        prev = x
                        continue
                    d.append("M%d %dh%dv1h-%dz" % (start, y, prev - start + 1, prev - start + 1))
                    if x is not None:
                        start = prev = x
            fill = c
            extra = ""
            if len(c) == 9:  # #rrggbbaa -> fill + opacity
                fill, alpha = c[:7], int(c[7:], 16) / 255
                extra = ' fill-opacity="%.2f"' % alpha
            out.append('<path fill="%s"%s d="%s"/>' % (fill, extra, "".join(d)))
        return "".join(out)

    def svg(self):
        attrs = "".join(' %s="%s"' % kv for kv in self.attrs.items())
        cls = ' class="%s"' % self.cls if self.cls else ""
        return "<g%s%s>%s</g>" % (cls, attrs, self.paths())


# ------------------------------------------------------------------ text

def glyph(ch, font):
    f = FONTS[font]
    return f["glyphs"].get(ch) or f["glyphs"].get(ch.upper())


def text_width(s, font="big", scale=1):
    f = FONTS[font]
    w = 0
    for i, ch in enumerate(s):
        if ch == " ":
            w += f["space"]
        else:
            g = glyph(ch, font)
            w += len(g[1][0]) if g else f["space"]
        if i < len(s) - 1:
            w += f["tracking"]
    return w * scale


def text_mask(s, font="big", scale=1, x=0, y=0):
    """Return the set of pixels for a string whose cap line is at y."""
    f = FONTS[font]
    pts = set()
    cx = 0
    for i, ch in enumerate(s):
        if ch == " ":
            cx += f["space"] + f["tracking"]
            continue
        g = glyph(ch, font)
        if not g:
            raise KeyError("glyph %r missing in font %s" % (ch, font))
        top, rows = g
        for j, row in enumerate(rows):
            for k, p in enumerate(row):
                if p == "#":
                    for sy in range(scale):
                        for sx in range(scale):
                            pts.add((x + (cx + k) * scale + sx, y + (top + j) * scale + sy))
        cx += len(rows[0]) + f["tracking"]
    return pts


def draw_text(layer, x, y, s, colour, font="big", scale=1):
    for p in text_mask(s, font, scale, x, y):
        layer.set(p[0], p[1], colour)
    return text_width(s, font, scale)


def dilate(pts, r=1, diagonal=True):
    out = set(pts)
    for (x, y) in pts:
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if not diagonal and abs(dx) + abs(dy) > r:
                    continue
                out.add((x + dx, y + dy))
    return out


def outline_of(pts, diagonal=True):
    return dilate(pts, 1, diagonal) - set(pts)


# ------------------------------------------------------------ document

class Doc:
    """An SVG document built from ordered layers + raw snippets."""

    def __init__(self, w, h, title, desc="", scale=3):
        self.w, self.h, self.scale = w, h, scale
        self.title, self.desc = title, desc
        self.items = []
        self.css = []

    def add(self, item):
        self.items.append(item)
        return item

    def layer(self, cls=None, **attrs):
        return self.add(Layer(cls, {k.replace("_", "-"): v for k, v in attrs.items()}))

    def raw(self, s):
        self.items.append(s)

    def style(self, css):
        self.css.append(css)

    def render(self):
        body = []
        for it in self.items:
            if isinstance(it, Layer):
                if it.px:
                    body.append(it.svg())
            else:
                body.append(it)
        css = "".join(self.css)
        css += "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
            'shape-rendering="crispEdges" role="img" aria-labelledby="t d">'
            '<title id="t">%s</title><desc id="d">%s</desc>'
            "<style>%s</style>%s</svg>\n"
            % (self.w, self.h, self.w * self.scale, self.h * self.scale,
               esc(self.title), esc(self.desc), css, "".join(body))
        )


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def keyframes_steps(name, frames, prop="transform"):
    """Discrete keyframes: frames is a list of (percent, value)."""
    parts = ["%s%%{%s:%s}" % (("%.3f" % p).rstrip("0").rstrip("."), prop, v) for p, v in frames]
    return "@keyframes %s{%s}" % (name, "".join(parts))
