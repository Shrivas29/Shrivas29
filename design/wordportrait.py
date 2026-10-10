"""A portrait typeset from my own words: each letter of a repeating line takes its brightness from the photo.

Run: python design/wordportrait.py   (writes design/shots/wordportrait-<mode>.png at 2x)
Needs the background-removed photo at design/shots/portrait-cut.png.
"""

from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps

HERE = Path(__file__).parent
WORDS = "SHRIVAS VM · ENTØ STUDIOS · DESIGN · BUILD · MOTION · DUNDEE · GOTHAM · THE DAILY BUGLE · POLISHED FAST ACCESSIBLE HUMAN · "
CROP = (200, 230, 760, 860)  # head and shoulders in the 960 x 1280 photo
SIZE = (1140, 1280)  # output at 2x
FONT_PX = 13
LEADING = 13
UNDERLAY = 0.24

GROUNDS = {"dark": ((6, 6, 6), (240, 237, 232)), "light": ((240, 237, 232), (6, 6, 6))}


def tone_map():
    """Brightness per output pixel: broad light with the facial detail lifted, the background cut away."""
    cut = Image.open(HERE / "shots" / "portrait-cut.png").convert("RGBA").crop(CROP)
    cut = cut.resize((SIZE[0], round(SIZE[0] * cut.height / cut.width)), Image.LANCZOS)
    canvas = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    canvas.paste(cut, (0, 0))
    mask = canvas.getchannel("A")
    gray = ImageOps.grayscale(canvas.convert("RGB"))
    gray = ImageOps.autocontrast(gray, cutoff=1, mask=mask.point(lambda a: 255 if a > 128 else 0))
    broad = gray.filter(ImageFilter.GaussianBlur(60))
    local = ImageOps.autocontrast(ImageChops.subtract(gray, broad, scale=1, offset=128), cutoff=1)
    tone = Image.blend(gray, local, 0.22).filter(ImageFilter.UnsharpMask(radius=3, percent=120, threshold=2))
    return tone, mask


def render(mode: str) -> Image.Image:
    """Letters as a stencil over the graded photo: up close you read words, from across the room you see a face."""
    bg, ink = GROUNDS[mode]
    tone, mask = tone_map()
    font = ImageFont.truetype(str(HERE / "fonts" / "SpaceMono-Bold.ttf"), FONT_PX)
    cw = font.getlength("M")
    stencil = Image.new("L", SIZE, 0)
    draw = ImageDraw.Draw(stencil)
    i = 0
    for row in range(int(SIZE[1] // LEADING) + 1):
        line = "".join(WORDS[(i + k) % len(WORDS)] for k in range(int(SIZE[0] // cw) + 2))
        draw.text((0, row * LEADING), line, font=font, fill=255)
        i += len(line) - 3
    # Brightness: light skin glows on the dark ground; the light ground prints the shadows.
    if mode == "dark":
        light = tone.point(lambda v: round(255 * min(1, (v / 255) ** 0.68 * 1.2)))
    else:
        light = ImageOps.invert(ImageOps.autocontrast(tone, cutoff=2)).point(lambda v: round(255 * (v / 255) ** 0.85))
    strength = ImageChops.multiply(light, mask)
    # A faint underlay of the photo fills the gaps between letters, so the face holds together.
    under = strength.point(lambda v: round(v * UNDERLAY))
    amount = ImageChops.lighter(ImageChops.multiply(strength, stencil), under)
    base = Image.new("RGB", SIZE, bg)
    top = Image.new("RGB", SIZE, ink)
    return Image.composite(top, base, amount)


if __name__ == "__main__":
    for mode in GROUNDS:
        im = render(mode)
        im.save(HERE / "shots" / f"wordportrait-{mode}.png")
        print(mode, im.size)
