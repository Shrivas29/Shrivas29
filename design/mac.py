"""The profile's top section as a classic Mac desktop: a 1-bit "About Shrivas" window that zooms open, a portrait that
draws in line by line, desktop icons for the work, and a pointer that double-clicks Gotham open.

Run: python design/mac.py   (writes assets/mac/*.svg and the linked tiles in README.md)
Needs the cut-out café photo at design/shots/cafe-cut-u2net.png and Departure Mono in design/fonts/.
"""

import base64
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np
from fontTools import subset
from fontTools.ttLib import TTFont
from PIL import Image, ImageFilter, ImageOps

from live import stats

HERE = Path(__file__).parent
OUT = HERE.parent / "assets"

W = 846
SH = 404  # the screen: menu bar and desktop
LH = 108  # the Launcher window under it
CW = 7  # Departure Mono advance at 11px
BLACK, WHITE, DESK, LIME = "#000", "#fff", "#c4c4c4", "#c8ff57"
T = 5.0  # one pass of the opening sequence, in seconds


# ---------------------------------------------------------------- pixel helpers


def bitmap(rows: list[str], x: int, y: int, scale: int = 1) -> str:
    """Pixel art from strings ('#' black, '.' white, anything else clear), merged into runs per row."""
    out = []
    for colour, mark in ((BLACK, "#"), (WHITE, ".")):
        d = []
        for j, row in enumerate(rows):
            i = 0
            while i < len(row):
                if row[i] == mark:
                    k = i
                    while k < len(row) and row[k] == mark:
                        k += 1
                    d.append(f"M{x + i * scale} {y + j * scale}h{(k - i) * scale}v{scale}h-{(k - i) * scale}z")
                    i = k
                else:
                    i += 1
        if d:
            out.append(f'<path fill="{colour}" d="{"".join(d)}"/>')
    return "".join(out)


def box(x, y, w, h, fill=WHITE, line=BLACK, t=1) -> str:
    """A crisp 1-pixel frame."""
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"/>'
        f'<path fill="{line}" d="M{x} {y}h{w}v{t}h-{w}zM{x} {y + h - t}h{w}v{t}h-{w}zM{x} {y}h{t}v{h}h-{t}zM{x + w - t} {y}h{t}v{h}h-{t}z"/>'
    )


def text(s: str, x: float, y: float, size: int = 11, fill: str = BLACK, anchor: str = "start", cls: str = "") -> str:
    c = f' class="{cls}"' if cls else ""
    return f'<text{c} x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" xml:space="preserve">{escape(s)}</text>'


def appear(at: float, dur: float = 0.01) -> str:
    """Hidden until `at`, then shown for good. Without SMIL the element simply shows."""
    k0, k1 = at / T, min(0.999, (at + dur) / T)
    # SMIL needs the key times to run from 0 to 1, or the browser drops the animation.
    return f'<animate attributeName="opacity" dur="{T}s" values="0;0;1;1" keyTimes="0;{k0:.4f};{k1:.4f};1" fill="freeze"/>'


# ---------------------------------------------------------------- icons and pointer

FOLDER = [
    "   ########                   ",
    "  #........#                  ",
    " #..........#                 ",
    "###############################",
    "#.............................#",
    "#.............................#",
    "#.............................#",
    "#.............................#",
    "#.............................#",
    "#.............................#",
    "#.............................#",
    "#.............................#",
    "#.............................#",
    "#.............................#",
    "#.............................#",
    "#.............................#",
    "#.............................#",
    "#.............................#",
    "#.............................#",
    "#.............................#",
    "###############################",
]

DOC = [
    "###############    ",
    "#.............##   ",
    "#.............#.#  ",
    "#.............#..# ",
    "#.............#####",
    "#.................#",
    "#..###########....#",
    "#.................#",
    "#..#########......#",
    "#.................#",
    "#..###########....#",
    "#.................#",
    "#..#######........#",
    "#.................#",
    "#..###########....#",
    "#.................#",
    "#..#########......#",
    "#.................#",
    "#.................#",
    "#.................#",
    "#.................#",
    "###################",
]

