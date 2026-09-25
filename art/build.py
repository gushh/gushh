#!/usr/bin/env python3
"""Generates every pixel-art SVG used by the profile README.

    python3 art/build.py

All art is drawn on a 280px-wide grid and exported at 3x, so the README
shows the same pixel size everywhere. Each asset comes in a "dark" and a
"light" flavour, picked by <picture> according to the visitor's GitHub
theme. No dependencies beyond the Python standard library.
"""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sprites as S  # noqa: E402
from pixel import (Doc, Layer, darken, dilate, draw_text, keyframes_steps,  # noqa: E402
                   lighten, mix, outline_of, ramp, text_mask, text_width)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets")
W = 280

PHP = "#777bb4"
LARAVEL = "#ff2d20"
INK = "#16142b"

THEMES = {
    "dark": {
        "rings": ["#05050c", "#e9e9f2", "#e9e9f2", "#05050c"],
        "bg": "#0f1022", "panel": "#171933", "panel_edge": "#2a2d52",
        "text": "#f2f2f7", "dim": "#9aa0c3", "faint": "#34375f",
        "php": "#a6aae6", "red": "#ff5a4e", "gold": "#ffc94d", "green": "#5bd69b",
        "cursor": "#ffc94d", "shine": "#ffffff38",
    },
    "light": {
        "rings": ["#2e3553", "#2e3553", "#a9b8e6", "#fbfaf5"],
        "bg": "#fbfaf5", "panel": "#eef0f8", "panel_edge": "#cfd5ea",
        "text": "#1f2440", "dim": "#5b617e", "faint": "#c9cee3",
        "php": "#4f5396", "red": "#cf2418", "gold": "#a8670f", "green": "#23855a",
        "cursor": "#d9480f", "shine": "#ffffff99",
    },
}


def save(name, doc):
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(doc.render())
    return path


# ------------------------------------------------------------ primitives

def window(L, x, y, w, h, t, fill=None):
    """RPG dialogue window: Dragon-Quest style in dark, Pokemon style in light."""
    rings = t["rings"]
    L.rect(x, y, w, h, fill or t["bg"])
    for i, c in enumerate(rings):
        xx, yy, ww, hh = x + i, y + i, w - 2 * i, h - 2 * i
        L.hline(xx, yy, ww, c)
        L.hline(xx, yy + hh - 1, ww, c)
        L.vline(xx, yy, hh, c)
        L.vline(xx + ww - 1, yy, hh, c)
    # rounded outer corners
    for cx, cy in ((x, y), (x + w - 1, y), (x, y + h - 1), (x + w - 1, y + h - 1)):
        L.set(cx, cy, None)
    for cx, cy in ((x + 1, y + 1), (x + w - 2, y + 1), (x + 1, y + h - 2), (x + w - 2, y + h - 2)):
        L.set(cx, cy, rings[0])
    return len(rings)


def panel(L, x, y, w, h, t):
    L.rect(x + 1, y, w - 2, h, t["panel_edge"])
    L.rect(x, y + 1, w, h - 2, t["panel_edge"])
    L.rect(x + 1, y + 1, w - 2, h - 2, t["panel"])


def fancy_text(L, x, y, s, scale, bands, depth_c, outline, ring=None, depth=2):
    """Arcade logo text: banded fill, extruded depth, outline and outer ring."""
    fill = text_mask(s, "big", scale, x, y)
    solid = set(fill)
    for (px, py) in fill:
        for k in range(1, depth + 1):
            solid.add((px, py + k))
    edge = outline_of(solid)
    if ring:
        for p in outline_of(solid | edge):
            L.set(p[0], p[1], ring)
    for p in edge:
        L.set(p[0], p[1], outline)
    for p in solid - fill:
        L.set(p[0], p[1], depth_c)
    ys = sorted({p[1] for p in fill})
    top, bottom = ys[0], ys[-1]
    for (px, py) in fill:
        f = (py - top) / max(1, bottom - top)
        L.set(px, py, bands[min(len(bands) - 1, int(f * len(bands)))])


def sparkle(L, x, y, c, big=False):
    L.set(x, y, "#ffffff")
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        L.set(x + dx, y + dy, c)
    if big:
        for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
            L.set(x + dx, y + dy, c)


def item_palette(base, accent=None):
    p = dict(S.ITEM_FIXED)
    p.update(ramp(base))
    if accent:
        p["h"] = accent
    p["x"] = "#cfe8ff"
    return p


def dither_band(L, x, y, w, c1, c2):
    for i in range(w):
        L.set(x + i, y, c1 if (i + y) % 2 else c2)


# ------------------------------------------------------------------ hero

SKIES = {
    "dark": ["#0b0a1f", "#110f2c", "#171438", "#1f1846", "#291c53", "#361f5e", "#472368", "#5a2870"],
    "light": ["#3d9bff", "#55a9ff", "#6db7ff", "#86c4ff", "#9fd0ff", "#b8ddff", "#cfe8ff", "#e4f2ff"],
}


def sky(L, pal, h):
    n = len(pal)
    band = h / n
    for i, c in enumerate(pal):
        y0, y1 = int(i * band), int((i + 1) * band)
        L.rect(0, y0, W, y1 - y0, c)
        if i:
            dither_band(L, 0, y0, W, pal[i - 1], c)
            dither_band(L, 0, y0 + 1, W, c, c)


def buildings(rng, y_base, hmin, hmax, wmin, wmax):
    out, x = [], -rng.randint(0, 6)
    while x < W:
        w = rng.randint(wmin, wmax)
        h = rng.randint(hmin, hmax)
        out.append((x, y_base - h, w, h))
        x += w + rng.choice([0, 0, 1, 2])
    return out


