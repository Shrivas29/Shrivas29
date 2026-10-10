"""The profile's top section as a classic Mac desktop: a 1-bit "About Shrivas" window that zooms open, a portrait that
draws in line by line, desktop icons for the work, and a pointer that double-clicks Gotham open.

Run: python design/mac.py   (writes assets/top.svg)
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

W, H = 846, 502
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


def build() -> str:
    s = stats()
    body, defs = [], []

    # Desktop and menu bar.
    defs.append(f'<pattern id="desk" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="4" fill="{DESK}"/><rect width="1" height="1" fill="#9c9c9c"/><rect x="2" y="2" width="1" height="1" fill="#9c9c9c"/></pattern>')
    body.append(f'<rect width="{W}" height="{H}" fill="url(#desk)"/>')
    body.append(f'<rect width="{W}" height="20" fill="{WHITE}"/><rect y="20" width="{W}" height="1" fill="{BLACK}"/>')
    body.append(f'<rect x="12" y="3" width="15" height="15" fill="{LIME}"/>' + box(12, 3, 15, 15, LIME) + text("Ø", 16, 15, 11))
    menus = ["File", "Edit", "View", "Special", "Label"]
    mx = 44
    for m in menus:
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
    rows = [
        ("Kind", "Designer, developer, founder"),
        ("Studio", "ENTØ Studios"),
        ("Base", "Dundee, Scotland"),
        ("Stack", "Next.js · React · TypeScript"),
        ("Motion", "Framer Motion · GSAP · Lenis"),
        ("Built", f"{s['repos']} repos · {s['live']} live sites"),
        ("Bar", "Polished, fast, accessible,"),
        ("", "human."),
    ]
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

    # Desktop icons along the right edge.
    icons = [("Gotham", FOLDER), ("Daily Bugle", FOLDER), ("ENTØ Studios", DISK), ("Vidyuth Nº12", DOC), ("Shrivas PS", DOC), ("Sujitha M", DOC), ("Trash", TRASH)]
    ix, iy0, step = 784, 34, 64
    gotham_box = None
    for i, (label, art) in enumerate(icons):
        iy = iy0 + i * step
        w_art = max(len(r) for r in art)
        gx = ix - w_art // 2
        lw = len(label) * CW + 6
        normal = bitmap(art, gx, iy) + f'<rect x="{ix - lw / 2:.0f}" y="{iy + 26}" width="{lw}" height="14" fill="{WHITE}"/>' + text(label, ix, iy + 37, anchor="middle")
        if label == "Gotham":
            gotham_box = (gx, iy, w_art, 40)
            flash = ";".join(["0", "0", "1", "0", "1", "1"])
            k = [0, 2.7 / T, 2.71 / T, 2.82 / T, 2.86 / T, 1]
            selected = bitmap(invert(art), gx, iy) + f'<rect x="{ix - lw / 2:.0f}" y="{iy + 26}" width="{lw}" height="14" fill="{BLACK}"/>' + text(label, ix, iy + 37, 11, WHITE, "middle")
            body.append(normal + f'<g opacity="0"><animate attributeName="opacity" dur="{T}s" values="{flash}" keyTimes="{";".join(f"{v:.4f}" for v in k)}" fill="freeze"/>{selected}</g>')
        else:
            body.append(normal)

    # The alert Gotham opens.
    lx, ly, lw_, lh = 436, 348, 290, 140
    alert = (
        f'<circle cx="{lx + 34}" cy="{ly + 52}" r="16" fill="{LIME}" stroke="{BLACK}" stroke-width="2"/>'
        + text("!", lx + 34, ly + 60, 22, anchor="middle")
        + text("Gotham is live.", lx + 62, ly + 42)
        + text("A Batman fan site you", lx + 62, ly + 58)
        + text("scroll into.", lx + 62, ly + 72)
        + text("gotham-ashen.vercel.app", lx + 62, ly + 92, fill="#555")
        + button(lx + lw_ - 70, ly + lh - 30, 54, "OK", True)
    )
    body.append(window(lx, ly, lw_, lh, "Gotham", alert, 3.25, gotham_box, "alert"))

    # The pointer: across the desktop, a double-click on Gotham, then over to OK.
    path = [(600, 470), (640, 300), (ix - 4, iy0 + 14), (ix - 4, iy0 + 14), (lx + lw_ - 44, ly + lh - 18)]
    times = [0, 1.9, 2.6, 3.45, 4.1]
    vals = ";".join(f"{x} {y}" for x, y in path)
    kt = ";".join(f"{t / T:.4f}" for t in times[:-1]) + f";{times[-1] / T:.4f}"
    body.append(
        f'<g transform="translate({path[-1][0]} {path[-1][1]})"><animateTransform attributeName="transform" type="translate" dur="{T}s" values="{vals};{path[-1][0]} {path[-1][1]}" keyTimes="{kt};1" calcMode="spline" keySplines="{";".join([".45 0 .25 1"] * len(path))}" fill="freeze"/>'
        + bitmap(ARROW, 0, 0) + "</g>"
    )

    used = "".join(menus) + "ØShrivas VMDundee  56.46° NAbout ShrivasFounder & creative director,ENTØ Studios.OpenGotham Portfolio OK!" + "".join(k + v for k, v in rows) + "".join(l for l, _ in icons) + "Gotham is live.A Batman fan site youscroll into.gotham-ashen.vercel.app0123456789·"
    css = embedded_font(used) + 'text{font-family:"DM",ui-monospace,monospace}rect,path{shape-rendering:crispEdges}'
    title = "A classic Mac desktop. An About Shrivas window: Shrivas VM, founder and creative director of ENTØ Studios, Dundee, Scotland, with a 1-bit portrait. Desktop icons for Gotham, The Daily Bugle, ENTØ Studios, Vidyuth Nº12, Shrivas PS and Sujitha M. An alert says Gotham is live."
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{escape(title)}">'
        f"<title>{escape(title)}</title><style>{css}</style><defs>{''.join(defs)}</defs>{''.join(body)}</svg>"
    )


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
    svg = build()
    (OUT / "top.svg").write_text(svg)
    print(f"top.svg {len(svg) / 1024:.0f} KB")
