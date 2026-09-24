"""Paint Senbonzakura in code, as the source for the ASCII card.

Byakuya's katana, the moment after "Chire": the blade drawn in fine lines up to where it
comes apart, and from there a thousand cherry-blossom petals streaming up and curling
over the top of the card. Petals are the only colour; everything else stays thin.

Returns (image, tint): an LA image whose alpha marks what is drawn and whose luminance
becomes glyph density, and an L mask marking the petals.
"""

import math
import random

from PIL import Image, ImageDraw, ImageFilter

SIZE = (600, 776)
SUPERSAMPLE = 3
SEED = 1000

GUARD = (184, 604)         # where the blade leaves the tsuba
BREAK = 0.62               # fraction of the blade still intact
BLADE_LEN = 420
ANGLE = math.radians(-64)  # up and to the right
HILT_LEN = 150
# The petal streams, as cubic Béziers starting where the blade gives way.
STREAMS = (
    (((0, 0), (110, -160), (60, -270), (-190, -235)), 290, 1.0),
    (((0, 0), (150, -40), (210, 150), (150, 270)), 110, 0.6),
)


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

    def polygon(self, points, lum: int, tinted: bool = False) -> None:
        scaled = [(x * SUPERSAMPLE, y * SUPERSAMPLE) for x, y in points]
        self.lum.polygon(scaled, fill=lum)
        self.alpha.polygon(scaled, fill=255)
        self.tint.polygon(scaled, fill=255 if tinted else 0)

    def line(self, points, r: float, lum: int) -> None:
        for (x0, y0), (x1, y1) in zip(points, points[1:]):
            steps = max(1, int(math.hypot(x1 - x0, y1 - y0) / 1.2))
            for i in range(steps + 1):
                self.dot(x0 + (x1 - x0) * i / steps, y0 + (y1 - y0) * i / steps, r, lum)


def _along(t: float, offset: float = 0.0) -> tuple[float, float]:
    """A point on the sword's axis (t in blade lengths from the guard; negative is the hilt),
    moved `offset` across it. The blade carries a slight curve."""
    ax, ay = math.cos(ANGLE), math.sin(ANGLE)
    nx, ny = -ay, ax
    sori = 14 * max(0.0, t) ** 2  # the curve, strongest toward the tip
    return (GUARD[0] + ax * BLADE_LEN * t + nx * (offset - sori),
            GUARD[1] + ay * BLADE_LEN * t + ny * (offset - sori))


def _blade(canvas: _Canvas, rng: random.Random) -> None:
    """Spine, edge and a wavy hamon, in fine lines, up to where it breaks into shards."""
    ts = [i / 200 * BREAK for i in range(201)]
    canvas.polygon([_along(t, -13) for t in ts] + [_along(t, 11) for t in reversed(ts)], 92)
    canvas.line([_along(t, -13) for t in ts], 2.2, 200)
    canvas.line([_along(t, 11) for t in ts], 2.4, 252)
    canvas.polygon([_along(t, 3 + 2.4 * math.sin(t * 60)) for t in ts[4:]] + [_along(t, 11) for t in reversed(ts[4:])], 178)
    # Where it comes apart: slivers of steel, turning over as they go.
    for i in range(18):
        t = BREAK + rng.uniform(0.0, 0.16)
        x, y = _along(t, rng.uniform(-18, 18))
        a = ANGLE + rng.uniform(-1.2, 1.2)
        length = rng.uniform(9, 18) * (1.2 - (t - BREAK) * 4)
        canvas.line([(x, y), (x + length * math.cos(a), y + length * math.sin(a))], 1.8, 235)