def draw_city(L, blds, body, edge, win_off, win_on, rng, lit=0.25, roof_bits=True):
    lit_windows = []
    for (x, y, w, h) in blds:
        L.rect(x, y, w, h, body)
        L.hline(x, y, w, edge)
        if roof_bits and w > 10 and rng.random() < .45:
            kind = rng.choice(["antenna", "tank", "step"])
            if kind == "antenna":
                ax = x + rng.randint(2, w - 3)
                L.vline(ax, y - 5, 5, body)
                L.set(ax, y - 6, "#ff4a3d")
            elif kind == "tank":
                tx = x + rng.randint(1, w - 7)
                L.rect(tx, y - 4, 6, 3, body)
                L.hline(tx, y - 4, 6, edge)
                L.vline(tx + 1, y - 1, 1, body)
                L.vline(tx + 4, y - 1, 1, body)
            else:
                L.rect(x + 2, y - 3, w - 4, 3, body)
                L.hline(x + 2, y - 3, w - 4, edge)
        for wy in range(y + 3, y + h - 2, 4):
            for wx in range(x + 2, x + w - 2, 3):
                if rng.random() < lit:
                    lit_windows.append((wx, wy))
                    L.rect(wx, wy, 1, 2, win_on)
                else:
                    L.rect(wx, wy, 1, 2, win_off)
    return lit_windows


