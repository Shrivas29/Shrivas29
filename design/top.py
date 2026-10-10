"""The profile's top section: a portrait typeset from my own words, full-bleed on the left and looking across at the
name, a spec sheet, live numbers and a prompt on the right, with the work running past on a ticker. Dark in both GitHub themes, like a framed poster.

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
PW = 600  # the portrait's width, from the left edge
X = 520  # the text column
BG, INK, MUTED, LINE, LIME = "#060606", "#f0ede8", "#8a8781", "#262626", "#c8ff57"
EASE = "cubic-bezier(.16,1,.3,1)"
MONO_CW = 0.612  # Space Mono advance in em
TICKER = "01 GOTHAM  ↗ gotham-ashen.vercel.app   ·   02 THE DAILY BUGLE   ·   03 ENTØ STUDIOS   ·   04 VIDYUTH Nº12   ·   05 SHRIVAS PS   ·   06 SUJITHA M   ·   "


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

    # The portrait on the left, looking across at the name; drawn in by a scan line.
    defs.append(
        f'<clipPath id="reveal"><rect x="0" y="0" width="{PW}" height="{H}">'
        f'<animate attributeName="height" dur="1.6s" values="0;{H}" calcMode="spline" keySplines=".45 0 .25 1" fill="freeze"/></rect></clipPath>'
        f'<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="{BG}" stop-opacity="0"/><stop offset="1" stop-color="{BG}"/></linearGradient>'
        f'<linearGradient id="floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG}" stop-opacity="0"/><stop offset="1" stop-color="{BG}"/></linearGradient>'
        f'<clipPath id="frame"><rect width="{W}" height="{H}"/></clipPath>'
    )
    body.append(f'<image clip-path="url(#reveal)" href="{portrait_uri()}" x="0" y="0" width="{PW}" height="{H}" preserveAspectRatio="xMidYMid slice"/>')
    body.append(f'<rect x="{PW - 130}" y="0" width="130" height="{H}" fill="url(#fade)"/>')
    body.append(f'<rect x="0" y="{H - 190}" width="{PW}" height="190" fill="url(#floor)"/>')
    body.append(
        f'<rect x="0" y="0" width="{PW}" height="2" fill="{LIME}">'
        f'<animate attributeName="y" dur="1.6s" values="0;{H}" calcMode="spline" keySplines=".45 0 .25 1" fill="freeze"/>'
        f'<animate attributeName="opacity" dur="1.9s" values="1;1;0" keyTimes="0;.84;1" fill="freeze"/></rect>'
    )

    # Labels: where the photo was taken, and the file.
    body.append(f'<g class="f" style="animation-delay:.1s">'
                + f'<rect x="{X}" y="37" width="9" height="9" fill="{LIME}"/>'
                + mono("ENTØ STUDIOS  /  FILE Nº 001", X + 18, 46, 11, "m", spacing=0.14)
                + mono("56.46° N  2.97° W", W - 40, 46, 11, "m", "end", 0.14)
                + "</g>")

    # The name, rising letter by letter; VM in lime.
    nx = X - 40
    size = (W - 40 - nx) / width("Syne-800", "SHRIVAS", 100, -0.01) * 100
    base1 = 84 + size * 0.7
    base2 = base1 + size * 0.88
    defs.append(f'<clipPath id="stage"><rect x="0" y="66" width="{W}" height="{base2 - 66 + 10}"/></clipPath>')
    glyphs = [(d, INK) for _, d in letters("Syne-800", "SHRIVAS", size, nx - 2, base1, -0.01)]
    glyphs += [(d, LIME) for _, d in letters("Syne-800", "VM", size, nx - 2, base2, -0.01)]
    word = "".join(f'<path class="l" fill="{c}" style="animation-delay:{0.15 + i * 0.06:.2f}s" d="{d}"/>' for i, (d, c) in enumerate(glyphs))
    body.append(f'<g clip-path="url(#stage)">{word}</g>')

    # The line under the name.
    y = base2 + 44
    body.append(f'<g class="f" style="animation-delay:.75s"><path fill="{INK}" d="{text_d("SpaceGrotesk-500", "Founder & creative director, ENTØ Studios", 17, X, y, -0.005)}"/></g>')

    # Spec sheet.
    y += 34
    for i, (k, v) in enumerate(SPEC):
        row = f'<g class="f" style="animation-delay:{0.9 + i * 0.07:.2f}s">'
        row += f'<rect x="{X}" y="{y - 19}" width="{W - 40 - X}" height="1" fill="{LINE}"/>'
        row += mono(k, X, y, 10, "m", spacing=0.16)
        row += mono(v, X + 80, y, 12.5, "v")
        row += "</g>"
        body.append(row)
        y += 28
    body.append(f'<rect class="f" style="animation-delay:1.35s" x="{X}" y="{y - 19}" width="{W - 40 - X}" height="1" fill="{LINE}"/>')

    # Live numbers.
    y += 34
    nums = [(str(s["repos"]), "REPOS"), (str(s["live"]), "LIVE SITES"), (str(s["contributions"]), "CONTRIBUTIONS, 2026")]
    for i, (n, label) in enumerate(nums):
        x = X + i * 140
        body.append(
            f'<g class="f" style="animation-delay:{1.45 + i * 0.08:.2f}s"><path fill="{INK}" d="{text_d("Syne-800", n, 32, x, y, 0)}"/>'
            + mono(label, x, y + 19, 9.5, "m", spacing=0.14)
            + "</g>"
        )

    # The prompt, typed, with a live cursor.
    py = H - 64
    prompt, cmd = "shrivas@entø ~ $ ", "open gotham"
    cw = 13 * MONO_CW
    total = 4.2

    def typed(cid, x, chars, start, cps):
        w = chars * cw + 3
        k0, k1 = start / total, min(1, (start + chars / cps) / total)
        defs.append(f'<clipPath id="{cid}"><rect x="{x - 1}" y="{py - 14}" height="20" width="{w:.1f}"><animate attributeName="width" dur="{total}s" values="0;0;{w:.1f}" keyTimes="0;{k0:.4f};{k1:.4f}" fill="freeze"/></rect></clipPath>')
        return f"url(#{cid})"

    body.append(mono("shrivas@entø", X, py, 13, "k", extra=f' clip-path="{typed("pa", X, len(prompt), 1.8, 300)}"').replace("</text>", '<tspan class="m"> ~ </tspan><tspan class="v">$ </tspan></text>'))
    body.append(mono(cmd, X + len(prompt) * cw, py, 13, "v", extra=f' clip-path="{typed("pb", X + len(prompt) * cw, len(cmd), 2.3, 12)}"'))
    body.append(f'<rect class="cursor" x="{X + (len(prompt) + len(cmd)) * cw + 2:.1f}" y="{py - 12}" width="{cw:.1f}" height="16" fill="{LIME}"/>')
    body.append(f'<rect x="32" y="{py - 8}" width="6" height="6" fill="{LIME}"/>' + mono("PORTRAIT TYPESET FROM MY OWN WORDS", 46, py, 10, "m", spacing=0.16))

    # A ticker along the bottom edge: the work, moving slowly past.
    ty = H - 30
    body.append(f'<rect x="0" y="{ty - 2}" width="{W}" height="1" fill="{LINE}"/>')
    run = TICKER * 3
    run_w = len(TICKER) * 11 * MONO_CW
    body.append(f'<g clip-path="url(#frame)"><g class="tick" style="--run:-{run_w:.1f}px">' + mono(run, 32, ty + 19, 11, "m", spacing=0) + "</g></g>")

    used = "".join(k + v for k, v in SPEC) + prompt + cmd + TICKER + "56.46° N  2.97° W ENTØ STUDIOS  /  FILE Nº 001 PORTRAIT TYPESET FROM MY OWN WORDS REPOS LIVE SITES CONTRIBUTIONS, 2026"
    css = (
        embedded_font(used)
        + f'text{{font-family:"SM",ui-monospace,monospace;fill:{INK}}}.m{{fill:{MUTED}}}.v{{fill:{INK}}}.k{{fill:{LIME};font-weight:700}}'
        f".l{{animation:rise 1.1s {EASE} both}}@keyframes rise{{from{{transform:translateY({size * 1.1:.0f}px)}}}}"
        ".f{animation:fade .8s ease both}@keyframes fade{from{opacity:0;transform:translateY(8px)}}"
        ".cursor{animation:blink 1.06s steps(1) infinite}@keyframes blink{50%{opacity:0}}"
        ".tick{animation:tick 40s linear infinite}@keyframes tick{to{transform:translateX(var(--run))}}"
        "@media (prefers-reduced-motion:reduce){.l,.f,.cursor,.tick{animation:none}}"
    )
    title = "Shrivas VM, founder and creative director of ENTØ Studios, based in Dundee, Scotland. A portrait of him typeset from his own words, looking across at his name, role, stack, work and live GitHub numbers."
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{escape(title)}">'
        f"<title>{escape(title)}</title><style>{css}</style><defs>{''.join(defs)}</defs>{''.join(body)}</svg>"
    )


if __name__ == "__main__":
    svg = build()
    (OUT / "top.svg").write_text(svg)
    print(f"top.svg {len(svg) / 1024:.0f} KB")
