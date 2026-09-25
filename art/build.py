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


# ------------------------------------------------------------------- main

def main():
    os.makedirs(OUT, exist_ok=True)
    for theme in THEMES:
        save("hero-%s.svg" % theme, hero(theme))
    print("assets written to", OUT)


if __name__ == "__main__":
    main()
