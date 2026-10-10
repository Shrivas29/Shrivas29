"""Build the profile's vector graphics (hero, section labels, principles, sign-off) in ENTØ's dark and light palettes.

Run: python design/build.py   (needs fonttools and uharfbuzz)
"""

from pathlib import Path

from fontTools.ttLib import TTFont

from typeset import FONTS, letters, text_d, width

OUT = Path(__file__).parent.parent / "assets"
W = 1600
M = 64

# ENTØ Studios' palette (entostudios.com). Lime is a fill, never text on the light ground.
PALETTES = {
    "dark": {"bg": "#060606", "ink": "#F0EDE8", "muted": "#8A8781", "line": "#2A2A2A", "lime": "#C8FF57", "edge": "#C8FF57"},
    "light": {"bg": "#F0EDE8", "ink": "#060606", "muted": "#67645F", "line": "#CFCAC1", "lime": "#C8FF57", "edge": "#060606"},
}

DISPLAY = "Syne-800"
DISPLAY_SEMI = "Syne-600"
LABEL = "SpaceGrotesk-600"
BODY = "SpaceGrotesk-500"

EASE = "cubic-bezier(.16,1,.3,1)"


def cap_height(name: str) -> float:
    tt = TTFont(FONTS / f"{name}.ttf")
    return tt["OS/2"].sCapHeight / tt["head"].unitsPerEm


def svg(h: int, body: str, css: str, title: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" role="img" aria-label="{title}">'
        f"<title>{title}</title><style>{css}"
        "@media (prefers-reduced-motion: reduce){*{animation:none!important}}</style>"
        f"{body}</svg>"
    )


def label(p, text, x, y, size=17, tracking=0.18, fill=None, anchor="start", font=LABEL):
    return f'<path fill="{fill or p["muted"]}" d="{text_d(font, text, size, x, y, tracking, anchor)}"/>'


# ---------------------------------------------------------------- hero


