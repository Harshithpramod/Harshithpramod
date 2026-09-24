"""Paint a Gotham gargoyle in code, as the source for the ASCII card.

A stone gargoyle crouched at the end of a cathedral ledge, facing out over the drop:
horned, open-jawed, bat wings folded up behind it, claws hooked over the edge. Behind
it the signal burns on the clouds, the only colour in the picture, and one eye catches it.

Returns (image, tint): an LA image whose alpha marks what is drawn and whose luminance
becomes glyph density, and an L mask marking the parts drawn in the signal colour.
"""

import math
import random
from collections.abc import Callable

from PIL import Image, ImageDraw, ImageFilter

from banner import bat_points

SIZE = (600, 776)
SUPERSAMPLE = 3
SEED = 13

SIGNAL = (205, 190, 150)   # cx, cy, r
LEDGE_Y = 560
STONE = 178


class _Canvas:
    """Luminance, coverage and tint layers, drawn together at supersampled size."""

    def __init__(self) -> None:
        big = (SIZE[0] * SUPERSAMPLE, SIZE[1] * SUPERSAMPLE)
        self.images = [Image.new("L", big, 0) for _ in range(3)]
        self.lum, self.alpha, self.tint = (ImageDraw.Draw(image) for image in self.images)

    def dot(self, x: float, y: float, r: float, lum: int, tinted: bool = False) -> None:
        box = [v * SUPERSAMPLE for v in (x - r, y - r, x + r, y + r)]
        self.lum.ellipse(box, fill=lum)
        self.alpha.ellipse(box, fill=255)
        self.tint.ellipse(box, fill=255 if tinted else 0)

    def polygon(self, points, lum: int, tinted: bool = False, erase: bool = False) -> None:
        scaled = [(x * SUPERSAMPLE, y * SUPERSAMPLE) for x, y in points]
        self.lum.polygon(scaled, fill=0 if erase else lum)
        self.alpha.polygon(scaled, fill=0 if erase else 255)
        self.tint.polygon(scaled, fill=255 if tinted and not erase else 0)

    def line(self, points, r: float, lum: int, tinted: bool = False) -> None:
        for (x0, y0), (x1, y1) in zip(points, points[1:]):
            steps = max(1, int(math.hypot(x1 - x0, y1 - y0) / 1.5))
            for i in range(steps + 1):
                self.dot(x0 + (x1 - x0) * i / steps, y0 + (y1 - y0) * i / steps, r, lum, tinted)


def _stroke(canvas: _Canvas, start, angle: float, length: float, bend: float,
            width: Callable[[float], float], lum: int, bend_power: float = 1.0, steps: int = 80):
    """A curved, tapering stroke; returns its tip."""
    x, y = start
    step = length / steps
    for i in range(steps + 1):
        t = i / steps
        canvas.dot(x, y, width(t), lum)
        heading = angle + bend * t ** bend_power
        x += step * math.cos(heading)
        y += step * math.sin(heading)
    return x, y


def _weather(canvas: _Canvas, rng: random.Random) -> None:
    """The signal on the clouds, the bat cut out of it, and rain across everything."""
    cx, cy, r = SIGNAL
    ring = [(cx + r * math.cos(a / 60 * math.tau), cy + r * 0.92 * math.sin(a / 60 * math.tau)) for a in range(60)]
    canvas.polygon(ring, 58, tinted=True)
    inner = [(cx + (x - cx) * 0.8, cy + (y - cy) * 0.8) for x, y in ring]
    canvas.polygon(inner, 40, tinted=True)
    canvas.polygon(bat_points(1.15, cx, cy - 6), 0, erase=True)
    for _ in range(46):
        x, y = rng.uniform(0, SIZE[0]), rng.uniform(0, SIZE[1] - 120)
        length = rng.uniform(16, 30)
        canvas.line([(x, y), (x - length * 0.3, y + length)], 1.3, 90)


def _building(canvas: _Canvas) -> None:
    """The ledge, a corbel under its end, and the cathedral wall with a lancet window."""
    canvas.polygon([(150, LEDGE_Y), (600, LEDGE_Y), (600, 598), (150, 598)], 158)
    canvas.line([(150, 578), (600, 578)], 1.6, 96)
    canvas.polygon([(158, 598), (262, 598), (246, 626), (214, 652), (182, 648), (166, 624)], 140)
    canvas.polygon([(262, 598), (600, 598), (600, 776), (262, 776)], 62)
    for y in range(640, 776, 34):  # masonry courses
        canvas.line([(262, y), (600, y)], 1.6, 120)
    # A pointed lancet window, dark, framed by a lighter arch.
    def arch(grow: float) -> list[tuple[float, float]]:
        crown = [(440 + (58 + grow) * math.cos(a), 700 - (74 + grow) * math.sin(a) ** 1.4)
                 for a in (math.pi - i / 30 * math.pi for i in range(31))]
        return [(382 - grow, 776)] + crown + [(498 + grow, 776)]

    canvas.polygon(arch(10), 196)
    canvas.polygon(arch(0), 0, erase=True)
    canvas.line([(440, 640), (440, 776)], 2.2, 150)


