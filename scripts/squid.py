"""Paint a vampire squid (Vampyroteuthis infernalis) in code, as the source for the ASCII card.

A living fossil from the oxygen-starved dark 600 to 1,200 m down. Two ear-like fins on
the mantle, a webbed cloak between eight arms lined with soft spines, glowing
photophores at the arm tips, and two long filaments it trails to catch marine snow.

Returns (image, tint): an LA image whose alpha marks what is drawn and whose luminance
becomes glyph density, and an L mask marking the parts drawn in the bloom colour.
"""

import math
import random
from collections.abc import Callable

from PIL import Image, ImageDraw, ImageFilter

SIZE = (600, 776)
SUPERSAMPLE = 3
SEED = 11

CX = 300
MANTLE_TOP, MANTLE_BASE, MANTLE_HALF = 64, 300, 78
EYES = ((CX - 50, 268), (CX + 50, 268))
CLOAK_TOP = 318
ARMS = 8


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
            bend_power: float = 1.0, steps: int = 90) -> list[tuple[float, float, float]]:
    """A curved stroke whose heading turns by `bend` radians along its length.
    Returns the points it passed through, with their headings."""
    x, y = start
    step = length / steps
    trail = []
    for i in range(steps + 1):
        t = i / steps
        heading = angle + bend * t ** bend_power
        canvas.dot(x, y, width(t), lum, tinted)
        trail.append((x, y, heading))
        x += step * math.cos(heading)
        y += step * math.sin(heading)
    return trail


def _mantle(canvas: _Canvas) -> None:
    """A tall dome, narrowing to a blunt top, with the fins standing off it like ears."""
    for side in (-1, 1):
        fx, fy = CX + side * 50, 150  # where the fin joins the mantle
        tilt = -side * 0.6            # raised and angled out, like the ears of a cowl
        ox, oy = fx + side * 40 * math.cos(tilt), fy + side * 40 * math.sin(tilt)
        fin = [
            (ox + 48 * math.cos(a) * math.cos(tilt) - 19 * math.sin(a) * math.sin(tilt),
             oy + 48 * math.cos(a) * math.sin(tilt) + 19 * math.sin(a) * math.cos(tilt))
            for a in (i / 48 * math.tau for i in range(48))
        ]
        canvas.polygon(fin, 196, True)
        canvas.dot(fx + side * 6, fy - 4, 6, 255, False)  # photophore at the fin's base

    steps = 60
    right = []
    for i in range(steps + 1):
        t = i / steps
        y = MANTLE_TOP + (MANTLE_BASE - MANTLE_TOP) * t
        right.append((CX + MANTLE_HALF * math.sin(math.pi / 2 * t) ** 0.55, y))
    outline = right + [(2 * CX - x, y) for x, y in reversed(right)]
    canvas.polygon(outline, 150, True)
    # Faint chromatophore mottling, which the ASCII turns into texture.
    rng = random.Random(SEED + 1)
    for _ in range(70):
        t = rng.uniform(0.08, 0.95)
        y = MANTLE_TOP + (MANTLE_BASE - MANTLE_TOP) * t
        half = MANTLE_HALF * math.sin(math.pi / 2 * t) ** 0.55 - 8
        canvas.dot(CX + rng.uniform(-half, half), y, rng.uniform(2, 4.5), rng.choice((95, 205)), True)


def _eyes(canvas: _Canvas) -> None:
    """Proportionally the largest eyes of any animal: pale, glowing, with a dark pupil."""
    for x, y in EYES:
        canvas.dot(x, y, 22, 60, False)
        canvas.dot(x, y, 18, 255, False)
        canvas.dot(x + 2, y + 2, 8, 30, False)


def _tip(i: int) -> tuple[float, float]:
    a = math.radians(14 + 152 * i / (ARMS - 1))
    return CX + 250 * math.cos(a), CLOAK_TOP + 300 * math.sin(a)


