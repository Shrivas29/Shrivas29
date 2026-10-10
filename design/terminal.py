"""The profile's top section: an ASCII portrait beside a system readout, set in Space Mono and booting like a console.

Run: python design/terminal.py   (writes assets/terminal-dark.svg and assets/terminal-light.svg)
Reads design/portrait.txt and live numbers from the GitHub API (GITHUB_TOKEN, or the gh CLI's token).
"""

import base64
import json
import os
import subprocess
import urllib.request
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools import subset
from fontTools.ttLib import TTFont

HERE = Path(__file__).parent
OUT = HERE.parent / "assets"
USER = "Shrivas29"

W = 1000
FONT = 14
CW = 8.568  # Space Mono's advance (612/1000 em) at 14px
LH = 18
PAD = 28
BAR = 40
COLS = 58  # readout width in characters

PALETTES = {
    "dark": {"bg": "#060606", "bar": "#0c0c0c", "line": "#2a2a2a", "ink": "#f0ede8", "face": "#f0ede8", "key": "#c8ff57", "dots": "#4a4844", "muted": "#8a8781", "lime": "#c8ff57", "on_lime": "#060606", "head": "#c8ff57"},
    "light": {"bg": "#f0ede8", "bar": "#e9e5de", "line": "#cfcac1", "ink": "#2b2925", "face": "#060606", "key": "#060606", "dots": "#b3ada3", "muted": "#67645f", "lime": "#c8ff57", "on_lime": "#060606", "head": "#060606"},
}


# ---------------------------------------------------------------- live numbers


def token() -> str | None:
    if os.environ.get("GITHUB_TOKEN"):
        return os.environ["GITHUB_TOKEN"]
    try:
        return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def stats() -> dict:
    """Public repos, live sites (repos with a homepage) and this year's contributions."""
    query = '{ user(login: "%s") { repositories(privacy: PUBLIC, first: 100, ownerAffiliations: OWNER) { totalCount nodes { name homepageUrl } } contributionsCollection { contributionCalendar { totalContributions } } } }' % USER
    req = urllib.request.Request("https://api.github.com/graphql", data=json.dumps({"query": query}).encode(), headers={"Authorization": f"bearer {token()}", "User-Agent": USER})
    data = json.load(urllib.request.urlopen(req))["data"]["user"]
    repos = data["repositories"]
    return {
        "repos": repos["totalCount"],
        "live": sum(1 for n in repos["nodes"] if n["homepageUrl"] and n["name"] != USER),
        "contributions": data["contributionsCollection"]["contributionCalendar"]["totalContributions"],
    }


# ---------------------------------------------------------------- the readout


def leader(key: str, value: str) -> tuple[str, str, str]:
    dots = COLS - len(key) - len(value) - 2
    return key, " " + "." * dots + " ", value


def readout(s: dict) -> list:
    """Each line is a tuple: ("head", title), ("kv", key, value), ("text", str), ("prompt", command) or None for a gap."""
    return [
        ("head", "shrivas@entø"),
        ("kv", "OS", "Designer, developer, founder"),
        ("kv", "Host", "ENTØ Studios"),
        ("kv", "Uptime", "2 years of shipping websites"),
        ("kv", "Location", "Dundee, Scotland · 56.46° N"),
        ("kv", "Kernel", "Next.js · React · TypeScript"),
        ("kv", "Shell", "Framer Motion · GSAP · Lenis"),
        ("kv", "Theme", "Syne · Space Grotesk · lime"),
        ("kv", "Resolution", "Polished, fast, accessible, human."),
        None,
        ("kv", "Work.Fan", "Gotham · The Daily Bugle"),
        ("kv", "Work.Client", "Vidyuth Nº12 · Sujitha M"),
        ("kv", "Work.Studio", "ENTØ Studios · Shrivas PS"),
        None,
        ("head", "Contact"),
        ("kv", "Email", "shrivasvm@gmail.com"),
        ("kv", "Portfolio", "shrivas-console.vercel.app"),
        ("kv", "Studio", "entostudios.com"),
        ("kv", "Instagram", "@buildwithento"),
        ("kv", "LinkedIn", "shrivas-vm"),
        None,
        ("head", "GitHub"),
        ("stats", s),
        None,
        ("prompt", "open gotham"),
        ("text", "↓ live at gotham-ashen.vercel.app, featured below"),
    ]


# ---------------------------------------------------------------- the font, embedded