def hero(theme):
    night = theme == "dark"
    H = 132
    rng = random.Random(13)
    d = Doc(W, H, "Gus Fernández | Sr. PHP & Laravel Developer 🚀",
            "Escena pixel art: un desarrollador programando en una terraza con el elePHPant, "
            + ("de noche bajo las estrellas." if night else "en un día soleado."))
    css = []

    # -- sky ------------------------------------------------------------
    L = d.layer()
    sky(L, SKIES[theme], 100)

    title_box = (18, 2, 246, 42)
    ribbon_box = (56, 42, 170, 18)
    moon_box = (238, 46, 22, 22)

    def free(x, y, pad=2):
        for bx, by, bw, bh in (title_box, ribbon_box, moon_box):
            if bx - pad <= x < bx + bw + pad and by - pad <= y < by + bh + pad:
                return False
        return True

    if night:
        stars = [L, d.layer("tw1"), d.layer("tw2"), d.layer("tw3")]
        for i in range(90):
            x, y = rng.randint(1, W - 2), rng.randint(1, 78)
            if not free(x, y):
                continue
            layer = stars[i % 4]
            c = rng.choice(["#ffffff", "#fff1b8", "#b8dcff", "#d9c8ff"])
            if rng.random() < .12:
                sparkle(layer, x, y, mix(c, SKIES[theme][2], .4))
            else:
                layer.set(x, y, c if y < 60 else mix(c, SKIES[theme][5], .35))
        css.append(".tw1{animation:tw 3s steps(1) infinite}.tw2{animation:tw 4.2s steps(1) infinite -1.3s}"
                   ".tw3{animation:tw 2.3s steps(1) infinite -.7s}"
                   "@keyframes tw{0%,100%{opacity:1}50%{opacity:.15}}")
        # shooting star
        ss = d.layer("shoot")
        for i in range(9):
            ss.set(40 + i * 2, 8 + i, mix("#ffffff", SKIES[theme][1], i / 9))
            ss.set(41 + i * 2, 8 + i, mix("#ffffff", SKIES[theme][1], i / 9))
        css.append(".shoot{animation:shoot 9s steps(1) infinite 2s;opacity:0}"
                   "@keyframes shoot{0%{opacity:0;transform:translate(0,0)}"
                   "80%{opacity:0;transform:translate(0,0)}"
                   "81%{opacity:1;transform:translate(0,0)}"
                   "84%{opacity:1;transform:translate(18px,9px)}"
                   "87%{opacity:1;transform:translate(36px,18px)}"
                   "88%{opacity:0;transform:translate(36px,18px)}"
                   "100%{opacity:0}}")
        # moon
        m = d.layer()
        m.sprite(242, 48, S.MOON, {"o": "#2b2150", "m": "#fff4c9", "c": "#e6d49a"})
        halo = d.layer()
        for (x, y) in outline_of({(242 + i, 48 + j) for j, r in enumerate(S.MOON) for i, ch in enumerate(r) if ch != "."}):
            if not m.get(x, y):
                halo.set(x, y, "#ffffff22")
    else:
        sun = d.layer()
        sun.disc(249, 57, 7.5, "#fff3b0")
        sun.disc(249, 57, 6.5, "#ffd84d")
        sun.disc(247.5, 55.5, 3, "#fff3b0")
        rays = d.layer("rays")
        for dx, dy in ((0, -11), (0, 11), (-11, 0), (11, 0), (-8, -8), (8, 8), (-8, 8), (8, -8)):
            rays.rect(249 + dx - (dx > 0) + (dx < 0), 57 + dy - (dy > 0) + (dy < 0), 2, 2, "#ffe27a")
        css.append(".rays{animation:rays 1.6s steps(1) infinite}@keyframes rays{50%{opacity:.35}}")
        # clouds + birds
        for i, (cx, cy, speed) in enumerate(((10, 50, 5), (150, 30, 7), (96, 66, 6))):
            cl = d.layer("c%d" % i)
            cl.sprite(cx, cy, S.CLOUD, {"w": "#ffffff", "s": "#d7ecff"})
            left, right = cx + 23, W - cx
            f = left / (left + right) * 100
            css.append(".c%d{animation:c%d %ds infinite}@keyframes c%d{"
                       "0%%{transform:translateX(0);animation-timing-function:steps(%d)}"
                       "%.2f%%{transform:translateX(-%dpx)}"
                       "%.2f%%{transform:translateX(%dpx);animation-timing-function:steps(%d)}"
                       "100%%{transform:translateX(0)}}"
                       % (i, i, (left + right) * speed // 10, i, left, f, left, f + .01, right, right))
        for i, (bx, by) in enumerate(((70, 60), (80, 56), (88, 62))):
            for f in (0, 1):
                bl = d.layer("bird%d" % f)
                bl.sprite(bx, by, S.BIRD[f], {"o": "#2e3553"})
        css.append(".bird0{animation:flap .5s steps(1) infinite}.bird1{animation:flap .5s steps(1) infinite -.25s}"
                   "@keyframes flap{50%{opacity:0}}")

    # -- title ----------------------------------------------------------
    T = d.layer()
    name = "GUS FERNÁNDEZ"
    tw = text_width(name, "big", 3)
    tx = (W - tw) // 2
    fancy_text(T, tx, 14, name, 3,
               bands=["#ffffff", "#ffd9d4", "#ff8f84", "#ff5a4e", LARAVEL, "#e0261a"],
               depth_c="#8d130c", outline=INK, ring=PHP if night else "#ffffff")
    tsp = d.layer("tsp")
    for i, (sx, sy) in enumerate(((tx + 4, 16), (tx + 118, 11), (tx + 205, 33), (tx + 70, 36))):
        lay = d.layer("sp%d" % i)
        sparkle(lay, sx, sy, "#fff4c2", big=True)
        css.append(".sp%d{animation:sp 4s steps(1) infinite %.1fs;opacity:0}" % (i, i * 1.0))
    css.append("@keyframes sp{0%,12%{opacity:1}13%,100%{opacity:0}}")
    del tsp

    # ribbon with subtitle
    R = d.layer()
    sub = "SR. PHP & LARAVEL DEVELOPER"
    sw = text_width(sub, "big")
    rw = sw + 16
    rx, ry = (W - rw) // 2, 45
    rib, rib_d, rib_h = PHP, darken(PHP, .35), lighten(PHP, .3)
    # folded tails with a V notch, tucked behind the band
    for side in (-1, 1):
        ex = rx - 10 if side < 0 else rx + rw - 2
        mask = set()
        for yy in range(ry + 3, ry + 15):
            depth = max(0, 3 - abs(yy - (ry + 8.5)) + .5)
            for xx in range(ex, ex + 12):
                cut = (xx - ex) < depth if side < 0 else (ex + 11 - xx) < depth
                if not cut:
                    mask.add((xx, yy))
        for p in outline_of(mask, diagonal=False):
            R.set(p[0], p[1], INK)
        for p in mask:
            R.set(p[0], p[1], rib_d)
        fx = rx if side < 0 else rx + rw - 2
        R.rect(fx, ry + 12, 2, 3, darken(PHP, .6))
    R.rect(rx, ry, rw, 12, rib)
    R.hline(rx, ry, rw, INK)
    R.hline(rx, ry + 11, rw, INK)
    R.hline(rx, ry + 1, rw, rib_h)
    R.hline(rx, ry + 10, rw, rib_d)
    R.vline(rx, ry, 12, INK)
    R.vline(rx + rw - 1, ry, 12, INK)
    draw_text(R, rx + 8, ry + 3, sub, INK, "big")
    draw_text(R, rx + 8, ry + 2, sub, "#ffffff", "big")

    # -- city -----------------------------------------------------------
    far = d.layer()
    if night:
        fb, fe, foff, fon = "#241d4c", "#302863", "#2d2659", "#ffd166"
        nb, ne, noff, non = "#16122e", "#221c42", "#1f1a3d", "#ffb84d"
    else:
        fb, fe, foff, fon = "#a3bddc", "#b8cde6", "#b5cbe5", "#e8f3ff"
        nb, ne, noff, non = "#7593bb", "#8aa6ca", "#6886ae", "#dcecff"
    fblds = buildings(rng, 100, 16, 34, 9, 20)
    fl = draw_city(far, fblds, fb, fe, foff, fon, rng, lit=.18 if night else .5)
    # rocket launching behind the skyline
    rk = d.layer("rocket")
    rk.sprite(246, 88, S.ROCKET, S.ROCKET_PAL)
    for f in (0, 1):
        fl_ = d.layer("fl%d rocket" % f)
        fl_.sprite(246, 99, S.FLAME[f], {"y": "#ffd166", "f": "#ff7a3d"})
    css.append(".rocket{animation:launch 11s infinite 1s}"
               "@keyframes launch{0%,62%{transform:translateY(0);opacity:0}"
               "62.01%{transform:translateY(0);opacity:1;animation-timing-function:steps(75)}"
               "92%,100%{transform:translateY(-150px);opacity:1}}"
               ".fl0{animation:launch 11s infinite 1s,fl .2s steps(1) infinite}"
               ".fl1{animation:launch 11s infinite 1s,fl .2s steps(1) infinite -.1s}"
               "@keyframes fl{50%{opacity:0}}")
    near = d.layer()
    nblds = buildings(rng, 100, 6, 20, 12, 26)
    nl = draw_city(near, nblds, nb, ne, noff, non, rng, lit=.22 if night else .35)
    if night:
        for k, cls in enumerate(("w1", "w2")):
            wl = d.layer(cls)
            for (x, y) in rng.sample(fl + nl, 10):
                wl.rect(x, y, 1, 2, "#fff1b8" if k else "#7fdcff")
        css.append(".w1{animation:tw 5s steps(1) infinite}.w2{animation:tw 7s steps(1) infinite -2s}")

    # -- string lights ---------------------------------------------------
    wire = d.layer()
    bulbs = [d.layer("b0"), d.layer("b1")]
    wire_c = "#0b0a1f" if night else "#3b4262"
    colors = ["#ff5a4e", "#ffc94d", "#5bd69b", "#6cb6ff", "#c39bff"]
    pts = []
    for x in range(0, W):
        t = x / (W - 1)
        y = int(round(84 + 10 * (1 - (2 * t - 1) ** 2)))
        wire.set(x, y, wire_c)
        pts.append((x, y))
    for i, x in enumerate(range(6, W, 11)):
        y = pts[x][1]
        c = colors[i % len(colors)]
        lay = bulbs[i % 2]
        wire.set(x, y + 1, wire_c)
        cc = c if night else mix(c, "#ffffff", .15)
        lay.rect(x, y + 2, 1, 2, cc)
        lay.set(x - 1, y + 2, cc if night else None)
        lay.set(x + 1, y + 2, cc if night else None)
        if night:
            lay.set(x, y + 4, c + "88")
    if night:
        css.append(".b0{animation:tw 1.4s steps(1) infinite}.b1{animation:tw 1.4s steps(1) infinite -.7s}")

    # -- rooftop ---------------------------------------------------------
    roof = d.layer()
    if night:
        top, wall, wall_d, floor, floor_l = "#3d3a66", "#2a2748", "#221f3d", "#1b1932", "#24213f"
    else:
        top, wall, wall_d, floor, floor_l = "#d9d4e6", "#aaa3c0", "#968eae", "#8b84a3", "#9790ad"
    roof.rect(0, 100, W, 6, wall)
    roof.hline(0, 100, W, top)
    for x in range(0, W, 14):
        roof.vline(x, 101, 5, wall_d)
    roof.rect(0, 106, W, H - 106, floor)
    for y in range(110, H, 7):
        roof.hline(0, y, W, floor_l)
    for y in range(106, H, 7):
        off = 0 if (y // 7) % 2 else 9
        for x in range(off, W, 18):
            roof.vline(x, y + 4, 3, floor_l)

    # -- server rack with blinking LEDs (left) + neon sign ---------------
    sv = d.layer()
    sx0, sy0 = 36, 104
    sv.rect(sx0, sy0, 16, 24, INK)
    sv.rect(sx0 + 1, sy0 + 1, 14, 22, "#3a3f58")
    for k in range(4):
        yy = sy0 + 3 + k * 5
        sv.rect(sx0 + 2, yy, 12, 4, "#23273a")
        sv.hline(sx0 + 2, yy, 12, "#4a5070")
        sv.hline(sx0 + 7, yy + 2, 5, "#161a28")
    sv.rect(sx0 + 1, sy0 + 23, 3, 2, INK)
    sv.rect(sx0 + 12, sy0 + 23, 3, 2, INK)
    for k in range(4):
        led = d.layer("led%d" % (k % 2))
        yy = sy0 + 5 + k * 5
        led.set(sx0 + 3, yy, "#5bd69b")
        led.set(sx0 + 5, yy, "#ffc94d" if k % 2 else "#6cb6ff")
    css.append(".led0{animation:tw .7s steps(1) infinite}.led1{animation:tw 1.1s steps(1) infinite -.4s}")
    nx, ny = 58, 71
    ne_ = d.layer()
    ne_.rect(nx, ny, 25, 11, INK)
    ne_.rect(nx + 1, ny + 1, 23, 9, "#1b1433" if night else "#3b4262")
    neon = d.layer("neon")
    draw_text(neon, nx + 4, ny + 3, "PHP", "#ff7ad9" if night else "#ffb3ec", "small")
    neon.set(nx + 20, ny + 3, "#7fdcff")
    neon.set(nx + 20, ny + 5, "#7fdcff")
    neon.set(nx + 20, ny + 7, "#7fdcff")
    ne_.vline(nx + 5, ny + 11, 3, INK)
    ne_.vline(nx + 19, ny + 11, 3, INK)
    css.append(".neon{animation:neon 5s steps(1) infinite}"
               "@keyframes neon{0%,40%,44%,48%,100%{opacity:1}42%,46%{opacity:.2}}")

    # -- desk + monitor ---------------------------------------------------
    D = d.layer()
    mx, my, mw, mh = 114, 70, 50, 34
    D.rect(mx, my, mw, mh, INK)
    D.rect(mx + 1, my + 1, mw - 2, mh - 2, "#3a3f58")
    D.hline(mx + 1, my + 1, mw - 2, "#565d7e")
    scr = (mx + 3, my + 3, mw - 6, mh - 7)
    D.rect(*scr, "#0d1424")
    D.set(mx + mw - 5, my + mh - 3, "#5bd69b")
    D.rect(mx + mw // 2 - 3, my + mh, 6, 3, "#2a2d3e")
    D.rect(mx + mw // 2 - 7, my + mh + 3, 14, 1, "#2a2d3e")
    # desk
    dx0, dy0, dw = 92, 108, 96
    D.rect(dx0, dy0, dw, 4, "#8a5a3c")
    D.hline(dx0, dy0, dw, "#b07a52")
    D.hline(dx0, dy0 + 3, dw, "#5e3a24")
    D.rect(dx0 + 3, dy0 + 4, 3, H - dy0 - 6, "#5e3a24")
    D.rect(dx0 + dw - 6, dy0 + 4, 3, H - dy0 - 6, "#5e3a24")
    D.sprite(dx0 + 4, dy0 - 9, S.PLANT, S.PLANT_PAL)
    D.sprite(dx0 + dw - 14, dy0 - 7, S.MUG, S.MUG_PAL)
    steam = d.layer("steam")
    steam.sprite(dx0 + dw - 14, dy0 - 7, [".s.s..", "..s.s."], {"s": "#cfd6e4"})
    css.append(".steam{animation:steam 1.2s steps(1) infinite}@keyframes steam{50%{transform:translate(1px,-1px)}}")
    if night:
        glow = d.layer()
        for y in range(dy0, dy0 + 1):
            for x in range(mx - 6, mx + mw + 6):
                glow.set(x, y, "#8fd3ff33")

    # code lines typing on the screen
    code = [
        [(PHP, 5), ("#e6e6f0", 9)],
        [(LARAVEL, 7), ("#e6e6f0", 4), ("#ffd166", 8)],
        [(None, 3), ("#5bd69b", 6), ("#e6e6f0", 12)],
        [(None, 3), ("#6cb6ff", 9), ("#ffd166", 5)],
        [(None, 6), (LARAVEL, 4), ("#e6e6f0", 14)],
        [(None, 3), ("#c39bff", 7), ("#e6e6f0", 5)],
        [("#e6e6f0", 2)],
    ]
    n = len(code)
    for i, line in enumerate(code):
        lay = d.layer("ln%d" % i)
        x = scr[0] + 2
        y = scr[1] + 2 + i * 3
        for c, w in line:
            if c:
                lay.hline(x, y, w, c)
            x += w + 1
        a = (i + 1) / (n + 3) * 100
        css.append(".ln%d{animation:ln%d 8s infinite}@keyframes ln%d{0%%,%.1f%%{opacity:0}%.1f%%,96%%{opacity:1}96.1%%,100%%{opacity:0}}"
                   % (i, i, i, a, a + .1))
    cur = d.layer("cur")
    cur.rect(scr[0] + 2, scr[1] + 2 + n * 3 - 1, 3, 2, "#ffffff")
    css.append(".cur{animation:tw 1s steps(1) infinite}")

    # -- dev (back view) with bobbing head --------------------------------
    dvx, dvy = 130, 99
    body = d.layer()
    head = d.layer("bob")
    for j, row in enumerate(S.DEV_BACK):
        target = head if j < 9 else body
        target.sprite(dvx, dvy + j, [row], S.DEV_BACK_PAL)
    css.append(".bob{animation:bob .9s steps(1) infinite}@keyframes bob{50%{transform:translateY(1px)}}")
    ch = d.layer()
    cx0 = dvx - 1
    ch.rect(cx0, 113, 20, 11, INK)
    ch.rect(cx0 + 1, 114, 18, 9, "#2b2f45")
    ch.hline(cx0 + 1, 114, 18, "#454b6b")
    ch.rect(cx0 + 8, 124, 4, 4, INK)
    ch.rect(cx0 + 2, 128, 16, 2, INK)
    ch.set(cx0 + 2, 130, "#454b6b")
    ch.set(cx0 + 17, 130, "#454b6b")

    # -- elePHPant --------------------------------------------------------
    ex, ey = 200, 111
    e = d.layer("ele")
    e.sprite(ex, ey, S.ELEPHANT[0], S.ELEPHANT_PAL, flip=True)
    css.append(".ele{animation:bob 1.3s steps(1) infinite -.3s}")
    for i in range(2):
        hl = d.layer("heart%d" % i)
        hl.sprite(ex + 6 + i * 4, ey - 6, [".#.#.", "#####", ".###.", "..#.."], {"#": "#ff5a8a"})
        css.append(".heart%d{animation:heart 6s steps(10) infinite %ds;opacity:0}" % (i, i * 3 + 1))
    css.append("@keyframes heart{0%{opacity:1;transform:translateY(0)}40%{opacity:1;transform:translateY(-10px)}"
               "41%,100%{opacity:0;transform:translateY(-10px)}}")

    d.style("".join(css))
    return d


# --------------------------------------------------------------- buttons

BUTTONS = [
    ("web", "MI SITIO WEB", "trece.ar", "#1e88e5", S.GLOBE),
    ("linkedin", "LINKEDIN", "gushh", "#0a66c2", S.INBOX),
    ("email", "EMAIL", "gus@trece.ar", "#e0443a", S.MAIL),
    ("calendly", "AGENDAR REUNIÓN", "Calendly", "#2ea44f", S.CAL),
]


def badge(L, x, y, size, colour):
    """Rounded, bevelled square used behind icons."""
    L.rect(x + 1, y, size - 2, size, INK)
    L.rect(x, y + 1, size, size - 2, INK)
    L.rect(x + 1, y + 1, size - 2, size - 2, colour)
    L.hline(x + 2, y + 1, size - 4, lighten(colour, .35))
    L.hline(x + 2, y + size - 2, size - 4, darken(colour, .3))


def button(theme, label, value, colour, icon, selected):
    t = THEMES[theme]
    w, h = 132, 26
    d = Doc(w, h, "%s: %s" % (label.title(), value))
    L = d.layer()
    window(L, 0, 0, w, h, t)
    badge(L, 7, 5, 16, colour)
    L.sprite(9, 7, icon, {"o": colour, "w": "#ffffff"})
    draw_text(L, 28, 6, label, t["dim"], "small")
    draw_text(L, 28, 13, value, t["text"], "big")
    arrow = d.layer("sel" if selected else None)
    draw_text(arrow, w - 13, 10, "▶", t["cursor"] if selected else t["faint"], "big")
    if selected:
        d.style(".sel{animation:nudge .8s steps(1) infinite}@keyframes nudge{50%{transform:translateX(2px)}}")
    return d


# --------------------------------------------------------------- headers

SECTIONS = [
    ("sobre-mi", "MUNDO 1-1", "SOBRE MÍ", S.HEART, S.HEART_PAL, PHP),
    ("stack", "MUNDO 1-2", "MI STACK TECNOLÓGICO", S.TOOLS, S.TOOLS_PAL, "#1e88e5"),
    ("experiencia", "MUNDO 1-3", "EXPERIENCIA DESTACADA", S.TROPHY, S.TROPHY_PAL, "#e0a31a"),
]


def header(theme, world, title, icon, pal, accent):
    t = THEMES[theme]
    w, h = W, 30
    d = Doc(w, h, title, "Encabezado de sección: %s" % world)
    L = d.layer()
    badge(L, 0, 3, 24, accent)
    iw, ih = max(len(r) for r in icon), len(icon)
    L.sprite((24 - iw) // 2, 3 + (24 - ih) // 2, icon, pal)
    draw_text(L, 31, 6, world, t["php"] if accent == PHP else accent if theme == "dark" else darken(accent, .25), "small")
    tw = draw_text(L, 31, 15, title, t["text"], "big")
    x0 = 31 + tw + 6
    for x in range(x0, w - 8):
        if (x - x0) % 3 != 2:
            L.set(x, 18, t["faint"])
    L.sprite(w - 7, 15, [".#.", "###", ".#."], {"#": accent})
    L.set(w - 6, 16, "#ffffff")
    sp = d.layer("spk")
    sparkle(sp, 22, 4, "#fff4c2")
    d.style(".spk{animation:spk 2.4s steps(1) infinite}@keyframes spk{0%,20%{opacity:1}21%,100%{opacity:0}}")
    return d


# ----------------------------------------------------------- profile card

def profile(theme):
    t = THEMES[theme]
    w, h = W, 76
    d = Doc(w, h, "Ficha de personaje: Gus Fernández",
            "Clase: Sr. PHP & Laravel Developer. Experiencia: +10 años. "
            "Foco: arquitectura, liderazgo y rendimiento. Clientes: toda Latinoamérica.")
    L = d.layer()
    window(L, 0, 0, w, h, t)
    # portrait
    px, py, pw, ph = 8, 8, 48, 60
    L.rect(px, py, pw, ph, INK)
    bg = ["#2a1f5c", "#34256b", "#40297a", "#4f2d86"] if theme == "dark" else ["#9fd0ff", "#b3daff", "#c7e4ff", "#dbeeff"]
    for i, c in enumerate(bg):
        L.rect(px + 1, py + 1 + i * 14, pw - 2, 15 if i < 3 else ph - 2 - i * 14, c)
    for sx, sy in ((px + 6, py + 6), (px + 40, py + 10), (px + 36, py + 4), (px + 8, py + 20)):
        L.set(sx, sy, "#ffffff" if theme == "dark" else "#ffffffcc")
    L.sprite(px + 4, py + ph - 44 - 1, S.DEV_FACE, S.DEV_FACE_PAL, scale=2)
    blink = d.layer("blink")
    for ex in (px + 4 + 6 * 2, px + 4 + 13 * 2):
        blink.rect(ex, py + ph - 45 + 9 * 2, 4, 4, S.DEV_FACE_PAL["s"])
        blink.rect(ex, py + ph - 45 + 10 * 2 + 1, 4, 1, INK)
    d.style(".blink{animation:blink 4s steps(1) infinite;opacity:0}@keyframes blink{0%,3%{opacity:1}3.1%,100%{opacity:0}}")
    # frame label
    L.rect(px + 8, py + ph - 4, pw - 16, 7, t["bg"])
    lw = text_width("LV 10+", "small")
    draw_text(L, px + (pw - lw) // 2, py + ph - 3, "LV 10+", t["gold"], "small")

    x0, vx = 64, 102
    draw_text(L, x0, 10, "GUS FERNÁNDEZ", t["text"], "big")
    for k in range(3):
        draw_text(L, w - 12 - k * 9, 10, "♥", t["red"], "big")
    L.hline(x0, 20, w - x0 - 8, t["faint"])
    rows = [("CLASE", 25), ("EXP", 37), ("FOCO", 49), ("CLIENTES", 61)]
    for label, y in rows:
        draw_text(L, x0, y + 1, label, t["dim"], "small")
    draw_text(L, vx, 25, "Sr. PHP & Laravel Developer", t["text"], "big")
    # XP bar
    bx, by, bw = vx, 37, 70
    L.rect(bx, by, bw, 7, INK)
    L.rect(bx + 1, by + 1, bw - 2, 5, "#e0a31a")
    L.hline(bx + 1, by + 1, bw - 2, "#ffe08a")
    L.hline(bx + 1, by + 5, bw - 2, "#b77a0d")
    shine = d.layer("xp")
    for k in range(3):
        shine.vline(bx + 3 + k, by + 1, 5, "#fff6cc")
    d.style(".xp{animation:xp 3s steps(32) infinite}@keyframes xp{0%{transform:translateX(0)}70%,100%{transform:translateX(62px)}}")
    draw_text(L, bx + bw + 5, 37, "+10 años", t["text"], "big")
    cx = vx
    for word, col in (("ARQUITECTURA", t["php"]), ("LIDERAZGO", t["red"]), ("RENDIMIENTO", t["green"])):
        ww = text_width(word, "small") + 6
        L.rect(cx + 1, 48, ww - 2, 9, col)
        L.rect(cx, 49, ww, 7, col)
        draw_text(L, cx + 3, 50, word, t["bg"], "small")
        cx += ww + 4
    draw_text(L, vx, 61, "Toda Latinoamérica", t["text"], "big")
    return d


# ------------------------------------------------------------- perk icons

def perk(icon, pal, anim):
    iw, ih = max(len(r) for r in icon), len(icon)
    d = Doc(20, 20, "icono")
    L = d.layer("fl")
    L.sprite((20 - iw) // 2, (20 - ih) // 2 + 1, icon, pal)
    d.style(".fl{animation:fl 2s steps(1) infinite %s}@keyframes fl{50%%{transform:translateY(-1px)}}" % anim)
    return d


# -------------------------------------------------------------- inventory

STACK = [
    ("BACKEND", S.SWORD, [
        ("PHP", "#777BB4"), ("Laravel", "#FF2D20"), ("Symfony", "#e8e8e8"),
        ("Yii Framework", "#40B3D8"), ("CodeIgniter", "#EF4223")]),
    ("BASES DE DATOS", S.POTION, [
        ("MySQL", "#4479A1"), ("MariaDB", "#1b6f86"), ("PostgreSQL", "#4169E1"),
        ("MongoDB", "#47A248"), ("Redis", "#DC382D")]),
    ("FRONTEND", S.GEM, [
        ("Vue.js", "#4FC08D"), ("Livewire", "#4E56A6"), ("Vite", "#B73BFE", "#FFD62E"),
        ("Tailwind CSS", "#38B2AC"), ("Bootstrap", "#7952B3"), ("HTML5", "#E34F26"), ("CSS3", "#1572B6")]),
    ("DEVOPS & INFRAESTRUCTURA", S.SHIELD, [
        ("Ubuntu", "#E95420"), ("DigitalOcean", "#0080FF"), ("Docker", "#2496ED")]),
    ("HERRAMIENTAS Y ENTORNOS", S.PICKAXE, [
        ("VS Code", "#007ACC"), ("Jira", "#0052CC"), ("GitKraken", "#179287"), ("GitHub", "#c9d1d9")]),
    ("FORMACIÓN", S.BOOK, [
        ("Laracasts", "#E12737"), ("Platzi", "#98CA3F"), ("Laravel Daily", "#E12737")]),
]


def wrap(words, width, font="small"):
    lines, cur = [], ""
    for wd in words.split(" "):
        test = (cur + " " + wd).strip()
        if text_width(test, font) <= width or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = wd
    return lines + [cur]


def inventory(theme):
    t = THEMES[theme]
    col_w, gap, x0, y0 = 85, 4, 8, 8
    row_h = 13
    specs = []
    for i, (cat, spr, items) in enumerate(STACK):
        lines = wrap(cat, col_w - 10)
        hh = 5 + len(lines) * 7 + 3 + len(items) * row_h + 4
        specs.append((cat, spr, items, lines, hh))
    col_h = [specs[i][4] + gap + specs[i + 3][4] for i in range(3)]
    inner = max(col_h)
    h = inner + 2 * y0
    alt = "; ".join("%s: %s" % (c.title(), ", ".join(it[0] for it in items)) for c, _, items in STACK)
    d = Doc(W, h, "Inventario — Mi Stack Tecnológico", alt)
    L = d.layer()
    window(L, 0, 0, W, h, t)
    positions = []
    for i, (cat, spr, items, lines, hh) in enumerate(specs):
        col = i % 3
        px = x0 + col * (col_w + gap)
        py = y0 if i < 3 else y0 + specs[i - 3][4] + gap
        ph = hh if i < 3 else inner - (py - y0)
        panel(L, px, py, col_w, ph, t)
        acc = t["php"] if theme == "dark" else t["php"]
        for k, line in enumerate(lines):
            draw_text(L, px + 5, py + 5 + k * 7, line, t["gold"], "small")
        yy = py + 5 + len(lines) * 7 + 1
        L.hline(px + 5, yy - 1, col_w - 10, t["panel_edge"])
        del acc
        for j, it in enumerate(items):
            name, colour = it[0], it[1]
            ry = yy + 2 + j * row_h
            L.sprite(px + 4, ry, spr, item_palette(colour, it[2] if len(it) > 2 else None))
            draw_text(L, px + 17, ry + 2, name, t["text"], "big")
            positions.append((px, ry))
    # selection cursor that hops through every item
    cur = d.layer("pick")
    bx, by = positions[0]
    cw, ch = col_w - 4, 12
    cx, cy = bx + 2, by - 1
    for (ax, ay, dx, dy) in ((cx, cy, 1, 1), (cx + cw - 1, cy, -1, 1), (cx, cy + ch - 1, 1, -1), (cx + cw - 1, cy + ch - 1, -1, -1)):
        cur.set(ax, ay, t["cursor"])
        cur.set(ax + dx, ay, t["cursor"])
        cur.set(ax, ay + dy, t["cursor"])
    n = len(positions)
    frames = []
    for k, (px, py) in enumerate(positions + [positions[0]]):
        frames.append((k / n * 100, "translate(%dpx,%dpx)" % (px - bx, py - by)))
    d.style(".pick{animation:pick %.1fs steps(1,end) infinite}" % (n * .9) + keyframes_steps("pick", frames))
    return d


# ------------------------------------------------------------ achievements

ACHIEVEMENTS = [
    ("liderazgo", "LIDERAZGO TÉCNICO", S.CROWN, S.CROWN_PAL),
    ("arquitectura", "ARQUITECTURA DE SOFTWARE", S.CASTLE, S.CASTLE_PAL),
    ("impacto", "PROYECTOS DE ALTO IMPACTO", S.STAR, S.STAR_PAL),
]


def achievement(theme, title, icon, pal, delay):
    t = THEMES[theme]
    w, h = W, 32
    d = Doc(w, h, "Logro desbloqueado: %s" % title.capitalize())
    L = d.layer()
    window(L, 0, 0, w, h, t)
    badge(L, 7, 5, 22, "#e0a31a")
    L.rect(9, 7, 18, 18, INK if theme == "dark" else "#2e3553")
    iw, ih = max(len(r) for r in icon), len(icon)
    L.sprite(9 + (18 - iw) // 2, 7 + (18 - ih) // 2, icon, pal)
    draw_text(L, 36, 8, "LOGRO DESBLOQUEADO", t["gold"], "small")
    draw_text(L, 36, 17, title, t["text"], "big")
    # completed check
    L.sprite(w - 20, 11, auto_check(), {"o": INK, "g": t["green"]})
    d.raw('<clipPath id="c"><rect x="4" y="4" width="%d" height="%d"/></clipPath><g clip-path="url(#c)">' % (w - 8, h - 8))
    shine = d.layer("shine")
    for k in range(7):
        for y in range(4, h - 4):
            x = 20 + k - (y - 4) // 2
            if k in (0, 1, 2, 5):
                shine.set(x, y, t["shine"])
    d.raw("</g>")
    d.style(".shine{animation:shine 5s steps(40) infinite %.1fs}"
            "@keyframes shine{0%%{transform:translateX(-30px)}40%%,100%%{transform:translateX(290px)}}" % delay)
    return d


def auto_check():
    return S.auto_outline([
        "........gg",
        ".......gg.",
        "gg....gg..",
        ".gg..gg...",
        "..gggg....",
        "...gg.....",
    ])


# ------------------------------------------------------------------ footer

def footer(theme):
    night = theme == "dark"
    t = THEMES[theme]
    H = 58
    rng = random.Random(7)
    d = Doc(W, H, "¡Gracias por jugar! ¿Continuar? Agendar reunión",
            "El elePHPant camina por el pasto de izquierda a derecha.")
    L = d.layer()
    pal = SKIES[theme]
    sky(L, pal[2:], 48)
    css = []
    if night:
        tw = d.layer("tw1")
        for i in range(30):
            x, y = rng.randint(1, W - 2), rng.randint(1, 38)
            (tw if i % 2 else L).set(x, y, rng.choice(["#ffffff", "#fff1b8", "#b8dcff"]))
        css.append(".tw1{animation:tw 3s steps(1) infinite}@keyframes tw{50%{opacity:.15}}")
    else:
        L.sprite(12, 6, S.CLOUD, {"w": "#ffffff", "s": "#d7ecff"})
        L.sprite(236, 12, S.CLOUD, {"w": "#ffffff", "s": "#d7ecff"})
    # ground
    g1, g2, d1, d2 = ("#3fa46a", "#2c7a4e", "#4a3024", "#3a241b") if night else ("#6fd08c", "#43a863", "#8a5a3c", "#6e4630")
    L.rect(0, 48, W, 10, d1)
    L.hline(0, 48, W, g1)
    L.hline(0, 49, W, g2)
    for x in range(0, W, 5):
        L.set(x + rng.randint(0, 2), 47, g1)
        L.set(rng.randint(0, W), 52 + rng.randint(0, 5), d2)
    for x in range(3, W, 23):
        L.sprite(x, 44, ["#.#", "###"], {"#": g1})
    # text
    msg = "¡GRACIAS POR JUGAR!"
    mw = text_width(msg, "big")
    fancy_text(L, (W - mw) // 2, 5, msg, 1,
               bands=["#ffffff", "#ffd9d4", "#ff8f84", LARAVEL], depth_c="#8d130c", outline=INK,
               ring=PHP if night else "#ffffff", depth=1)
    cta = d.layer("cta")
    s = "¿CONTINUAR? ▶ AGENDAR REUNIÓN"
    sw = text_width(s, "small")
    draw_text(cta, (W - sw) // 2 + 1, 19, s, INK if night else "#ffffff", "small")
    draw_text(cta, (W - sw) // 2, 18, s, "#fff4c2" if night else "#1f2440", "small")
    css.append(".cta{animation:cta 1.2s steps(1) infinite}@keyframes cta{70%{opacity:1}71%,100%{opacity:.25}}")
    # walking elephant
    walk = d.layer("walk")
    for f in (0, 1):
        fr = d.layer("wf%d" % f)
        fr.sprite(-30, 30, S.ELEPHANT[f], S.ELEPHANT_PAL)
    del walk
    css.append(".wf0,.wf1{animation:walk 16s steps(320) infinite}"
               "@keyframes walk{0%{transform:translateX(0)}100%{transform:translateX(320px)}}"
               ".wf0{animation:walk 16s steps(320) infinite,step .5s steps(1) infinite}"
               ".wf1{animation:walk 16s steps(320) infinite,step .5s steps(1) infinite -.25s}"
               "@keyframes step{50%{opacity:0}}")
    d.style("".join(css))
    return d


# ------------------------------------------------------------------- main

def main():
    os.makedirs(OUT, exist_ok=True)
    for theme in THEMES:
        save("hero-%s.svg" % theme, hero(theme))
        for i, (key, label, value, colour, icon) in enumerate(BUTTONS):
            save("btn-%s-%s.svg" % (key, theme), button(theme, label, value, colour, icon, i == 0))
        for key, world, title, icon, pal, accent in SECTIONS:
            save("title-%s-%s.svg" % (key, theme), header(theme, world, title, icon, pal, accent))
        save("profile-%s.svg" % theme, profile(theme))
        save("inventory-%s.svg" % theme, inventory(theme))
        for i, (key, title, icon, pal) in enumerate(ACHIEVEMENTS):
            save("logro-%s-%s.svg" % (key, theme), achievement(theme, title, icon, pal, i * 1.2))
        save("footer-%s.svg" % theme, footer(theme))
    for key, icon, pal, delay in (("arquitectura", S.TOWER, S.TOWER_PAL, "0s"),
                                  ("liderazgo", S.FLAG, S.FLAG_PAL, "-.6s"),
                                  ("clean-code", S.BRACES, S.BRACES_PAL, "-1.2s")):
        save("perk-%s.svg" % key, perk(icon, pal, delay))
    print("assets written to", OUT)


if __name__ == "__main__":
    main()
