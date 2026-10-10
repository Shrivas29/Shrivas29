"""Turn the founder photo into an ASCII portrait set in Space Mono, densest marks ending in ENTØ's Ø.

Run: python design/portrait.py   (writes design/portrait.txt)
Needs the background-removed photo at design/shots/portrait-cut.png.
"""

from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps

HERE = Path(__file__).parent
COLS = 48
CELL = (8.568, 18.0)  # Space Mono at 14px: advance width and line height
CROP = (240, 230, 720, 850)  # head and shoulders in the 960 x 1280 photo
CANDIDATES = " .'-:;~=+*!|/tvxcoesa#%&$gd@QNØ"


def ramp() -> list[tuple[float, str]]:
    """Each candidate's ink coverage in Space Mono, light to dense."""
    font = ImageFont.truetype(str(HERE / "fonts" / "SpaceMono-Regular.ttf"), 64)
    out = []
    for ch in CANDIDATES:
        im = Image.new("L", (64, 120), 0)
        ImageDraw.Draw(im).text((0, 10), ch, font=font, fill=255)
        out.append((sum(im.get_flattened_data()) / (64 * 120 * 255), ch))
    out.sort()
    lo, hi = out[0][0], out[-1][0]
    return [((d - lo) / (hi - lo), ch) for d, ch in out]


def nearest(table, v: float) -> str:
    return min(table, key=lambda dc: abs(dc[0] - v))[1]


def render() -> str:
    cut = Image.open(HERE / "shots" / "portrait-cut.png").convert("RGBA").crop(CROP)
    w, h = cut.size
    rows = round(COLS * (h / w) * (CELL[0] / CELL[1]))
    mask = cut.getchannel("A").point(lambda a: 255 if a > 128 else 0)
    gray = ImageOps.autocontrast(ImageOps.grayscale(cut.convert("RGB")), cutoff=1, mask=mask).filter(ImageFilter.GaussianBlur(1.2))
    # Three parts broad tone to one part local detail: hair stays a mass, eyes and brows still read.
    broad = gray.filter(ImageFilter.GaussianBlur(26))
    local = ImageOps.autocontrast(ImageChops.subtract(gray, broad, scale=1, offset=128), cutoff=2)
    tone = Image.blend(gray, local, 0.25).resize((COLS, rows), Image.LANCZOS)
    alpha = cut.getchannel("A").resize((COLS, rows), Image.LANCZOS)
    table = ramp()
    lines = []
    for y in range(rows):
        row = ""
        for x in range(COLS):
            a = alpha.getpixel((x, y)) / 255
            if a < 0.35:
                row += " "
                continue
            # Shadows take the dense marks, like ink: the hair reads as a mass on either ground.
            v = (1 - tone.getpixel((x, y)) / 255) ** 1.15 * a
            row += nearest(table, max(0.04, min(1.0, v)))
        lines.append(row.rstrip())
    while lines and not lines[0].strip():
        lines.pop(0)
    return "\n".join(lines)


if __name__ == "__main__":
    text = render()
    (HERE / "portrait.txt").write_text(text)
    print(f"{len(text.splitlines())} rows\n{text}")
