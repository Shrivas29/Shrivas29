"""The profile's top section: a portrait typeset from my own words, full-bleed on the right, with the name,
a spec sheet, live numbers and a prompt on the left. Dark in both GitHub themes, like a framed poster.

Run: python design/top.py   (needs design/shots/wordportrait-dark.png from wordportrait.py; writes assets/top.svg)
"""

import base64
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image

from live import embedded_font, stats
from typeset import letters, text_d, width

HERE = Path(__file__).parent
OUT = HERE.parent / "assets"

W, H = 1000, 640
X = 40
PX = 430  # where the portrait starts
BG, INK, MUTED, LINE, LIME = "#060606", "#f0ede8", "#8a8781", "#262626", "#c8ff57"
EASE = "cubic-bezier(.16,1,.3,1)"
MONO_CW = 0.612  # Space Mono advance in em


def portrait_uri() -> str:
    im = Image.open(HERE / "shots" / "wordportrait-dark.png").convert("RGB")
    buf = BytesIO()
    im.save(buf, "JPEG", quality=88, optimize=True, progressive=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def mono(text, x, y, size=13, cls="v", anchor="start", spacing=0.0, extra=""):
    ls = f' letter-spacing="{spacing}em"' if spacing else ""
    return f'<text class="{cls}" x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}"{ls} xml:space="preserve"{extra}>{escape(text)}</text>'


SPEC = [
    ("ROLE", "Designer · developer · founder"),
    ("STUDIO", "ENTØ Studios, creative intelligence"),
    ("BASE", "Dundee, Scotland"),
    ("STACK", "Next.js · React · TypeScript"),
    ("MOTION", "Framer Motion · GSAP · Lenis"),
    ("WORK", "Gotham · The Daily Bugle · Vidyuth Nº12"),
]


def build() -> str:
    s = stats()
    body = [f'<rect width="{W}" height="{H}" fill="{BG}"/>']
    defs = []

    # The portrait, drawn in by a scan line running down it.
    defs.append(
        f'<clipPath id="reveal"><rect x="{PX}" y="0" width="{W - PX}" height="{H}">'
        f'<animate attributeName="height" dur="1.6s" values="0;{H}" calcMode="spline" keySplines=".45 0 .25 1" fill="freeze"/></rect></clipPath>'
        f'<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="{BG}"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></linearGradient>'
        f'<linearGradient id="floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG}" stop-opacity="0"/><stop offset="1" stop-color="{BG}"/></linearGradient>'
    )
    body.append(f'<image clip-path="url(#reveal)" href="{portrait_uri()}" x="{PX}" y="0" width="{W - PX}" height="{H}" preserveAspectRatio="xMidYMid slice"/>')
    body.append(f'<rect x="{PX}" y="0" width="110" height="{H}" fill="url(#fade)"/>')
    body.append(f'<rect x="{PX}" y="{H - 90}" width="{W - PX}" height="90" fill="url(#floor)"/>')
    body.append(
        f'<rect x="{PX}" y="0" width="{W - PX}" height="2" fill="{LIME}">'
        f'<animate attributeName="y" dur="1.6s" values="0;{H}" calcMode="spline" keySplines=".45 0 .25 1" fill="freeze"/>'
        f'<animate attributeName="opacity" dur="1.9s" values="1;1;0" keyTimes="0;.84;1" fill="freeze"/></rect>'
    )

    # Labels at the top and on the portrait.
    body.append(f'<g class="f" style="animation-delay:.1s">'
                + f'<rect x="{X}" y="37" width="9" height="9" fill="{LIME}"/>'
                + mono("ENTØ STUDIOS  /  FILE Nº 001", X + 18, 46, 11.5, "m", spacing=0.14)
                + mono("56.46° N  2.97° W", W - 40, 46, 11.5, "m", "end", 0.14)
                + "</g>")

    # The name, rising letter by letter; VM in lime.
    size = 560 / width("Syne-800", "SHRIVAS", 100, -0.01) * 100
    base1, base2 = 146, 146 + size * 0.86
    defs.append(f'<clipPath id="stage"><rect x="0" y="70" width="{W}" height="{base2 - 70 + 8}"/></clipPath>')
    glyphs = [(d, INK) for _, d in letters("Syne-800", "SHRIVAS", size, X - 3, base1, -0.01)]
    glyphs += [(d, LIME) for _, d in letters("Syne-800", "VM", size, X - 3, base2, -0.01)]
    word = "".join(f'<path class="l" fill="{c}" style="animation-delay:{0.15 + i * 0.06:.2f}s" d="{d}"/>' for i, (d, c) in enumerate(glyphs))
    body.append(f'<g clip-path="url(#stage)">{word}</g>')

    # The line under the name.
    y = base2 + 46
    body.append(f'<g class="f" style="animation-delay:.75s"><path fill="{INK}" d="{text_d("SpaceGrotesk-500", "Founder & creative director, ENTØ Studios", 17.5, X, y, -0.005)}"/></g>')

    # Spec sheet.
    y += 34
    for i, (k, v) in enumerate(SPEC):
        row = f'<g class="f" style="animation-delay:{0.9 + i * 0.07:.2f}s">'
        row += f'<rect x="{X}" y="{y - 19}" width="{410}" height="1" fill="{LINE}"/>'
        row += mono(k, X, y, 10.5, "m", spacing=0.16)
        row += mono(v, X + 82, y, 13, "v")
        row += "</g>"
        body.append(row)
        y += 29
    body.append(f'<rect class="f" style="animation-delay:1.35s" x="{X}" y="{y - 19}" width="410" height="1" fill="{LINE}"/>')

    # Live numbers.
    y += 30
    nums = [(str(s["repos"]), "REPOS"), (str(s["live"]), "LIVE SITES"), (str(s["contributions"]), "CONTRIBUTIONS, 2026")]
    for i, (n, label) in enumerate(nums):
        x = X + i * 120
        body.append(
            f'<g class="f" style="animation-delay:{1.45 + i * 0.08:.2f}s"><path fill="{INK}" d="{text_d("Syne-800", n, 34, x, y, 0)}"/>'
            + mono(label, x, y + 20, 10, "m", spacing=0.14)
            + "</g>"
        )

    # The prompt, typed, with a live cursor.
    py = H - 32
    prompt, cmd = "shrivas@entø ~ $ ", "open gotham"
    cw = 13 * MONO_CW
    total = 4.2
    def typed(cid, x, chars, start, cps):
        w = chars * cw + 3
        k0, k1 = start / total, min(1, (start + chars / cps) / total)
        defs.append(f'<clipPath id="{cid}"><rect x="{x - 1}" y="{py - 14}" height="20" width="{w:.1f}"><animate attributeName="width" dur="{total}s" values="0;0;{w:.1f}" keyTimes="0;{k0:.4f};{k1:.4f}" fill="freeze"/></rect></clipPath>')
        return f"url(#{cid})"
    body.append(mono("shrivas@entø", X, py, 13, "k", extra=f' clip-path="{typed("pa", X, len(prompt), 1.8, 300)}"').replace("</text>", f'<tspan class="m"> ~ </tspan><tspan class="v">$ </tspan></text>'))
    body.append(mono(cmd, X + len(prompt) * cw, py, 13, "v", extra=f' clip-path="{typed("pb", X + len(prompt) * cw, len(cmd), 2.3, 12)}"'))
    body.append(f'<rect class="cursor" x="{X + (len(prompt) + len(cmd)) * cw + 2:.1f}" y="{py - 12}" width="{cw:.1f}" height="16" fill="{LIME}"/>')
    body.append(mono("TYPESET FROM MY OWN WORDS", W - 40, py, 10, "m", "end", 0.16))

    used = "".join(k + v for k, v in SPEC) + prompt + cmd + "ENTØ STUDIOS  /  FILE Nº 001 56.46° N  2.97° W TYPESET FROM MY OWN WORDS REPOS LIVE SITES CONTRIBUTIONS, 2026"
    css = (
        embedded_font(used)
        + f'text{{font-family:"SM",ui-monospace,monospace;fill:{INK}}}.m{{fill:{MUTED}}}.v{{fill:{INK}}}.k{{fill:{LIME};font-weight:700}}'
        f".l{{animation:rise 1.1s {EASE} both}}@keyframes rise{{from{{transform:translateY({size * 1.1:.0f}px)}}}}"
        ".f{animation:fade .8s ease both}@keyframes fade{from{opacity:0;transform:translateY(8px)}}"
        ".cursor{animation:blink 1.06s steps(1) infinite}@keyframes blink{50%{opacity:0}}"
        "@media (prefers-reduced-motion:reduce){.l,.f,.cursor{animation:none}}"
    )
    title = "Shrivas VM, founder and creative director of ENTØ Studios, based in Dundee, Scotland. A portrait typeset from his own words."
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{escape(title)}">'
        f"<title>{escape(title)}</title><style>{css}</style><defs>{''.join(defs)}</defs>{''.join(body)}</svg>"
    )


if __name__ == "__main__":
    svg = build()
    (OUT / "top.svg").write_text(svg)
    print(f"top.svg {len(svg) / 1024:.0f} KB")