def _wing(canvas: _Canvas) -> None:
    """Folded bat wing behind the shoulders: a dark membrane between pale finger bones."""
    shoulder, wrist = (292, 340), (338, 186)
    fingers = [(424, 100), (486, 162), (520, 252), (514, 350)]
    outline = [shoulder, wrist, fingers[0]]
    for a, b in zip(fingers, fingers[1:] + [(446, 404)]):
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        outline += [(mid[0] + (wrist[0] - mid[0]) * 0.22, mid[1] + (wrist[1] - mid[1]) * 0.22), b]
    canvas.polygon(outline, 50)
    canvas.line([shoulder, wrist], 6, 206)
    for tip in fingers:
        canvas.line([wrist, tip], 3, 198)
    _stroke(canvas, wrist, -2.3, 26, -1.4, lambda t: 4 - 3 * t, 220)  # the thumb claw


def _body(canvas: _Canvas, rng: random.Random) -> None:
    """Crouched, hunched, facing left, with its tail curled over the back of the ledge."""
    _stroke(canvas, (468, 520), 0.1, 150, 3.2, lambda t: 9 - 6 * t, 150, bend_power=1.2)
    torso = [(196, 300), (250, 296), (320, 318), (402, 356), (460, 416), (484, 478), (466, 530),
             (414, 552), (300, 552), (252, 522), (230, 462), (214, 402), (194, 350)]
    canvas.polygon(torso, STONE)
    canvas.polygon([(x + (330 - x) * 0.35, y + (430 - y) * 0.35) for x, y in torso], STONE + 22)
    # Haunch, then the hind foot gripping the ledge.
    canvas.polygon([(420 + 64 * math.cos(a / 40 * math.tau), 478 + 58 * math.sin(a / 40 * math.tau)) for a in range(40)], 196)
    canvas.polygon([(350, 520), (440, 526), (446, LEDGE_Y), (344, LEDGE_Y)], 170)
    for x in (352, 378, 404, 430):
        canvas.polygon([(x - 7, LEDGE_Y - 2), (x + 9, LEDGE_Y - 2), (x + 2, LEDGE_Y + 10)], 214)
    # Foreleg down to claws hooked over the ledge's end.
    canvas.polygon([(214, 384), (258, 396), (230, 472), (212, 548), (178, 552), (186, 470)], 190)
    for x in (162, 178, 194):
        canvas.polygon([(x, LEDGE_Y - 4), (x + 14, LEDGE_Y - 2), (x - 2, LEDGE_Y + 20)], 222)
    # Weathered stone: pits and lichen as darker and lighter flecks.
    for _ in range(170):
        x, y = rng.uniform(190, 480), rng.uniform(300, 550)
        if _in_poly(x, y, torso):
            canvas.dot(x, y, rng.uniform(1.6, 3.2), rng.choice((120, 140, 226)))


def _head(canvas: _Canvas) -> None:
    """Jutting out over the drop: brow ridge, open jaw with fangs, a horn swept back."""
    _stroke(canvas, (200, 292), -1.75, 120, 2.3, lambda t: 11 - 9 * t, 206, bend_power=1.1)
    _stroke(canvas, (222, 298), -1.45, 78, 2.0, lambda t: 8 - 6.5 * t, 170, bend_power=1.1)
    canvas.polygon([(214, 300), (244, 252), (238, 312)], 188)  # ear
    skull = [(226, 296), (196, 282), (154, 284), (120, 296), (92, 314), (74, 332), (88, 342), (122, 338),
             (130, 350), (98, 360), (94, 372), (132, 376), (164, 364), (196, 362), (232, 350)]
    canvas.polygon(skull, 214)
    canvas.polygon([(88, 342), (122, 338), (130, 350), (98, 360)], 0, erase=True)  # the open mouth
    for x, y, down in ((96, 341, 1), (112, 339, 1), (104, 361, -1), (120, 358, -1)):
        canvas.polygon([(x - 4, y), (x + 4, y), (x, y + 13 * down)], 242)
    canvas.line([(120, 300), (150, 292), (186, 298)], 3, 120)  # brow ridge
    canvas.dot(162, 312, 9, 30)
    canvas.dot(160, 312, 4.5, 250, tinted=True)  # the eye, catching the signal
    canvas.line([(78, 330), (90, 326)], 2.2, 60)  # nostril


def _in_poly(x: float, y: float, poly) -> bool:
    inside = False
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            inside = not inside
    return inside


def render() -> tuple[Image.Image, Image.Image]:
    rng = random.Random(SEED)
    canvas = _Canvas()
    _weather(canvas, rng)
    _building(canvas)
    _wing(canvas)
    _body(canvas, rng)
    _head(canvas)

    lum, alpha, tint = (image.resize(SIZE, Image.LANCZOS) for image in canvas.images)
    return Image.merge("LA", (lum, alpha)).filter(ImageFilter.SMOOTH), tint


if __name__ == "__main__":
    image, tint = render()
    lum = image.getchannel("L")
    gold = Image.merge("RGB", (lum.point(lambda v: min(255, v * 2.6)), lum.point(lambda v: min(255, v * 2)), lum.point(lambda v: v * 0.3)))
    preview = Image.merge("RGB", (lum, lum, lum))
    preview.paste(gold, mask=tint)
    preview.save("gargoyle-preview.png")
