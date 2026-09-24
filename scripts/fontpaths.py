"""Turn text into SVG path data, so the art renders identically on every machine.

GitHub serves README images as <img>, which cannot load web fonts, and viewers
without a CJK brush font would otherwise see kanji in a fallback face.
"""

from dataclasses import dataclass
from functools import lru_cache

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont


@dataclass(frozen=True)
class FontRef:
    path: str
    axes: tuple[tuple[str, float], ...] = ()  # pins a variable font, e.g. (("wght", 500),)


@dataclass(frozen=True)
class Shaped:
    d: str
    width: float
    height: float  # the em size, for vertical layout
    ascent: float = 0.0  # distance from the path's top edge down to the baseline


@lru_cache(maxsize=None)
def _load(ref: FontRef) -> TTFont:
    font = TTFont(ref.path)
    if ref.axes:
        font = instantiateVariableFont(font, dict(ref.axes))
    return font


def text_path(ref: FontRef, text: str, size: float, tracking: float = 0.0) -> Shaped:
    """Lay out one line left to right. `tracking` is extra space per glyph, in ems."""
    font = _load(ref)
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    scale = size / font["head"].unitsPerEm
    ascent = font["hhea"].ascent

    pen = SVGPathPen(glyph_set)
    x = 0.0
    for char in text:
        name = cmap.get(ord(char))
        if name is None:
            raise ValueError(f"{ref.path} has no glyph for {char!r}")
        # Font units point up; SVG points down. Flip and place the baseline at the ascent.
        transform = (scale, 0, 0, -scale, x, ascent * scale)
        glyph_set[name].draw(TransformPen(pen, transform))
        x += glyph_set[name].width * scale + tracking * size
    width = x - tracking * size if text else 0.0
    return Shaped(d=pen.getCommands(), width=width, height=size, ascent=ascent * scale)


def vertical_path(ref: FontRef, text: str, size: float, gap: float = 0.1) -> Shaped:
    """Stack glyphs top to bottom, each centred in its column (for kanji)."""
    parts = []
    y = 0.0
    for char in text:
        glyph = text_path(ref, char, size)
        dx = (size - glyph.width) / 2
        parts.append(f'<path transform="translate({dx:.2f} {y:.2f})" d="{glyph.d}"/>')
        y += size * (1 + gap)
    return Shaped(d="".join(parts), width=size, height=y - size * gap)
