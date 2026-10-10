"""Set type as SVG outlines, so the profile graphics need no web fonts and render the same everywhere."""

from functools import lru_cache
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONTS = Path(__file__).parent / "fonts"


@lru_cache(maxsize=None)
def _font(name: str):
    path = FONTS / f"{name}.ttf"
    blob = hb.Blob.from_file_path(str(path))
    face = hb.Face(blob)
    tt = TTFont(path)
    return hb.Font(face), tt, tt["head"].unitsPerEm


def shape(name: str, text: str, size: float, tracking: float = 0.0):
    """Shaped glyphs as (x_advance_start, glyph_name, cluster) in px, plus the line width. Tracking is in em."""
    font, tt, upem = _font(name)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True, "liga": True})
    scale = size / upem
    order = tt.getGlyphOrder()
    x = 0.0
    out = []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        out.append((x + pos.x_offset * scale, order[info.codepoint], info.cluster))
        x += pos.x_advance * scale + tracking * size
    return out, x - tracking * size


def glyph_d(name: str, glyph: str, size: float, x: float, y: float) -> str:
    """Path data for one glyph with its origin at (x, y) on the baseline."""
    _, tt, upem = _font(name)
    scale = size / upem
    pen = SVGPathPen(tt.getGlyphSet(), ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
    tt.getGlyphSet()[glyph].draw(TransformPen(pen, (scale, 0, 0, -scale, x, y)))
    return pen.getCommands()


def width(name: str, text: str, size: float, tracking: float = 0.0) -> float:
    return shape(name, text, size, tracking)[1]


def text_d(name: str, text: str, size: float, x: float, y: float, tracking: float = 0.0, anchor: str = "start") -> str:
    """One path for a whole line. anchor: start, middle or end."""
    glyphs, w = shape(name, text, size, tracking)
    dx = {"start": 0, "middle": -w / 2, "end": -w}[anchor]
    return "".join(glyph_d(name, g, size, x + dx + gx, y) for gx, g, _ in glyphs)


def letters(name: str, text: str, size: float, x: float, y: float, tracking: float = 0.0):
    """Each character as its own path, for per-letter animation. Spaces are skipped."""
    glyphs, _ = shape(name, text, size, tracking)
    return [(text[c], glyph_d(name, g, size, x + gx, y)) for gx, g, c in glyphs if text[c].strip()]
