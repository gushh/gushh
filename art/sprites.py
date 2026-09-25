"""Hand-placed sprites. One character = one pixel; '.' is transparent.

Palettes are resolved at draw time, so the same art can be recoloured
(e.g. every sword takes the colours of the technology it represents).
"""

def auto_outline(rows, thick=False):
    """Pad art by one pixel and wrap every inked pixel with an 'o' outline."""
    w = max(len(r) for r in rows)
    g = [["."] * (w + 2)] + [["."] + list(r.ljust(w, ".")) + ["."] for r in rows] + [["."] * (w + 2)]
    out = [r[:] for r in g]
    nb = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    if thick:
        nb += [(1, 1), (-1, -1), (1, -1), (-1, 1)]
    for y in range(len(g)):
        for x in range(w + 2):
            if g[y][x] != ".":
                continue
            for dx, dy in nb:
                yy, xx = y + dy, x + dx
                if 0 <= yy < len(g) and 0 <= xx < w + 2 and g[yy][xx] != ".":
                    out[y][x] = "o"
                    break
    return ["".join(r) for r in out]


# ---------------------------------------------------------------- elePHPant
# The PHP mascot, facing right. Two walking frames share the upper body.
_ELE_TOP = [
    "..................ooo.......",
    "........oooo....oohhhoo.....",
    ".....ooohhhhoo.ohhllbhho....",
    "...oohhhllllhhooolbbbbbho...",
    "..ohhlllbbbbloDddobbbbbbo...",
    ".ohllbbbbbbboDDddobbbowbho..",
    "ohlbbbbbbbbboDDddobbbobbbo..",
    "olbbbbbbbbbboDDddobbbbbbbo..",
    "obbbbbbbbbbboDDddobbbbbbbo..",
    "obbbbbbbbbbboDDDDobbbbbbbo..",
    "odbbbbbbbbbboDDDDobbbbbbbo..",
    ".odbbbbbbbbbbooooddddobbbo..",
    "..oddbbbbbbbbbbddbbooobbbo..",
    "..odddobbboodddobbbo.obbboo.",
    "..odddobbboodddobbbo.obbbhho",
    "..odddobbboodddobbbo.obbbbo.",
    "..odddobbboodddobbbo..oooo..",
]
ELEPHANT = [
    _ELE_TOP + [
        "..odddobbboodddobbbo........",
        "...ooo.ooo..ooo.ooo.........",
    ],
    _ELE_TOP + [
        "..odddooooooodddooooo.......",
        "...ooo......ooo.............",
    ],
]
ELEPHANT_PAL = {
    "o": "#1f1b3d", "h": "#b9bdf0", "l": "#9ea3dc", "b": "#7f84c4",
    "d": "#5b5f9c", "D": "#4a4e88", "e": "#1f1b3d", "w": "#ffffff",
}

# --------------------------------------------------------- developer (back)
# Seen from behind, sitting on a chair, headphones on, red hoodie.
DEV_BACK = [
    "......oooooo......",
    "....oohhhhhhoo....",
    "...ohhhhhhhhhho...",
    "..okkkkkkkkkkkko..",
    "..ok.hhhhhhhh.ko..",
    ".oqqohhhhhhhhoqqo.",
    ".oqqohhhhhhhhoqqo.",
    ".oqqoHhhhhhhHoqqo.",
    "..o.oHHhhhhHHo.o..",
    "....ossssssss o...",
    "..oorrrrrrrrrrroo.",
    ".orrrrrRRRRrrrrrro",
    "orrrrrRRddRRrrrrro",
    "orrrrrrRRRRrrrrrro",
    "orrrrrrrrrrrrrrrro",
    "orrrrrrrrrrrrrrrro",
    "oRrrrrrrrrrrrrrrRo",
    "oRRrrrrrrrrrrrrRRo",
    "oRRRRRRRRRRRRRRRRo",
    ".oooooooooooooooo.",
]
DEV_BACK_PAL = {
    "o": "#16142b", "h": "#4a2f25", "H": "#2f1d17", "k": "#2b2b3a",
    "q": "#ff2d20", "s": "#e9a77f", "r": "#ff2d20", "R": "#c71f15", "d": "#8d130c",
}