DISK = [
    "######################  ",
    "#....#..........#....##.",
    "#....#..........#.##.#.#",
    "#....#..........#.##.#..#",
    "#....#..........#....#..#",
    "#....############....#..#",
    "#.......................#",
    "#.......................#",
    "#..####################.#",
    "#..#..................#.#",
    "#..#..................#.#",
    "#..#..................#.#",
    "#..#..................#.#",
    "#..#..................#.#",
    "#..#..................#.#",
    "#..####################.#",
    "#.......................#",
    "#########################",
]

TRASH = [
    "      ######      ",
    "      #....#      ",
    "##################",
    "#................#",
    "##################",
    " #..............# ",
    " #..#..#..#..#..# ",
    " #..#..#..#..#..# ",
    " #..#..#..#..#..# ",
    " #..#..#..#..#..# ",
    " #..#..#..#..#..# ",
    " #..#..#..#..#..# ",
    " #..#..#..#..#..# ",
    " #..#..#..#..#..# ",
    " #..#..#..#..#..# ",
    " #..............# ",
    " ################ ",
]

ARROW = [
    "#           ",
    "##          ",
    "#.#         ",
    "#..#        ",
    "#...#       ",
    "#....#      ",
    "#.....#     ",
    "#......#    ",
    "#.......#   ",
    "#........#  ",
    "#.....##### ",
    "#..#..#     ",
    "#.# #..#    ",
    "##  #..#    ",
    "#    #..#   ",
    "     #..#   ",
    "      ##    ",
]


REPO = "https://github.com/Shrivas29/"
ICONS = [
    ("Gotham", FOLDER, REPO + "GOTHAM"),
    ("Daily Bugle", FOLDER, REPO + "spiderverse"),
    ("ENTØ Studios", DISK, REPO + "ENTO"),
    ("Vidyuth Nº12", DOC, REPO + "VIDYUTH-PORTFOLIO-"),
    ("Shrivas PS", DOC, REPO + "SHRIVAS---CONSOLE-"),
    ("Sujitha M", DOC, REPO + "SUJITHA-PORTFOLIO"),
    ("All repos", FOLDER, "https://github.com/Shrivas29?tab=repositories"),
]


def invert(rows: list[str]) -> list[str]:
    return ["".join("." if c == "#" else "#" if c == "." else c for c in r) for r in rows]


# ---------------------------------------------------------------- the portrait


def portrait(w: int, h: int) -> str:
    """The café photo, cut out, Atkinson-dithered to one bit at its display size, as a data URI."""
    cut = Image.open(HERE / "shots" / "cafe-cut-u2net.png").convert("RGBA").crop((380, 70, 1100, 900))
    base = Image.new("RGBA", cut.size, (255, 255, 255, 255))
    base.alpha_composite(cut)
    g = ImageOps.grayscale(base.convert("RGB")).resize((w, h), Image.LANCZOS)
    mask = cut.getchannel("A").resize((w, h)).point(lambda a: 255 if a > 128 else 0)
    g = ImageOps.autocontrast(g, cutoff=1, mask=mask)
    g = g.point(lambda v: round(255 * (v / 255) ** 0.62)).filter(ImageFilter.UnsharpMask(2, 140, 2))
    a = np.asarray(g, dtype=np.float32) / 255.0
    for y in range(h):
        for x in range(w):
            old = a[y, x]
            new = 1.0 if old > 0.5 else 0.0
            a[y, x] = new
            e = (old - new) / 8
            for dx, dy in ((1, 0), (2, 0), (-1, 1), (0, 1), (1, 1), (0, 2)):
                if 0 <= x + dx < w and y + dy < h:
                    a[y + dy, x + dx] += e
    im = Image.fromarray((a * 255).clip(0, 255).astype(np.uint8)).convert("1")
    buf = BytesIO()
    im.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


# ---------------------------------------------------------------- windows