def embedded_font(chars: str) -> str:
    rules = ""
    for weight, name in ((400, "SpaceMono-Regular"), (700, "SpaceMono-Bold")):
        font = TTFont(HERE / "fonts" / f"{name}.ttf")
        sub = subset.Subsetter(subset.Options(flavor="woff2", layout_features=["*"], name_IDs=["*"]))
        sub.populate(text=chars)
        sub.subset(font)
        buf = BytesIO()
        font.flavor = "woff2"
        font.save(buf)
        data = base64.b64encode(buf.getvalue()).decode()
        rules += f'@font-face{{font-family:"SM";font-weight:{weight};src:url(data:font/woff2;base64,{data}) format("woff2")}}'
    return rules


# ---------------------------------------------------------------- the frame


def build(mode: str, portrait: list[str], s: dict) -> str:
    p = PALETTES[mode]
    lines = readout(s)
    rows = max(len(portrait), len(lines))
    h = BAR + PAD + rows * LH + PAD
    px, rx = PAD, PAD + 48 * CW + 30
    top = BAR + PAD + 13  # first baseline
    out = []
    clips = []
    t = 0.0

    def typed(i: int, x: float, y: float, chars: int, start: float, cps: float = 140) -> str:
        """A clip that reveals a line from the left, like it is being typed. Without SMIL the line simply shows."""
        w = chars * CW + 4
        dur = max(0.05, chars / cps)
        total = 4.6
        k0, k1 = start / total, min(1, (start + dur) / total)
        clips.append(
            f'<clipPath id="t{i}"><rect x="{x - 2}" y="{y - 14}" height="{LH}" width="{w:.1f}">'
            f'<animate attributeName="width" dur="{total}s" values="0;0;{w:.1f}" keyTimes="0;{k0:.4f};{k1:.4f}" fill="freeze"/></rect></clipPath>'
        )
        return f't{i}'

    # Title bar.
    out.append(f'<rect width="{W}" height="{BAR}" fill="{p["bar"]}"/><rect y="{BAR - 1}" width="{W}" height="1" fill="{p["line"]}"/>')
    out.append(f'<rect x="{PAD}" y="{BAR / 2 - 5}" width="10" height="10" fill="{p["lime"]}"/>')
    out.append(f'<text class="bar" x="{PAD + 20}" y="{BAR / 2 + 4}">entø ~/studio/shrivas</text>')
    out.append(f'<text class="bar" x="{W - PAD}" y="{BAR / 2 + 4}" text-anchor="end">session 001 · 2026</text>')

    # Portrait, revealed by a scan line running down it.
    ph = len(portrait) * LH
    out.append(
        f'<clipPath id="face"><rect x="0" y="{BAR + PAD}" width="{rx - 10}" height="{ph}">'
        f'<animate attributeName="height" dur="1.3s" values="0;{ph}" keySplines=".45 0 .25 1" calcMode="spline" fill="freeze"/></rect></clipPath>'
    )
    face = "".join(f'<text x="{px}" y="{top + i * LH}" xml:space="preserve">{escape(row)}</text>' for i, row in enumerate(portrait))
    out.append(f'<g class="face" clip-path="url(#face)">{face}</g>')
    out.append(
        f'<rect class="scan" x="{px - 6}" y="{BAR + PAD}" width="{48 * CW + 12}" height="2" fill="{p["lime"]}">'
        f'<animate attributeName="y" dur="1.3s" values="{BAR + PAD};{BAR + PAD + ph}" keySplines=".45 0 .25 1" calcMode="spline" fill="freeze"/>'
        f'<animate attributeName="opacity" dur="1.6s" values="1;1;0" keyTimes="0;.8;1" fill="freeze"/></rect>'
    )

    # The readout, typed line by line.
    start = 0.35
    for i, line in enumerate(lines):
        y = top + i * LH
        if line is None:
            continue
        kind = line[0]
        if kind == "head":
            title = line[1]
            label = title if title.startswith("shrivas") else f"- {title}"
            cid = typed(i, rx, y, COLS, start, 260)
            x2 = rx + (len(label) + 1) * CW
            if mode == "light" and title.startswith("shrivas"):
                out.append(f'<g clip-path="url(#{cid})"><rect x="{rx - 3}" y="{y - 13}" width="{len(label) * CW + 6}" height="17" fill="{p["lime"]}"/><text class="head" x="{rx}" y="{y}">{escape(label)}</text><rect x="{x2}" y="{y - 5}" width="{rx + COLS * CW - x2}" height="1" fill="{p["line"]}"/></g>')
            else:
                out.append(f'<g clip-path="url(#{cid})"><text class="head" x="{rx}" y="{y}">{escape(label)}</text><rect x="{x2}" y="{y - 5}" width="{rx + COLS * CW - x2}" height="1" fill="{p["line"]}"/></g>')
            start += 0.12
        elif kind == "kv":
            k, d, v = leader(line[1], line[2])
            cid = typed(i, rx, y, COLS, start)
            out.append(f'<text clip-path="url(#{cid})" x="{rx}" y="{y}" xml:space="preserve"><tspan class="k">{escape(k)}</tspan><tspan class="d">{d}</tspan><tspan class="v">{escape(v)}</tspan></text>')
            start += 0.07
        elif kind == "stats":
            st = line[1]
            parts = [("Repos", st["repos"]), ("Live sites", st["live"]), (f"Contributions", st["contributions"])]
            text = ""
            for j, (k, v) in enumerate(parts):
                sep = '<tspan class="d">  |  </tspan>' if j else ""
                text += f'{sep}<tspan class="k">{k}</tspan><tspan class="d"> .. </tspan><tspan class="v">{v}</tspan>'
            cid = typed(i, rx, y, COLS, start)
            out.append(f'<text clip-path="url(#{cid})" x="{rx}" y="{y}" xml:space="preserve">{text}</text>')
            start += 0.1
        elif kind == "prompt":
            prompt = "shrivas@entø ~ $ "
            start += 0.25
            cid_a = typed(i, rx, y, len(prompt), start, 400)
            cid_b = typed(i + 100, rx + len(prompt) * CW, y, len(line[1]), start + 0.2, 14)
            out.append(f'<text clip-path="url(#{cid_a})" x="{rx}" y="{y}" xml:space="preserve"><tspan class="k">shrivas@entø</tspan><tspan class="d"> ~ </tspan><tspan class="v">$ </tspan></text>')
            out.append(f'<text clip-path="url(#{cid_b})" x="{rx + len(prompt) * CW}" y="{y}" class="v">{escape(line[1])}</text>')
            cx = rx + (len(prompt) + len(line[1])) * CW + 2
            out.append(f'<rect class="cursor" x="{cx:.1f}" y="{y - 12}" width="{CW:.1f}" height="16" fill="{p["lime"]}" stroke="{p["on_lime"] if mode == "light" else "none"}" stroke-width="1"/>')
            start += 0.2 + len(line[1]) / 14 + 0.2
        elif kind == "text":
            cid = typed(i, rx, y, len(line[1]), start, 90)
            out.append(f'<text clip-path="url(#{cid})" class="m" x="{rx}" y="{y}">{escape(line[1])}</text>')

    used = "".join(portrait) + "".join(" ".join(str(x) for x in l[1:]) if l else "" for l in lines) + "shrivas@entø ~ $ .|-0123456789 entøstudioshrivasssion·2026/~"
    css = (
        embedded_font(used + "Contributions Live sites Repos")
        + f'text{{font-family:"SM",ui-monospace,monospace;font-size:{FONT}px;fill:{p["ink"]}}}'
        f'.bar{{font-size:12px;letter-spacing:.06em;fill:{p["muted"]}}}'
        f'.face text{{fill:{p["face"]};opacity:.9}}'
        f'.head{{font-weight:700;fill:{p["head"]}}}'
        f'.k{{font-weight:700;fill:{p["key"]}}}.d{{fill:{p["dots"]}}}.v{{fill:{p["ink"]}}}.m{{fill:{p["muted"]}}}'
        ".cursor{animation:blink 1.06s steps(1) infinite}@keyframes blink{50%{opacity:0}}"
        "@media (prefers-reduced-motion:reduce){.cursor{animation:none}}"
    )
    title = "shrivas@entø: designer, developer, founder of ENTØ Studios, based in Dundee, Scotland. ASCII portrait beside a system readout."
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" role="img" aria-label="{escape(title)}">'
        f"<title>{escape(title)}</title><style>{css}</style>"
        f'<rect width="{W}" height="{h}" fill="{p["bg"]}"/>'
        f'<defs>{"".join(clips)}</defs>{"".join(out)}</svg>'
    )


def main():
    portrait = (HERE / "portrait.txt").read_text().split("\n")
    s = stats()
    for mode in PALETTES:
        svg = build(mode, portrait, s)
        (OUT / f"terminal-{mode}.svg").write_text(svg)
        print(f"terminal-{mode}.svg {len(svg) / 1024:.1f} KB", s)


if __name__ == "__main__":
    main()
