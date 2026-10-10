"""A portrait typeset from my own words: the letters are a stencil over my photo, so up close you read words
and from across the room you see a face.

Run: python design/wordportrait.py   (writes design/shots/wordportrait-dark.png at 2x)
Needs the background-removed photo at design/shots/portrait-cut.png (the café photo, cut out with rembg).
"""

from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps

HERE = Path(__file__).parent
WORDS = "SHRIVAS VM · ENTØ STUDIOS · DESIGN · BUILD · MOTION · DUNDEE · GOTHAM · THE DAILY BUGLE · POLISHED FAST ACCESSIBLE HUMAN · "
CROP = (360, 80, 1129, 900)  # head to chest in the 1536 x 1305 café photo, above the table
SIZE = (1200, 1280)  # output at 2x
FONT_PX = 13
LEADING = 13
UNDERLAY = 0.32  # how much of the photo shows between the letters
CURVE = (0.08, 0.48)  # hair and jacket stay dark below the first value; skin lifts toward the second
LOCAL = 0.2  # share of local contrast, which keeps the glasses and the hand crisp
BG, INK = (6, 6, 6), (240, 237, 232)


def tone_map():
    cut = Image.open(HERE / "shots" / "portrait-cut.png").convert("RGBA").crop(CROP)
    cut = cut.resize((SIZE[0], round(SIZE[0] * cut.height / cut.width)), Image.LANCZOS)
    canvas = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    canvas.paste(cut, (0, 0))
    mask = canvas.getchannel("A")
    gray = ImageOps.autocontrast(ImageOps.grayscale(canvas.convert("RGB")), cutoff=0.5, mask=mask.point(lambda a: 255 if a > 128 else 0))
    broad = gray.filter(ImageFilter.GaussianBlur(60))
    local = ImageOps.autocontrast(ImageChops.subtract(gray, broad, scale=1, offset=128), cutoff=1)
    tone = Image.blend(gray, local, LOCAL).filter(ImageFilter.UnsharpMask(radius=3, percent=120, threshold=2))
    lo, hi = CURVE

    def curve(v):
        x = min(1, max(0, (v / 255 - lo) / (hi - lo)))
        return round(255 * (0.1 + 0.9 * x * x * (3 - 2 * x)))

    return tone.point(curve), mask


def render() -> Image.Image:
    light, mask = tone_map()
    font = ImageFont.truetype(str(HERE / "fonts" / "SpaceMono-Bold.ttf"), FONT_PX)
    cw = font.getlength("M")
    stencil = Image.new("L", SIZE, 0)
    draw = ImageDraw.Draw(stencil)
    i = 0
    for row in range(int(SIZE[1] // LEADING) + 1):
        line = "".join(WORDS[(i + k) % len(WORDS)] for k in range(int(SIZE[0] // cw) + 2))
        draw.text((0, row * LEADING), line, font=font, fill=255)
        i += len(line) - 3
    strength = ImageChops.multiply(light, mask)
    amount = ImageChops.lighter(ImageChops.multiply(strength, stencil), strength.point(lambda v: round(v * UNDERLAY)))
    return Image.composite(Image.new("RGB", SIZE, INK), Image.new("RGB", SIZE, BG), amount)


if __name__ == "__main__":
    im = render()
    im.save(HERE / "shots" / "wordportrait-dark.png")
    print(im.size)