def window(x, y, w, h, title, content, at, zoom_from, wid) -> str:
    """A System 7 window that opens with zoom rectangles from `zoom_from`, then holds."""
    fx, fy, fw, fh = zoom_from
    rects = ""
    steps = 7
    for i in range(1, steps + 1):
        k = i / steps
        rx, ry = fx + (x - fx) * k, fy + (y - fy) * k
        rw, rh = fw + (w - fw) * k, fh + (h - fh) * k
        t0 = at - 0.36 + i * 0.045
        k0, k1, k2 = max(0, t0) / T, max(0, t0 + 0.01) / T, min(1, (t0 + 0.09) / T)
        rects += (
            f'<rect x="{rx:.0f}.5" y="{ry:.0f}.5" width="{rw:.0f}" height="{rh:.0f}" fill="none" stroke="{BLACK}" stroke-dasharray="2 2" opacity="0">'
            f'<animate attributeName="opacity" dur="{T}s" values="0;0;1;0;0" keyTimes="0;{k0:.4f};{k1:.4f};{k2:.4f};1" fill="freeze"/></rect>'
        )
    bar = 19
    stripes = "".join(f'<rect x="{x + 2}" y="{y + 4 + i * 2}" width="{w - 4}" height="1" fill="{BLACK}"/>' for i in range(6))
    tw = len(title) * CW + 16
    chrome = (
        box(x, y, w, h)
        + f'<rect x="{x + 1}" y="{y + bar}" width="{w - 2}" height="1" fill="{BLACK}"/>'
        + stripes
        + f'<rect x="{x + w / 2 - tw / 2:.0f}" y="{y + 2}" width="{tw}" height="{bar - 3}" fill="{WHITE}"/>'
        + text(title, x + w / 2, y + 14, 11, anchor="middle")
        + f'<rect x="{x + 8}" y="{y + 3}" width="13" height="13" fill="{WHITE}"/>' + box(x + 9, y + 4, 11, 11)
        + f'<rect x="{x + w - 21}" y="{y + 3}" width="13" height="13" fill="{WHITE}"/>' + box(x + w - 20, y + 4, 11, 11) + box(x + w - 20, y + 4, 7, 7)
        + f'<rect x="{x + 2}" y="{y + h}" width="{w}" height="2" fill="{BLACK}"/><rect x="{x + w}" y="{y + 2}" width="2" height="{h}" fill="{BLACK}"/>'
    )
    return f'{rects}<g id="{wid}" opacity="1">{appear(at)}{chrome}{content}</g>'


def button(x, y, w, label, default=False) -> str:
    out = (
        f'<rect x="{x}" y="{y}" width="{w}" height="20" rx="5" fill="{WHITE}" stroke="{BLACK}" stroke-width="1"/>'
        + text(label, x + w / 2, y + 14, 11, anchor="middle")
    )
    if default:
        out = f'<rect x="{x - 4}" y="{y - 4}" width="{w + 8}" height="28" rx="8" fill="{WHITE}" stroke="{BLACK}" stroke-width="3"/>' + out
    return out


# ---------------------------------------------------------------- the desktop


def drawing(css_text: str, defs: list[str], body: list[str]) -> str:
    return f"<style>{css_text}</style><defs>{''.join(defs)}</defs>{''.join(body)}"


CSS = 'text{font-family:"DM",ui-monospace,monospace}rect,path{shape-rendering:crispEdges}'
DESK_PATTERN = f'<pattern id="desk" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="4" fill="{DESK}"/><rect width="1" height="1" fill="#9c9c9c"/><rect x="2" y="2" width="1" height="1" fill="#9c9c9c"/></pattern>'
ALERT = (586, 196, 244, 126)  # x, y, w, h