def _cloak(canvas: _Canvas, rng: random.Random) -> None:
    """The web between the arms, hanging open like a cape, its hem scalloped between tips."""
    tips = [_tip(i) for i in range(ARMS)]
    hem = []
    for i, (x, y) in enumerate(tips):
        hem.append((x, y))
        if i < ARMS - 1:
            nx, ny = tips[i + 1]
            mx, my = (x + nx) / 2, (y + ny) / 2
            # The web sags back toward the body between each pair of arms.
            hem.append((mx + (CX - mx) * 0.2, my + (CLOAK_TOP - my) * 0.2))
    body = [(CX + MANTLE_HALF, CLOAK_TOP - 22)] + hem + [(CX - MANTLE_HALF, CLOAK_TOP - 22)]
    canvas.polygon(body, 118, True)

    for i, (tx, ty) in enumerate(tips):
        base = (CX + (i - (ARMS - 1) / 2) * 20, CLOAK_TOP - 6)
        angle = math.atan2(ty - base[1], tx - base[0])
        length = math.hypot(tx - base[0], ty - base[1])
        curl = 0.9 if tx > CX else -0.9
        sway = 0.1 if tx > CX else -0.1
        trail = _stroke(canvas, base, angle - sway, length * 1.01, 2 * sway, lambda t: 4.2 - 1.4 * t, 212)
        end = _stroke(canvas, (tx, ty), angle, 44, curl, lambda t: 2.8 - 1.8 * t, 212, bend_power=1.3, steps=30)
        canvas.dot(*end[-1][:2], 4.5, 255, False)  # photophore at the tip
        # Cirri: soft spines along the arm, on both sides, the "fangs" of the cloak.
        for x, y, heading in trail[12::9]:
            for side in (-1, 1):
                spike = heading + side * rng.uniform(1.1, 1.5)
                _stroke(canvas, (x, y), spike, rng.uniform(9, 14), 0, lambda t: 1.4, 232, steps=8)


def _filaments(canvas: _Canvas) -> None:
    """Two retractile filaments, many times the body's length, drifting below."""
    for side, bend in ((-1, 0.5), (1, -0.45)):
        trail = _stroke(canvas, (CX + side * 12, CLOAK_TOP + 40), math.pi / 2 - side * 0.2, 430, bend,
                        lambda t: 1.9 - 0.6 * t, 248, bend_power=1.8, steps=200)
        canvas.dot(*trail[-1][:2], 3, 255, False)


def _marine_snow(canvas: _Canvas, rng: random.Random) -> None:
    """The drifting organic debris it eats. Kept clear of the body."""
    placed = 0
    while placed < 70:
        x, y = rng.uniform(12, SIZE[0] - 12), rng.uniform(12, SIZE[1] - 12)
        in_body = abs(x - CX) < 270 and CLOAK_TOP - 250 < y < CLOAK_TOP + 330 and abs(x - CX) < 90 + (y - 40) * 0.8
        if in_body:
            continue
        canvas.dot(x, y, rng.uniform(1.4, 2.6), rng.randint(90, 170), False)
        placed += 1


def render() -> tuple[Image.Image, Image.Image]:
    rng = random.Random(SEED)
    canvas = _Canvas()
    _marine_snow(canvas, rng)
    _filaments(canvas)
    _cloak(canvas, rng)
    _mantle(canvas)
    _eyes(canvas)

    lum, alpha, tint = (image.resize(SIZE, Image.LANCZOS) for image in canvas.images)
    return Image.merge("LA", (lum, alpha)).filter(ImageFilter.SMOOTH), tint


if __name__ == "__main__":
    image, tint = render()
    lum = image.getchannel("L")
    red = Image.merge("RGB", (lum, lum.point(lambda v: v * 0.35), lum.point(lambda v: v * 0.4)))
    preview = Image.merge("RGB", (lum, lum, lum))
    preview.paste(red, mask=tint)
    preview.save("squid-preview.png")