def hero(p) -> str:
    top = 78
    rule1 = 106
    name = "SHRIVAS VM"
    size = (W - 2 * M) / width(DISPLAY, name, 100, -0.01) * 100
    cap = cap_height(DISPLAY) * size
    cap_top = rule1 + 58
    base = cap_top + cap
    rule2 = base + 54
    info = rule2 + 54
    value = info + 42
    h = int(value + 108)
    foot = h - 46

    glyphs = letters(DISPLAY, name, size, M, base, -0.01)
    word = "".join(
        f'<path class="l" style="animation-delay:{0.08 + i * 0.06:.2f}s" d="{d}"/>' for i, (_, d) in enumerate(glyphs)
    )
    still = "".join(f'<path d="{d}"/>' for _, d in glyphs)
    band = cap * 0.55

    cols = [(M, "ROLE", "Founder & creative director"), (M + 520, "PRACTICE", "Design · Build · Motion"), (M + 1010, "STATUS", "Open to work")]
    row = ""
    for i, (x, k, v) in enumerate(cols):
        dx = 30 if k == "STATUS" else 0
        row += f'<g class="f" style="animation-delay:{1.25 + i * 0.1:.2f}s">'
        row += label(p, k, x, info, 16, 0.2)
        row += f'<path fill="{p["ink"]}" d="{text_d(BODY, v, 30, x + dx, value, -0.005)}"/>'
        if k == "STATUS":
            row += f'<circle class="dot" cx="{x + 9}" cy="{value - 10}" r="8.5" fill="{p["lime"]}" stroke="{p["edge"]}" stroke-width="2"/>'
        row += "</g>"

    css = (
        f".l{{animation:rise 1.1s {EASE} both}}"
        "@keyframes rise{from{transform:translateY(" + f"{cap * 1.25:.0f}" + "px)}}"
        f".r{{transform-box:fill-box;transform-origin:left;animation:draw 1.2s {EASE} both}}"
        "@keyframes draw{from{transform:scaleX(0)}}"
        ".f{animation:fade .9s ease both}@keyframes fade{from{opacity:0;transform:translateY(10px)}}"
        ".dot{animation:blink 1.8s ease-in-out 2s infinite}@keyframes blink{50%{opacity:.25}}"
    )
    body = (
        f'<rect width="{W}" height="{h}" fill="{p["bg"]}"/>'
        f'<g class="f" style="animation-delay:.1s">'
        + label(p, "ENTØ STUDIOS", M, top, 17, 0.2, p["ink"])
        + label(p, "/  CREATIVE INTELLIGENCE STUDIO", M + width(LABEL, "ENTØ STUDIOS", 17, 0.2) + 22, top, 17, 0.18)
        + label(p, "Nº 001  —  PROFILE, 2026", W - M, top, 17, 0.18, anchor="end")
        + "</g>"
        f'<rect class="r" x="{M}" y="{rule1}" width="{W - 2 * M}" height="2" fill="{p["line"]}"/>'
        f'<defs><clipPath id="stage"><rect x="0" y="{rule1 + 2}" width="{W}" height="{rule2 - rule1 - 2}"/></clipPath>'
        f'<clipPath id="juice"><rect x="0" y="{base + 40}" width="{W}" height="{band:.0f}">'
        f'<animate attributeName="y" from="{base + 40:.0f}" to="{cap_top - band - 40:.0f}" begin="1.05s" dur="1.1s" fill="freeze" calcMode="spline" keySplines=".45 0 .25 1" keyTimes="0;1"/>'
        "</rect></clipPath></defs>"
        f'<g clip-path="url(#stage)" fill="{p["ink"]}">{word}</g>'
        f'<g clip-path="url(#juice)" fill="{p["lime"]}">{still}</g>'
        f'<rect class="r" style="animation-delay:.35s" x="{M}" y="{rule2}" width="{W - 2 * M}" height="2" fill="{p["line"]}"/>'
        + row
        + f'<g class="f" style="animation-delay:1.6s">'
        + label(p, "DUNDEE, SCOTLAND  ·  56.46° N  2.97° W", M, foot, 15, 0.16)
        + label(p, "ENTOSTUDIOS.COM", W - M, foot, 15, 0.2, anchor="end")
        + "</g>"
    )
    return svg(h, body, css, "Shrivas VM. Founder and creative director, ENTØ Studios. Design, build, motion. Open to work.")


# ---------------------------------------------------------------- section labels


def section(p, index: str, title: str, note: str) -> str:
    h = 96
    y = 52
    body = (
        f'<rect width="{W}" height="{h}" fill="none"/>'
        f'<rect x="{M}" y="{y - 15}" width="14" height="14" fill="{p["lime"]}" stroke="{p["edge"]}" stroke-width="{0 if p["edge"] == p["lime"] else 1.5}"/>'
        + label(p, index, M + 34, y, 18, 0.2)
        + label(p, title, M + 34 + width(LABEL, index, 18, 0.2) + 26, y, 18, 0.22, p["ink"])
        + label(p, note, W - M, y, 16, 0.18, anchor="end")
        + f'<rect class="r" x="{M}" y="{y + 24}" width="{W - 2 * M}" height="2" fill="{p["line"]}"/>'
    )
    css = f".r{{transform-box:fill-box;transform-origin:left;animation:draw 1.2s {EASE} both}}@keyframes draw{{from{{transform:scaleX(0)}}}}"
    return svg(h, body, css, f"{index} {title}")


# ---------------------------------------------------------------- principles

PRINCIPLES = [
    ("01", ["A website is", "not a brochure."], ["It's a sales tool, a brand", "statement and a growth engine."]),
    ("02", ["Code and design", "are one craft."], ["The best sites feel effortless", "because someone cared about both."]),
    ("03", ["Polished, fast,", "accessible, human."], ["The bar for every build, from", "the first frame to the last line."]),
]


