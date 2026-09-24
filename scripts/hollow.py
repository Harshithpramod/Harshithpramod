"""Paint a Hollow mask in code, as the source for the ASCII card.

Original fan art after Bleach: a bone-white mask, sculpted rather than smooth, with empty
angled eyes, a grin of teeth, a crack across the brow, and the red stripes running down
one side. Loose reiatsu drifts off its edges.

Returns (image, tint): an LA image whose alpha marks what is drawn and whose luminance
becomes glyph density, and an L mask marking the parts drawn in the bloom colour.
"""

import math
import random

from PIL import Image, ImageDraw, ImageFilter

SIZE = (600, 776)
SUPERSAMPLE = 3
SEED = 5

CX = 300
TOP, BOTTOM = 96, 704
EYE_Y = 350


def half_width(y: float) -> float:
    """The mask's outline: a domed brow, full cheekbones, a jaw that tapers to the chin."""
    t = (y - TOP) / (BOTTOM - TOP)
    if t < 0 or t > 1:
        return 0.0
    if t < 0.34:
        return 190 * math.sqrt(max(0.0, 1 - ((0.34 - t) / 0.34) ** 2))
    if t < 0.6:
        return 190 - 12 * (t - 0.34) / 0.26
    u = (t - 0.6) / 0.4
    width = 178 - 74 * u ** 1.3
    return width * math.sqrt(max(0.0, 1 - max(0.0, (u - 0.9) / 0.1) ** 2)) if u > 0.9 else width


class _Canvas:
    """Luminance, coverage and tint layers, drawn together at supersampled size."""

    def __init__(self) -> None:
        big = (SIZE[0] * SUPERSAMPLE, SIZE[1] * SUPERSAMPLE)
        self.images = [Image.new("L", big, 0) for _ in range(3)]
        self.lum, self.alpha, self.tint = (ImageDraw.Draw(image) for image in self.images)

    def dot(self, x: float, y: float, r: float, lum: int, tinted: bool) -> None:
        box = [v * SUPERSAMPLE for v in (x - r, y - r, x + r, y + r)]
        self.lum.ellipse(box, fill=lum)
        self.alpha.ellipse(box, fill=255)
        self.tint.ellipse(box, fill=255 if tinted else 0)

    def polygon(self, points: list[tuple[float, float]], lum: int, tinted: bool = False, erase: bool = False) -> None:
        scaled = [(x * SUPERSAMPLE, y * SUPERSAMPLE) for x, y in points]
        self.lum.polygon(scaled, fill=0 if erase else lum)
        self.alpha.polygon(scaled, fill=0 if erase else 255)
        self.tint.polygon(scaled, fill=255 if tinted and not erase else 0)


def _inside(x: float, y: float, margin: float = 0) -> bool:
    return abs(x - CX) < half_width(y) - margin


def _line(canvas: _Canvas, points: list[tuple[float, float]], r: float, lum: int, tinted: bool = False) -> None:
    """A polyline of dots, kept on the mask."""
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        steps = max(1, int(math.hypot(x1 - x0, y1 - y0) / 1.5))
        for i in range(steps + 1):
            x, y = x0 + (x1 - x0) * i / steps, y0 + (y1 - y0) * i / steps
            if _inside(x, y, r + 2):
                canvas.dot(x, y, r, lum, tinted)


def _face(canvas: _Canvas) -> None:
    """Bone white, brighter toward the centre so the ASCII reads it as rounded."""
    for scale, lum in ((1.0, 168), (0.86, 196), (0.68, 222), (0.46, 242)):
        right = [(CX + half_width(y) * scale, y) for y in range(TOP, BOTTOM + 1, 4)]
        mid = (TOP + BOTTOM) / 2 - 30
        right = [(x, mid + (y - mid) * (0.4 + 0.6 * scale)) for x, y in right]
        canvas.polygon(right + [(2 * CX - x, y) for x, y in reversed(right)], lum)