# ------------------------------------------------------ developer (portrait)
DEV_FACE = [
    "......oooooooo......",
    "....oohhhhhhhhoo....",
    "...ohhhhhhhhhhhho...",
    "..ohhhhhhhhhhhhhho..",
    "..ohhhhhhhhhhhhhho..",
    ".ohhsshhhhhhhhhhhho.",
    ".ohsssssssshhsssshho",
    ".ohsssssssssssssshho",
    ".ohssooossssooossho.",
    "okhssoewssssoewsshko",
    "okkssoeessssoeesskko",
    "okksssssssssssssskko",
    ".okssppssssssppssko.",
    "..osssssssmssssssso.",
    "..ossssssmmmsssssso.",
    "...osssssssssssso...",
    "....ooSSSSSSSSoo....",
    "..oorrrqrrrrqrrroo..",
    ".orrrrrqrrrrqrrrrro.",
    "orrrrrrqrrrrqrrrrrro",
    "orrrrrrwrrrrwrrrrrro",
    "orRrrrrrrrrrrrrrrRro",
]
DEV_FACE_PAL = {
    "o": "#16142b", "h": "#4a2f25", "s": "#e9a77f", "S": "#c9855f",
    "e": "#16142b", "w": "#ffffff", "p": "#f08a7a", "m": "#9c4a3a",
    "k": "#2b2b3a", "r": "#ff2d20", "R": "#c71f15", "q": "#ffd9d6",
}

# ------------------------------------------------------------ RPG items 10px
SWORD = [
    ".......ooo",
    "......ohho",
    ".....ohlbo",
    "....ohlbo.",
    ".o.ohlbo..",
    "ogoolbo...",
    ".oggbo....",
    "..oGgo....",
    ".owoogo...",
    "owo..oo...",
]
POTION = [
    "...oooo...",
    "...occo...",
    "...oxxo...",
    "...oxxo...",
    "..oxwxxo..",
    ".oghbbbbo.",
    ".ohlbbbdo.",
    ".olbbbbdo.",
    "..obbddo..",
    "...oooo...",
]
GEM = [
    "..oooooo..",
    ".ohhlllbo.",
    "ohhllllbbo",
    "oddddddddo",
    "olhlllbbdo",
    ".olllbbdo.",
    "..olbbdo..",
    "...obdo...",
    "....oo....",
    "..........",
]
SHIELD = [
    "oooooooooo",
    "oSsssssssSo"[:10],
    "oshhllbbSo",
    "oshllbbbSo",
    "oslbbbbdSo",
    "oslbbbbdSo",
    ".oSbbbddo.",
    ".oSSbddSo.",
    "..oSSSSo..",
    "...oooo...",
]
PICKAXE = [
    "..oooooo..",
    ".ohhllbbo.",
    "ohloooobdo",
    "obo.ow.odo",
    "oo..ow..oo",
    "....ow....",
    "....ow....",
    "....oW....",
    "....oW....",
    "....oo....",
]
BOOK = [
    ".ooooooo..",
    "ohlllllbo.",
    "olpppppbo.",
    "olbbbbbbo.",
    "olbbhhbbo.",
    "olbbbbbbo.",
    "olbbbbbbo.",
    "odddddddo.",
    "owwwwwwwoo",
    ".ooooooooo",
]
ITEM_FIXED = {
    "o": "#16142b", "g": "#f2c14e", "G": "#a8742a", "w": "#8b5a2b", "W": "#5e3a1a",
    "c": "#c08552", "s": "#dfe6ee", "S": "#8a96a6", "p": "#f3e3b5",
}

# ------------------------------------------------------------- icons 16px
HEART = [
    "................",
    "..ooooo..ooooo..",
    ".ohhrrroorrrrro.",
    "ohwhrrrrrrrrrrdo",
    "ohhrrrrrrrrrrrdo",
    "orrrrrrrrrrrrrdo",
    "orrrrrrrrrrrrrdo",
    ".orrrrrrrrrrrdo.",
    "..orrrrrrrrrdo..",
    "...orrrrrrrdo...",
    "....orrrrrdo....",
    ".....orrrdo.....",
    "......ordo......",
    ".......oo.......",
    "................",
    "................",
]
HEART_PAL = {"o": "#16142b", "h": "#ffb3ad", "w": "#ffffff", "r": "#ff2d20", "d": "#b3170e"}

TOOLS = [
    "..oo.........oo.",
    ".osso.......osso",
    "ossso......ossSo",
    "osSo.o....ossSo.",
    ".oSSSo...ossSo..",
    "..ooSSo.owwSo...",
    "....oSSowwWo....",
    ".....oSwwWo.....",
    ".....owwWSSo....",
    "....owwWo.oSSo..",
    "...owwWo...oSSo.",
    "..owwWo.....oSSo",
    ".owwWo.......oSo",
    "owwWo.........oo",
    "oWWo............",
    ".oo.............",
]
TOOLS_PAL = {"o": "#16142b", "s": "#e8eef5", "S": "#9aa7b8", "w": "#c98a4b", "W": "#8b5a2b"}