def principles(p) -> str:
    col = (W - 2 * M - 2 * 48) / 3
    size = min(col / width(DISPLAY_SEMI, line, 1) for _, lines, _ in PRINCIPLES for line in lines) * 0.98
    size = min(size, 46)
    h = 392
    body = f'<rect width="{W}" height="{h}" fill="{p["bg"]}"/>'
    for i, (num, lines, caption) in enumerate(PRINCIPLES):
        x = M + i * (col + 48)
        g = "<g>"
        g += f'<rect x="{x}" y="64" width="{col:.0f}" height="2" fill="{p["line"]}"/>'
        g += f'<rect x="{x}" y="62" width="44" height="6" fill="{p["lime"]}"/>'
        g += label(p, num, x, 112, 16, 0.2)
        for j, line in enumerate(lines):
            g += f'<path fill="{p["ink"]}" d="{text_d(DISPLAY_SEMI, line, size, x, 172 + j * size * 1.12, -0.01)}"/>'
        for j, line in enumerate(caption):
            g += f'<path fill="{p["muted"]}" d="{text_d(BODY, line, 21, x, 172 + 2 * size * 1.12 + 26 + j * 30, 0)}"/>'
        body += g + "</g>"
    return svg(h, body, "", "How I work. 01: A website is not a brochure. 02: Code and design are one craft. 03: Polished, fast, accessible, human.")


# ---------------------------------------------------------------- sign-off


def signoff(p) -> str:
    mark = "ENTØ"
    size = 900 / width(DISPLAY, mark, 100, 0.02) * 100
    cap = cap_height(DISPLAY) * size
    cap_top = 70
    base = cap_top + cap
    h = int(base + 150)
    x = (W - width(DISPLAY, mark, size, 0.02)) / 2
    glyphs = "".join(f'<path d="{d}"/>' for _, d in letters(DISPLAY, mark, size, x, base, 0.02))
    band = cap * 0.62
    low, high = base + 30, cap_top - band - 30
    body = (
        f'<rect width="{W}" height="{h}" fill="{p["bg"]}"/>'
        f'<defs><clipPath id="fill"><rect x="0" y="{low:.0f}" width="{W}" height="{band:.0f}">'
        f'<animate attributeName="y" values="{low:.0f};{low:.0f};{high:.0f};{high:.0f}" keyTimes="0;.45;.8;1" dur="7s" begin="0.6s" repeatCount="indefinite" calcMode="spline" keySplines="0 0 1 1;.45 0 .25 1;0 0 1 1"/>'
        "</rect></clipPath></defs>"
        f'<g fill="{p["ink"]}">{glyphs}</g>'
        f'<g clip-path="url(#fill)" fill="{p["lime"]}">{glyphs}</g>'
        + f'<path fill="{p["ink"]}" d="{text_d(BODY, "Websites that speak for themselves.", 30, W / 2, base + 72, -0.005, "middle")}"/>'
        + label(p, "© 2026 SHRIVAS VM  ·  ENTØ STUDIOS  ·  DUNDEE", W / 2, base + 118, 15, 0.2, anchor="middle")
    )
    return svg(h, body, "", "ENTØ Studios. Websites that speak for themselves.")


SECTIONS = {
    "work": ("01", "SELECTED WORK", "FOUR BUILDS, 2026"),
    "index": ("02", "INDEX", "EVERYTHING ON THIS PROFILE"),
    "practice": ("03", "HOW I WORK", "THE BAR"),
    "toolkit": ("04", "TOOLKIT", "WHAT I BUILD WITH"),
    "contact": ("05", "CONTACT", "SAY HELLO"),
}


def main():
    OUT.mkdir(exist_ok=True)
    for mode, p in PALETTES.items():
        (OUT / f"principles-{mode}.svg").write_text(principles(p))
        (OUT / f"signoff-{mode}.svg").write_text(signoff(p))
        for key, (i, t, n) in SECTIONS.items():
            (OUT / f"section-{key}-{mode}.svg").write_text(section(p, i, t, n))
    for f in sorted(OUT.glob("*.svg")):
        print(f"{f.name:32s} {f.stat().st_size / 1024:6.1f} KB")


if __name__ == "__main__":
    main()