def build_screen(s: dict, font: str) -> str:
    """Menu bar and desktop: the About window, the hard disk, the Gotham alert and the Trash."""
    body, defs = [], [DESK_PATTERN]
    body.append(f'<rect width="{W}" height="{SH}" fill="url(#desk)"/>')
    body.append(f'<rect width="{W}" height="20" fill="{WHITE}"/><rect y="20" width="{W}" height="1" fill="{BLACK}"/>')
    body.append(box(12, 3, 15, 15, LIME) + text("Ø", 16, 15, 11))
    mx = 44
    for m in MENUS:
        body.append(text(m, mx, 15))
        mx += len(m) * CW + 21
    body.append(text("Shrivas VM", W - 14, 15, anchor="end"))
    body.append(text("Dundee  56.46° N", W - 14 - 11 * CW - 24, 15, fill="#555", anchor="end"))

    # About window.
    ax, ay, aw, ah = 20, 36, 552, 356
    px, py, pw, ph = ax + 18, ay + 34, 232, 268
    defs.append(
        f'<clipPath id="draw"><rect x="{px}" y="{py}" width="{pw}" height="{ph}">'
        f'<animate attributeName="height" dur="{T}s" values="0;0;{ph};{ph}" keyTimes="0;{0.5 / T:.4f};{1.9 / T:.4f};1" fill="freeze"/></rect></clipPath>'
    )
    tx = px + pw + 24
    rows = about_rows(s)
    about = (
        box(px - 1, py - 1, pw + 2, ph + 2)
        + f'<image clip-path="url(#draw)" href="{portrait(pw, ph)}" x="{px}" y="{py}" width="{pw}" height="{ph}" image-rendering="optimizeSpeed" style="image-rendering:pixelated"/>'
        + f'<g opacity="1">{appear(0.7)}' + text("Shrivas VM", tx, py + 18, 22) + "</g>"
        + f'<g opacity="1">{appear(0.85)}' + text("Founder & creative director,", tx, py + 42) + text("ENTØ Studios.", tx, py + 56) + "</g>"
        + f'<g opacity="1">{appear(0.95)}<rect x="{tx}" y="{py + 68}" width="{ax + aw - 18 - tx}" height="1" fill="{BLACK}"/></g>'
    )
    for i, (k, v) in enumerate(rows):
        ry = py + 90 + i * 17
        about += f'<g opacity="1">{appear(1.0 + i * 0.08)}' + text(k, tx, ry, fill="#555") + text(v, tx + 56, ry) + "</g>"
    about += f'<g opacity="1">{appear(1.75)}' + button(tx + 2, py + ph - 22, 112, "Open Gotham", True) + button(tx + 136, py + ph - 22, 96, "Portfolio") + "</g>"
    body.append(window(ax, ay, aw, ah, "About Shrivas", about, 0.35, (12, 3, 15, 15), "about"))

    # The hard disk at the top right and the Trash at the bottom right, as on any Mac.
    ix = 790
    for label, art, y0 in (("Shrivas HD", DISK, 34), ("Trash", TRASH, SH - 66)):
        w_art = max(len(r) for r in art)
        lw = len(label) * CW + 6
        body.append(bitmap(art, ix - w_art // 2, y0 + (22 - len(art))) + f'<rect x="{ix - lw / 2:.0f}" y="{y0 + 29}" width="{lw}" height="14" fill="{WHITE}"/>' + text(label, ix, y0 + 40, anchor="middle"))

    # The alert the Launcher's Gotham button opens; it zooms up from the bottom edge, where the button sits.
    lx, ly, lw_, lh = ALERT
    alert = (
        f'<circle cx="{lx + 30}" cy="{ly + 52}" r="15" fill="{LIME}" stroke="{BLACK}" stroke-width="2"/>'
        + text("!", lx + 30, ly + 60, 22, anchor="middle")
        + text("Gotham is live.", lx + 56, ly + 38)
        + text("A Batman fan site", lx + 56, ly + 53)
        + text("you scroll into.", lx + 56, ly + 67)
        + text("gotham-ashen.vercel.app", lx + 56, ly + 85, fill="#555")
        + button(lx + lw_ - 70, ly + lh - 32, 54, "OK", True)
    )
    body.append(window(lx, ly, lw_, lh, "Gotham", alert, 3.25, (30, SH - 6, 100, 6), "alert"))
    return drawing(font + CSS, defs, body)


def build_launcher(font: str) -> str:
    """The Launcher: one window of big buttons, one per project. Each button becomes its own linked tile."""
    body, defs = [], [DESK_PATTERN]
    body.append(f'<rect width="{W}" height="{LH}" fill="url(#desk)"/>')
    x, y, w, h = 8, 4, W - 18, LH - 10
    bar = 19
    stripes = "".join(f'<rect x="{x + 2}" y="{y + 4 + i * 2}" width="{w - 4}" height="1" fill="{BLACK}"/>' for i in range(6))
    title = "Launcher"
    tw = len(title) * CW + 16
    body.append(
        box(x, y, w, h)
        + f'<rect x="{x + 1}" y="{y + bar}" width="{w - 2}" height="1" fill="{BLACK}"/>' + stripes
        + f'<rect x="{x + w / 2 - tw / 2:.0f}" y="{y + 2}" width="{tw}" height="{bar - 3}" fill="{WHITE}"/>' + text(title, x + w / 2, y + 14, anchor="middle")
        + f'<rect x="{x + 8}" y="{y + 3}" width="13" height="13" fill="{WHITE}"/>' + box(x + 9, y + 4, 11, 11)
        + f'<rect x="{x + 2}" y="{y + h}" width="{w}" height="2" fill="{BLACK}"/><rect x="{x + w}" y="{y + 2}" width="2" height="{h}" fill="{BLACK}"/>'
    )
    for i, (label, art, _) in enumerate(ICONS):
        cx = TILE_X[i] + TILE_W[i] / 2
        # Centred in its tile, but kept clear of the window's edges.
        bw, bh = 96, 62
        bx, by = round(min(max(cx - bw / 2, x + 10), x + w - 10 - bw)), y + bar + 8
        cx = bx + bw / 2
        w_art = max(len(r) for r in art)
        gx, gy = round(cx - w_art / 2), by + 8 + (22 - len(art))
        normal = box(bx, by, bw, bh) + bitmap(art, gx, gy) + text(label, cx, by + 52, anchor="middle")
        if label == "Gotham":
            flash = "0;0;1;0;1;1"
            k = [0, 2.7 / T, 2.71 / T, 2.82 / T, 2.86 / T, 1]
            pressed = box(bx, by, bw, bh, BLACK) + bitmap(invert(art), gx, gy) + text(label, cx, by + 52, 11, WHITE, "middle")
            body.append(normal + f'<g opacity="0"><animate attributeName="opacity" dur="{T}s" values="{flash}" keyTimes="{";".join(f"{v:.4f}" for v in k)}" fill="freeze"/>{pressed}</g>')
            start, end = (round(cx + 30), by + bh - 4), (round(cx + 4), by + 24)
            body.append(
                f'<g transform="translate({end[0]} {end[1]})"><animateTransform attributeName="transform" type="translate" dur="{T}s" values="{start[0]} {start[1]};{start[0]} {start[1]};{end[0]} {end[1]};{end[0]} {end[1]}" keyTimes="0;{2.1 / T:.4f};{2.6 / T:.4f};1" calcMode="spline" keySplines="0 0 1 1;.45 0 .25 1;0 0 1 1" fill="freeze"/>'
                + bitmap(ARROW, 0, 0) + "</g>"
            )
        else:
            body.append(normal)
    return drawing(font + CSS, defs, body)


MENUS = ["File", "Edit", "View", "Special", "Label"]
TILE_W = [121, 121, 121, 121, 121, 121, 120]
TILE_X = [sum(TILE_W[:i]) for i in range(len(TILE_W))]
SPLIT = 580  # the screen splits here: the About side and the alert side
PORTFOLIO = "https://shrivas-console.vercel.app"
SCALE = 99.9  # percent of the README's width; a hair under 100 so rounding never wraps a row


def about_rows(s: dict) -> list[tuple[str, str]]:
    return [
        ("Kind", "Designer, developer, founder"),
        ("Studio", "ENTØ Studios"),
        ("Base", "Dundee, Scotland"),
        ("Stack", "Next.js · React · TypeScript"),
        ("Motion", "Framer Motion · GSAP · Lenis"),
        ("Built", f"{s['repos']} repos · {s['live']} live sites"),
        ("Bar", "Polished, fast, accessible,"),
        ("", "human."),
    ]


# ---------------------------------------------------------------- tiles
#
# GitHub shows each README image as one link and strips image maps, and its stylesheet pads floated images.
# Images on the same line do sit flush, though. So the screen is one row of two images and the Launcher is one
# row of buttons, each a window onto the same drawing so the seams line up.


def svg(viewbox: tuple, inner: str, alt: str) -> str:
    x, y, w, h = viewbox
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} {y} {w} {h}" width="{w}" height="{h}" role="img" aria-label="{escape(alt)}">'
        f"<title>{escape(alt)}</title>{inner}</svg>"
    )