TROPHY = [
    "..oooooooooooo..",
    ".ohhhhgggggggGo.",
    "oooohgggggggGoooo"[:16],
    "ogo.ohggggggGo.go"[:16],
    "ogo.ohggggggGo.go"[:16],
    ".ogoohgggggGGoogo"[:16],
    "..oooohggggGoooo.",
    ".....ohgggGGo....",
    "......oggGGo.....",
    ".......oGGo......",
    ".......oGGo......",
    "......oggGGo.....",
    ".....oooooooo....",
    "....obbbbbbbbo...",
    "....oBBBBBBBBo...",
    "....oooooooooo...",
]
TROPHY_PAL = {"o": "#16142b", "h": "#fff4c2", "g": "#f2c14e", "G": "#c98a1f",
              "b": "#6e4a2a", "B": "#4a2f18"}

CROWN = [
    "................",
    "................",
    ".oo....oo....oo.",
    "ogho..ogho..ogho",
    "oggo..oggo..oggo",
    "ohgGo.ohgGo.ohGo"[:16],
    "ohggoohgggoohggo",
    "ohgggghgggggggGo",
    "ohggrrggbbggrrGo",
    "ohggrrggbbggrrGo",
    "ohgggggggggggGGo",
    "oooooooooooooooo",
    "ohhhhhhhhhhhhhGo",
    "oGGGGGGGGGGGGGGo",
    "oooooooooooooooo",
    "................",
]
CROWN_PAL = {"o": "#16142b", "h": "#fff4c2", "g": "#f2c14e", "G": "#c98a1f",
             "r": "#ff2d20", "b": "#4fc3f7"}

CASTLE = auto_outline([
    "hs.hs.hs.hs.hS",
    "hs.hs.hs.hs.hS",
    "hssssssssssssS",
    "hssssssssssssS",
    "hsswsssssswssS",
    "hsswsssssswssS",
    "hssssssssssssS",
    "hsssssbbsssssS",
    "hssssbbbbssssS",
    "hssssbbbbssssS",
    "hssssbbbbssssS",
    "hssssbbbbssssS",
])
CASTLE_PAL = {"o": "#16142b", "h": "#e8eef5", "s": "#b8c2d0", "S": "#7d889a", "b": "#3a2a1a", "w": "#3a2a1a"}

STAR = [
    ".......oo.......",
    "......ohgo......",
    "......ohgo......",
    ".....ohhggo.....",
    "oooooohhgggooooo",
    "ohhhhhhhggggggGo",
    ".ohhhhhggggggGo.",
    "..ohhhhgggggGo..",
    "...ohhhgggggo...",
    "...ohhgggggGo...",
    "..ohhggoogggGo..",
    "..ohgoo..oogGo..",
    ".ohoo......ooGo.",
    ".oo..........oo.",
    "................",
    "................",
]
STAR_PAL = {"o": "#16142b", "h": "#fff4c2", "g": "#f2c14e", "G": "#c98a1f"}

TOWER = [
    ".....oooooo.....",
    ".....orrrrdo....",
    ".....ohrrrdo....",
    ".....oooooooo...",
    "....oppppppqo...",
    "....ohppppppqo..",
    "....oooooooooo..",
    "...obbbbbbbbbdo.",
    "...ohbbbbbbbbdo.",
    "...oooooooooooo.",
    "..oggggggggggGGo",
    "..ohggggggggggGo",
    "..oooooooooooooo",
    ".ovvvvvvvvvvvvVo",
    ".ohvvvvvvvvvvvVo",
    ".oooooooooooooo.",
]
TOWER_PAL = {"o": "#16142b", "r": "#ff2d20", "d": "#b3170e", "h": "#ffffff",
             "p": "#8f94d6", "q": "#5b5f9c", "b": "#4fc3f7", "g": "#5bd69b",
             "G": "#2f9e6a", "v": "#f2c14e", "V": "#c98a1f"}

FLAG = [
    ".oo.............",
    "ohgo............",
    "ogGoooooooooo...",
    ".ohorrrrrrrrrro.",
    ".owohrrrrrrrrrro",
    ".owohrrrrrrrrdo.",
    ".owohrrrrrrrdo..",
    ".owohrrrrrrrrdo.",
    ".owohrrrrrrrrrdo",
    ".owoooooooooooo.",
    ".owo............",
    ".owo............",
    ".owo............",
    ".oWo............",
    "oggGo...........",
    "ooooo...........",
]
FLAG_PAL = {"o": "#16142b", "h": "#ffb3ad", "g": "#f2c14e", "G": "#c98a1f",
            "r": "#ff2d20", "d": "#b3170e", "w": "#c98a4b", "W": "#8b5a2b"}