def _hilt(canvas: _Canvas) -> None:
    """Tsuba, habaki, and the wrapped grip with its diamond pattern, all in outline."""
    ax, ay = math.cos(ANGLE), math.sin(ANGLE)
    nx, ny = -ay, ax
    gx, gy = GUARD
    tsuba = [(gx + nx * 46 * math.cos(a) + ax * 8 * math.sin(a), gy + ny * 46 * math.cos(a) + ay * 8 * math.sin(a))
             for a in (i / 48 * math.tau for i in range(49))]
    canvas.polygon(tsuba, 110)
    canvas.line(tsuba, 2.2, 225)
    canvas.polygon([_along(0.0, -14), _along(0.06, -14), _along(0.06, 12), _along(0.0, 12)], 215)  # habaki

    end = -HILT_LEN / BLADE_LEN
    grip = [_along(end * i / 40, -16) for i in range(41)] + [_along(end * i / 40, 16) for i in range(40, -1, -1)]
    canvas.polygon(grip, 70)
    canvas.line(grip, 2.0, 205)
    wraps = 9
    for k in range(wraps):
        a0, a1 = end * (k + 0.1) / wraps, end * (k + 0.9) / wraps
        canvas.line([_along(a0, -16), _along(a1, 16)], 2.2, 218)
        canvas.line([_along(a0, 16), _along(a1, -16)], 2.2, 218)
    canvas.polygon([_along(end, -17), _along(end - 0.04, -15), _along(end - 0.04, 15), _along(end, 17)], 215)  # kashira


def _petal(canvas: _Canvas, x: float, y: float, size: float, angle: float, lum: int) -> None:
    """One sakura petal: an oval with the notch at its tip."""
    points = []
    for i in range(24):
        a = i / 24 * math.tau
        notch = 1 - 0.45 * math.exp(-((a if a < math.pi else a - math.tau) / 0.32) ** 2)
        px, py = size * 0.5 * (1 + math.cos(a)) * notch, size * 0.34 * math.sin(a)
        points.append((x + px * math.cos(angle) - py * math.sin(angle), y + px * math.sin(angle) + py * math.cos(angle)))
    canvas.polygon(points, lum, tinted=True)


def _bezier(p, t: float) -> tuple[float, float]:
    u = 1 - t
    return tuple(u**3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t**3 * d for a, b, c, d in zip(*p))


def _streams(canvas: _Canvas, rng: random.Random) -> None:
    """Dense and large at the blade, spreading and thinning as the stream runs out."""
    ox, oy = _along(BREAK + 0.05)
    for curve, count, scale in STREAMS:
        points = [(ox + x, oy + y) for x, y in curve]
        for _ in range(count):
            t = rng.random() ** 1.3
            cx, cy = _bezier(points, t)
            spread = (10 + 70 * t) * scale
            x, y = cx + rng.gauss(0, spread), cy + rng.gauss(0, spread * 0.8)
            size = (30 - 12 * t) * rng.uniform(0.75, 1.2) * (0.8 + 0.2 * scale)
            _petal(canvas, x, y, size, rng.uniform(0, math.tau), rng.randint(215, 255))
    # A few strays, drifting down through the empty space.
    for _ in range(18):
        _petal(canvas, rng.uniform(20, 580), rng.uniform(300, 760), rng.uniform(15, 21), rng.uniform(0, math.tau),
               rng.randint(190, 240))


def render() -> tuple[Image.Image, Image.Image]:
    rng = random.Random(SEED)
    canvas = _Canvas()
    _hilt(canvas)
    _blade(canvas, rng)
    _streams(canvas, rng)

    lum, alpha, tint = (image.resize(SIZE, Image.LANCZOS) for image in canvas.images)
    return Image.merge("LA", (lum, alpha)).filter(ImageFilter.SMOOTH), tint


if __name__ == "__main__":
    image, tint = render()
    lum = image.getchannel("L")
    pink = Image.merge("RGB", (lum, lum.point(lambda v: v * 0.62), lum.point(lambda v: v * 0.72)))
    preview = Image.merge("RGB", (lum, lum, lum))
    preview.paste(pink, mask=tint)
    preview.save("senbonzakura-preview.png")