def write_tiles():
    s = stats()
    used = "".join(MENUS) + "ØShrivas VMDundee  56.46° NAbout ShrivasFounder & creative director,ENTØ Studios.Open Gotham Portfolio OK! Launcher Shrivas HD Trash"
    used += "".join(k + v for k, v in about_rows(s)) + "".join(l for l, _, _ in ICONS) + "Gotham is live.A Batman fan siteyou scroll into.gotham-ashen.vercel.app0123456789·"
    font = embedded_font(used)
    screen, launcher = build_screen(s, font), build_launcher(font)
    folder = OUT / "mac"
    folder.mkdir(exist_ok=True)
    for old in folder.glob("*.svg"):
        old.unlink()

    tiles = [
        ("screen-about", (0, 0, SPLIT, SH), screen, PORTFOLIO, "About Shrivas: Shrivas VM, founder and creative director of ENTØ Studios, Dundee, Scotland, with a 1-bit portrait. Opens his portfolio."),
        ("screen-gotham", (SPLIT, 0, W - SPLIT, SH), screen, "https://gotham-ashen.vercel.app", "Alert: Gotham is live, a Batman fan site you scroll into. Opens Gotham."),
    ]
    for i, (label, _, href) in enumerate(ICONS):
        slug = label.lower().replace(" ", "-").replace("ø", "o").replace("º", "")
        alt = f"Launcher button: {label}. Opens the repo." if label != "All repos" else "Launcher button: All repos. Opens every repository."
        tiles.append((f"launcher-{slug}", (TILE_X[i], 0, TILE_W[i], LH), launcher, href, alt))

    row1, row2 = [], []
    for name, vb, inner, href, alt in tiles:
        (folder / f"{name}.svg").write_text(svg(vb, inner, alt))
        tag = f'<a href="{href}"><img width="{vb[2] / W * SCALE:.3f}%" src="./assets/mac/{name}.svg" alt="{escape(alt)}"></a>'
        (row1 if name.startswith("screen") else row2).append(tag)
    block = "<p>" + "".join(row1) + "<br>" + "".join(row2) + "</p>"
    readme = OUT.parent / "README.md"
    text_ = readme.read_text()
    a, b = text_.index("<!-- mac:start -->"), text_.index("<!-- mac:end -->")
    readme.write_text(text_[: a + len("<!-- mac:start -->")] + "\n" + block + "\n" + text_[b:])
    total = sum(f.stat().st_size for f in folder.glob("*.svg"))
    print(f"{len(tiles)} tiles, {total / 1024:.0f} KB, README block updated")


def embedded_font(chars: str) -> str:
    font = TTFont(HERE / "fonts" / "DepartureMono-Regular.woff2")
    sub = subset.Subsetter(subset.Options(flavor="woff2", name_IDs=["*"]))
    sub.populate(text=chars)
    sub.subset(font)
    buf = BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    return f'@font-face{{font-family:"DM";src:url(data:font/woff2;base64,{base64.b64encode(buf.getvalue()).decode()}) format("woff2")}}'


if __name__ == "__main__":
    write_tiles()