BRACES = auto_outline([
    "...pp.......pp...",
    "..pq.........qp..",
    "..p...........p..",
    "..p.....g.....p..",
    "..p....gwg....p..",
    ".p......g......p.",
    "p...............p",
    ".p.............p.",
    "..p...........p..",
    "..p...........p..",
    "..p...........p..",
    "..pq.........qp..",
    "...pp.......pp...",
], thick=True)
BRACES_PAL = {"o": "#16142b", "p": "#8f94d6", "q": "#5b5f9c", "g": "#f2c14e", "w": "#ffffff"}

# ------------------------------------------------------- contact icons 12px
GLOBE = [
    "....oooo....",
    "..oowwwwoo..",
    ".owwoowwwwo.",
    ".owowwowwwo.",
    "owwowwwowwwo",
    "ooooooooooo."[:12],
    "owwowwwowwwo",
    "owwowwwowwwo",
    ".owwowowwwo.",
    ".owwwoowwwo.",
    "..oowwwwoo..",
    "....oooo....",
]
INBOX = [
    "oooooooooooo",
    "owwwwwwwwwwo",
    "owoowwwwwwwo",
    "owoowwwwwwwo",
    "owwwwwwwwwwo",
    "owoowoooowwo",
    "owoowoowoowo",
    "owoowowwwowo",
    "owoowowwwowo",
    "owoowowwwowo",
    "owwwwwwwwwwo",
    "oooooooooooo",
]
MAIL = [
    "............",
    "............",
    "oooooooooooo",
    "oowwwwwwwwoo",
    "owowwwwwwowo",
    "owwowwwwowwo",
    "owwwoooowwwo",
    "owwowwwwowwo",
    "owowwwwwwowo",
    "oowwwwwwwwoo",
    "oooooooooooo",
    "............",
]
CAL = [
    "..o.....o...",
    "oowoooooowoo",
    "owwwwwwwwwwo",
    "oooooooooooo",
    "owwwwwwwwwwo",
    "owowowowowwo",
    "owwwwwwwwwwo",
    "owowowowowwo",
    "owwwwwwwwwwo",
    "owowowowwwwo",
    "owwwwwwwwwwo",
    "oooooooooooo",
]

# ----------------------------------------------------------------- scenery
ROCKET = [
    "...oo...",
    "..owwo..",
    ".owwwwo.",
    ".owbbwo.",
    ".owbbwo.",
    ".owwwwo.",
    ".owwwwo.",
    ".orwwro.",
    "orrwwrro",
    "orroorro",
    "oo....oo",
]
ROCKET_PAL = {"o": "#16142b", "w": "#e8eef5", "b": "#4fc3f7", "r": "#ff2d20"}
FLAME = [
    [".yyyy...", "..yy....", "...y...."],
    ["..yy....", ".yffy...", "..y....."],
]

MOON = [
    ".....oooo.....",
    "...oommmmoo...",
    "..ommmmmmmmo..",
    ".ommmcmmmmmmo.",
    ".ommcccmmmmmo.",
    "ommmmcmmmmmmmo",
    "ommmmmmmmcmmmo",
    "ommmmmmmmccmmo",
    "ommcmmmmmmmmmo",
    "ommmmmmmmmmmmo",
    ".ommmmmmmmmmo.",
    ".oommmmcmmmoo.",
    "..oommmmmmoo..",
    "....oooooo....",
]

CLOUD = [
    ".......wwww...........",
    ".....wwwwwwww.........",
    "....wwwwwwwwwww.www...",
    "..wwwwwwwwwwwwwwwwwww.",
    ".wwwwwwwwwwwwwwwwwwwww",
    "wwwwwwwwwwwwwwwwwwwwww",
    "ssssssssssssssssssssss",
]

BIRD = [
    ["o...o", ".o.o.", "..o.."],
    [".....", "ooooo", "..o.."],
]

PLANT = [
    "..g..g..",
    ".gG.gG..",
    "..gGgGg.",
    ".gGgGg..",
    "..gGGg..",
    ".oooooo.",
    ".occcco.",
    "..occo..",
    "..oooo..",
]
PLANT_PAL = {"g": "#5bd69b", "G": "#2f9e6a", "o": "#16142b", "c": "#c8663a"}

MUG = [
    ".s.s..",
    "..s.s.",
    "oooo..",
    "owwooo",
    "owwo.o",
    "owwooo",
    "oooo..",
]
MUG_PAL = {"o": "#16142b", "w": "#ff2d20", "s": "#cfd6e4"}
