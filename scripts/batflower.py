"""Paint a black bat flower (Tacca chantrieri) in code, as the source for the ASCII card.

A real plant that looks like a bat: two pairs of dark, wing-shaped bracts spread either
side of a cluster of nodding buds, and long whiskers hang a foot below it all.

Returns (image, tint): an LA image whose alpha marks what is drawn and whose luminance
becomes glyph density, and an L mask marking the parts drawn in the bloom colour.
"""

import math
import random
from collections.abc import Callable

from PIL import Image, ImageDraw, ImageFilter

SIZE = (600, 776)
SUPERSAMPLE = 3
SEED = 39

CENTRE = (300, 236)
# (angle of the bract's axis, length, widest half-width). Upper pair spread like wings,
# lower pair droop.
BRACTS = ((-0.30, 262, 92), (math.pi + 0.30, 262, 92), (1.22, 170, 42), (math.pi - 1.22, 170, 42))
SCAPE = ((300, 250), (318, 110), (470, 30), (560, -10), 6)  # the stalk it nods from


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

    def polygon(self, points: list[tuple[float, float]], lum: int, tinted: bool) -> None:
        scaled = [(x * SUPERSAMPLE, y * SUPERSAMPLE) for x, y in points]
        self.lum.polygon(scaled, fill=lum)
        self.alpha.polygon(scaled, fill=255)
        self.tint.polygon(scaled, fill=255 if tinted else 0)


def _stroke(canvas: _Canvas, start: tuple[float, float], angle: float, length: float, bend: float,
            width: Callable[[float], float], lum: int, tinted: bool = False,
            bend_power: float = 1.0, steps: int = 90) -> tuple[float, float]:
    """A curved stroke whose heading turns by `bend` radians along its length; returns its tip."""
    x, y = start
    step = length / steps
    for i in range(steps + 1):
        t = i / steps
        heading = angle + bend * t ** bend_power
        canvas.dot(x, y, width(t), lum, tinted)
        x += step * math.cos(heading)
        y += step * math.sin(heading)
    return x, y


def _bract(canvas: _Canvas, angle: float, length: float, half: float, rng: random.Random) -> None:
    """A wing: ovate, its trailing edge scalloped like a bat's, with veins fanning from the base."""
    cx, cy = CENTRE
    ax, ay = math.cos(angle), math.sin(angle)
    nx, ny = -ay, ax  # normal to the axis
    # Which side of the axis faces down: that edge gets the scallops.
    lower = 1 if ny > 0 else -1

    def edge(t: float, side: int) -> tuple[float, float]:
        w = half * math.sin(math.pi * min(1.0, t ** 0.75)) ** 0.9
        if side == lower:
            w *= 1 - 0.28 * abs(math.sin(3 * math.pi * t)) ** 1.5
        # The tip sweeps upward a little, like a wing held open.
        sweep = -18 * t ** 2 * (1 if ay <= 0.5 else 0)
        return cx + ax * length * t + nx * w * side, cy + ay * length * t + ny * w * side + sweep

    steps = 80
    outline = [edge(i / steps, 1) for i in range(steps + 1)] + [edge(i / steps, -1) for i in range(steps, -1, -1)]
    canvas.polygon(outline, 196, True)
    # Veins: darker lines from the base, fanning toward the edges. They become texture in ASCII.
    for k in range(-3, 4):
        vein = []
        for i in range(0, steps + 1, 2):
            t = i / steps
            px, py = edge(t, 1 if k >= 0 else -1)
            mx, my = cx + ax * length * t, cy + ay * length * t
            share = abs(k) / 4 * t ** 0.6
            vein.append((mx + (px - mx) * share, my + (py - my) * share))
        for x, y in vein[3:-2]:
            canvas.dot(x, y, 1.6, 120, True)
    canvas.dot(cx, cy, 10, 170, True)


def _buds(canvas: _Canvas, rng: random.Random) -> None:
    """The flowers proper: a cluster of nodding buds on curved stalks, just below the centre."""
    for i in range(11):
        angle = math.pi / 2 + (i - 5) * 0.24 + rng.uniform(-0.06, 0.06)
        length = rng.uniform(40, 76)
        bend = 0.5 if angle < math.pi / 2 else -0.5
        tip = _stroke(canvas, CENTRE, angle, length, bend, lambda t: 2.2, 150, True)
        canvas.dot(*tip, rng.uniform(7, 9.5), 238, True)


def _whiskers(canvas: _Canvas, rng: random.Random) -> None:
    """The long filaments that make it a bat flower: fine, trailing, a little wind in them."""
    cx, cy = CENTRE
    for _ in range(24):
        start = (cx + rng.uniform(-22, 22), cy + rng.uniform(10, 26))
        angle = math.pi / 2 + rng.uniform(-0.3, 0.3)
        length = rng.uniform(340, 520)
        bend = rng.uniform(-0.35, 0.35)
        tip = _stroke(canvas, start, angle, length, bend, lambda t: 3.0 - 1.2 * t, rng.randint(205, 245),
                      bend_power=1.6, steps=160)
        canvas.dot(*tip, 2.6, 250, False)


def _scape(canvas: _Canvas) -> None:
    p0, p1, p2, p3, width = SCAPE
    for i in range(241):
        t = i / 240
        u = 1 - t
        x = u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0]
        y = u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]
        canvas.dot(x, y, width * (0.8 + 0.35 * t) / 2, 135, False)


def render() -> tuple[Image.Image, Image.Image]:
    rng = random.Random(SEED)
    canvas = _Canvas()
    _scape(canvas)
    _whiskers(canvas, rng)
    for angle, length, half in BRACTS[2:] + BRACTS[:2]:  # lower pair behind the upper
        _bract(canvas, angle, length, half, rng)
    _buds(canvas, rng)

    lum, alpha, tint = (image.resize(SIZE, Image.LANCZOS) for image in canvas.images)
    return Image.merge("LA", (lum, alpha)).filter(ImageFilter.SMOOTH), tint


if __name__ == "__main__":
    image, tint = render()
    lum = image.getchannel("L")
    preview = Image.merge("RGB", (lum, lum.point(lambda v: v * 0.8), lum))
    preview.save("batflower-preview.png")