def _stripes(canvas: _Canvas) -> None:
    """Two red bands down the mask's left side (the viewer's right), through the eye."""
    for offset, end in ((62, 572), (104, 548)):
        for y in range(TOP, end, 2):
            t = (y - TOP) / (end - TOP)
            x = CX + offset + 12 * math.sin((y - TOP) / 170)
            r = 2 + 12 * math.sin(math.pi * min(1.0, t * 1.05)) ** 0.5  # tapered to points at both ends
            if _inside(x, y, r + 2):
                canvas.dot(x, y, r, 205, True)


def _eyes(canvas: _Canvas) -> None:
    """Empty and angled down toward the nose, with a dark rim so the edge reads."""
    shape = ((40, 22), (42, -6), (98, -32), (112, -12), (92, 24), (60, 34))
    for side in (-1, 1):
        rim = [(CX + side * (x * 1.2 - 8), EYE_Y + y * 1.6) for x, y in shape]
        hole = [(CX + side * x * 1.12, EYE_Y + y * 1.35) for x, y in shape]
        canvas.polygon(rim, 70)
        canvas.polygon(hole, 0, erase=True)
    for side in (-1, 1):  # nostril slits
        _line(canvas, [(CX + side * 8, 452), (CX + side * 16, 478)], 2.6, 50)


def _teeth(canvas: _Canvas) -> None:
    """A wide grin: two rows of teeth meeting on a curved line."""
    def smile(x: float, lift: float) -> float:
        return 612 + lift - 18 * (1 - ((x - CX) / 110) ** 2)

    xs = list(range(CX - 118, CX + 119, 3))
    _line(canvas, [(x, smile(x, 0)) for x in xs], 2.8, 30)
    _line(canvas, [(x, smile(x, -30)) for x in xs], 1.8, 110)
    _line(canvas, [(x, smile(x, 30)) for x in xs], 1.8, 110)
    for x in range(CX - 108, CX + 109, 18):
        _line(canvas, [(x, smile(x, -30)), (x, smile(x, 30))], 1.6, 60)


def _crack(canvas: _Canvas) -> None:
    pts = [(CX - 186, 250), (CX - 150, 236), (CX - 136, 212), (CX - 104, 206), (CX - 92, 180), (CX - 60, 170)]
    _line(canvas, pts, 3.6, 20)
    _line(canvas, [(CX - 136, 212), (CX - 126, 256)], 3.0, 30)


def _reiatsu(canvas: _Canvas, rng: random.Random) -> None:
    """Spiritual pressure bleeding off the edges, some of it red."""
    placed = 0
    while placed < 90:
        y = rng.uniform(TOP - 60, BOTTOM + 40)
        side = rng.choice((-1, 1))
        x = CX + side * (half_width(y) + rng.uniform(14, 130) ** 1.05)
        if not 8 < x < SIZE[0] - 8 or _inside(x, y, -10):
            continue
        canvas.dot(x, y, rng.uniform(2.8, 4.4), rng.randint(90, 220), rng.random() < 0.35)
        placed += 1


def render() -> tuple[Image.Image, Image.Image]:
    rng = random.Random(SEED)
    canvas = _Canvas()
    _reiatsu(canvas, rng)
    _face(canvas)
    _stripes(canvas)
    _crack(canvas)
    _teeth(canvas)
    _eyes(canvas)

    lum, alpha, tint = (image.resize(SIZE, Image.LANCZOS) for image in canvas.images)
    return Image.merge("LA", (lum, alpha)).filter(ImageFilter.SMOOTH), tint


if __name__ == "__main__":
    image, tint = render()
    lum = image.getchannel("L")
    red = Image.merge("RGB", (lum, lum.point(lambda v: v * 0.25), lum.point(lambda v: v * 0.3)))
    preview = Image.merge("RGB", (lum, lum, lum))
    preview.paste(red, mask=tint)
    preview.save("hollow-preview.png")
