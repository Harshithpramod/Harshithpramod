"""The header: Gotham after midnight. Rain, the signal on the clouds, and someone watching it.

Original vector art. Motion stays slow and rare on purpose: the rain is constant,
lightning comes once every thirteen seconds, and the bats only now and then.
"""

import math
import random
from dataclasses import dataclass

from fontpaths import FontRef, Shaped, text_path

W, H = 1280, 440
SEED = 27

SPOT = (858, 118, 124, 64)   # the signal on the clouds: cx, cy, rx, ry
LAMP = (1168, 336)           # the searchlight on the GCPD roof
PERCH = (1004, 262)          # where he crouches, on the ledge, inside the beam
SKY = ("#040507", "#090c11", "#15171a")
FAR = "#0c0f14"
NEAR = "#050608"
SIGNAL = "#f5c518"
SODIUM = "#e8b14a"           # street-lamp orange in the windows
PAPER = "#ece9df"
STEEL = "#8fa6c6"


@dataclass(frozen=True)
class Fonts:
    display: FontRef
    display_bold: FontRef
    italic: FontRef
    sans: FontRef
    sans_medium: FontRef
    mono: FontRef


def bat_path(scale: float = 1.0, cx: float = 0.0, cy: float = 0.0) -> str:
    """The emblem, angular, built from its right half and mirrored. 200 wide at scale 1."""
    half = (
        (0, -16), (6, -16), (10, -34), (14, -14), (24, -12), (46, -20), (72, -32), (100, -44),
        (88, -6), (76, -14), (66, 8), (54, -2), (42, 18), (30, 8), (16, 26), (0, 46),
    )
    points = list(half) + [(-x, y) for x, y in reversed(half[1:-1])]
    return "M" + " L".join(f"{cx + x * scale:.1f} {cy + y * scale:.1f}" for x, y in points) + " Z"


def _clouds(rng: random.Random) -> str:
    """Low, heavy cloud: dark masses with their undersides lit by the city."""
    out = []
    for cy, width, dur, fill, opacity in (
        (60, 900, 190, "#1c2129", 0.55), (128, 700, 150, "#232833", 0.45),
        (196, 820, 230, "#2a2a2a", 0.30), (104, 520, 120, "#303744", 0.35),
    ):
        cx = rng.uniform(520, 980)
        puffs = "".join(
            f'<ellipse cx="{cx + rng.uniform(-width / 2, width / 2):.0f}" cy="{cy + rng.uniform(-10, 10):.0f}" '
            f'rx="{rng.uniform(80, 170):.0f}" ry="{rng.uniform(14, 26):.0f}"/>'
            for _ in range(8)
        )
        out.append(
            f'<g fill="{fill}" opacity="{opacity}" filter="url(#cloud)">{puffs}'
            f'<animateTransform attributeName="transform" type="translate" values="-260 0;260 0;-260 0" '
            f'dur="{dur}s" begin="-{rng.uniform(0, dur):.0f}s" repeatCount="indefinite"/></g>'
        )
    return "".join(out)


def _signal() -> str:
    """The spot on the clouds and the bat inside it. The old lamp flickers, faintly."""
    cx, cy, rx, ry = SPOT
    flicker = (
        '<animate attributeName="opacity" values="1;0.86;1;1;0.92;1" keyTimes="0;0.04;0.08;0.6;0.63;1" '
        'dur="7s" repeatCount="indefinite"/>'
    )
    return (
        f'<g>{flicker}'
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx * 2.1:.0f}" ry="{ry * 2.4:.0f}" fill="url(#spotHalo)"/>'
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#spot)" filter="url(#soft)"/>'
        f'<path d="{bat_path(0.9, cx, cy - 2)}" fill="#07080a" opacity="0.88" filter="url(#softer)"/>'
        '</g>'
    )


def _beam() -> str:
    """From the lamp to the spot, its edges tangent to the ellipse."""
    lx, ly = LAMP
    cx, cy, rx, ry = SPOT
    rim = [(cx + rx * math.cos(a / 90 * math.pi), cy + ry * math.sin(a / 90 * math.pi)) for a in range(180)]
    bearing = lambda p: math.atan2(p[1] - ly, p[0] - lx)
    upper, lower = max(rim, key=bearing), min(rim, key=bearing)
    shape = f"M{lx - 6} {ly - 6} L{upper[0]:.0f} {upper[1]:.0f} L{lower[0]:.0f} {lower[1]:.0f} L{lx + 6} {ly + 5} Z"
    return f'<path d="{shape}" fill="url(#beam)"/>'


def _tower(x: float, w: float, top: float, style: str) -> str:
    """One Gotham silhouette: flat, stepped art-deco, needle spire, or gothic pinnacles."""
    body = f'<rect x="{x:.0f}" y="{top:.0f}" width="{w + 1:.0f}" height="{H - top:.0f}"/>'
    if style == "setback":
        return body + (
            f'<rect x="{x + w * 0.14:.0f}" y="{top - 22:.0f}" width="{w * 0.72:.0f}" height="23"/>'
            f'<rect x="{x + w * 0.3:.0f}" y="{top - 40:.0f}" width="{w * 0.4:.0f}" height="19"/>'
        )
    if style == "spire":
        mid = x + w / 2
        return body + (
            f'<rect x="{x + w * 0.2:.0f}" y="{top - 26:.0f}" width="{w * 0.6:.0f}" height="27"/>'
            f'<path d="M{mid - w * 0.14:.1f} {top - 26:.0f} L{mid:.1f} {top - 96:.0f} L{mid + w * 0.14:.1f} {top - 26:.0f} Z"/>'
        )
    if style == "gothic":
        peaks = "".join(
            f'<path d="M{px - 5:.1f} {top:.0f} L{px:.1f} {top - 24:.0f} L{px + 5:.1f} {top:.0f} Z"/>'
            for px in (x + 5, x + w - 5)
        )
        return body + peaks + f'<path d="M{x + 8:.0f} {top:.0f} L{x + w / 2:.0f} {top - 38:.0f} L{x + w - 8:.0f} {top:.0f} Z"/>'
    return body


def _skyline(rng: random.Random) -> tuple[str, str]:
    """Far towers (behind the beam) and the near roofs (in front of it). The left stays low
    so it never crowds the name."""
    far, windows = [], []
    styles = ("flat", "setback", "setback", "spire", "gothic")
    x = 0.0
    while x < W:
        w = rng.uniform(40, 96)
        top = rng.uniform(362, 398) if x < 600 else rng.uniform(210, 320)
        far.append(_tower(x, w, top, rng.choice(styles) if x > 560 else "flat"))
        for _ in range(rng.randint(2, 7) if x > 560 else rng.randint(0, 2)):
            wx, wy = x + rng.uniform(5, w - 8), top + rng.uniform(10, H - top - 10)
            colour = SODIUM if rng.random() < 0.8 else STEEL
            windows.append(
                f'<rect x="{wx:.0f}" y="{wy:.0f}" width="3" height="5" fill="{colour}" opacity="{rng.uniform(0.3, 0.75):.2f}"/>'
            )
        x += w
    # One window goes dark and comes back, as if someone's still up.
    windows.append(
        f'<rect x="1086" y="268" width="3" height="5" fill="{SODIUM}" opacity="0.8">'
        '<animate attributeName="opacity" values="0.8;0.8;0.05;0.05;0.8" keyTimes="0;0.4;0.42;0.8;0.82" dur="17s" repeatCount="indefinite"/></rect>'
    )

    px, py = PERCH
    lx, ly = LAMP
    near = [
        _tower(0, 90, 412, "flat"), _tower(90, 140, 420, "flat"), _tower(230, 120, 408, "flat"),
        _tower(350, 170, 418, "flat"), _tower(520, 130, 404, "flat"), _tower(650, 120, 396, "flat"),
        _tower(770, 150, 384, "setback"),
        # His building, with the ledge he crouches on.
        f'<rect x="{px - 16}" y="{py}" width="112" height="{H - py}"/>',
        f'<rect x="{px - 30}" y="{py - 2}" width="44" height="7"/>',
        f'<path d="M{px - 30} {py + 5} L{px - 22} {py + 16} L{px - 10} {py + 5} Z"/>',
        _tower(px + 96, 70, 340, "flat"),
        # The GCPD roof and its searchlight.
        f'<rect x="{lx - 64}" y="{ly + 14}" width="{W - lx + 64}" height="{H - ly}"/>',
        f'<rect x="{lx - 3}" y="{ly}" width="6" height="16"/>',
        f'<g transform="rotate(-36 {lx} {ly})"><rect x="{lx - 13}" y="{ly - 10}" width="26" height="20" rx="3"/></g>',
    ]
    lamp_glow = f'<circle cx="{lx - 6}" cy="{ly - 6}" r="7" fill="{SIGNAL}" opacity="0.9" filter="url(#glow)"/>'
    return (
        f'<g fill="{FAR}">{"".join(far)}</g>{"".join(windows)}',
        f'<g fill="{NEAR}">{"".join(near)}</g>{lamp_glow}',
    )


def _knight() -> str:
    """Crouched on the ledge, seen from behind, cape moving in the wind. The beam's edge
    catches his left side."""
    px, py = PERCH
    cape_a = "M-12 -50 C-22 -38 -30 -18 -36 2 Q-27 -8 -18 3 Q-9 -8 0 4 Q9 -8 18 3 Q27 -8 36 2 C30 -18 22 -38 12 -50 Z"
    cape_b = "M-12 -50 C-24 -38 -33 -18 -40 4 Q-30 -7 -20 4 Q-10 -9 1 5 Q10 -7 19 2 Q27 -9 35 0 C29 -18 22 -38 12 -50 Z"
    head = "M-9 -48 C-12 -56 -11 -63 -8 -66 L-7 -80 L-3 -67 L3 -67 L7 -80 L8 -66 C11 -63 12 -56 9 -48 Z"
    rim = "M-12 -50 C-22 -38 -30 -18 -36 2"
    spline = 'calcMode="spline" keyTimes="0;0.5;1" keySplines="0.45 0 0.55 1;0.45 0 0.55 1"'
    return f'''
<g transform="translate({px - 8} {py - 1})">
  <path d="{cape_a}" fill="{NEAR}"><animate attributeName="d" values="{cape_a};{cape_b};{cape_a}" dur="5s" repeatCount="indefinite" {spline}/></path>
  <path d="{head}" fill="{NEAR}"/>
  <path d="{rim}" fill="none" stroke="{SIGNAL}" stroke-opacity="0.35" stroke-width="1.2"/>
  <path d="M-7 -80 L-8 -66 C-11 -63 -12 -56 -9 -48" fill="none" stroke="{SIGNAL}" stroke-opacity="0.45" stroke-width="1"/>
</g>'''


def _rain(rng: random.Random) -> str:
    out = []
    for _ in range(90):
        x = rng.uniform(-40, W + 60)
        length = rng.uniform(12, 26)
        dur = rng.uniform(0.7, 1.3)
        out.append(
            f'<line x1="{x:.0f}" y1="-30" x2="{x - length * 0.22:.1f}" y2="{-30 + length:.0f}" '
            f'stroke="#a9b6c8" stroke-opacity="{rng.uniform(0.1, 0.3):.2f}" stroke-width="1">'
            f'<animateTransform attributeName="transform" type="translate" values="0 0;-104 {H + 60}" '
            f'dur="{dur:.2f}s" begin="-{rng.uniform(0, dur):.2f}s" repeatCount="indefinite"/></line>'
        )
    return "".join(out)


def _lightning() -> str:
    """Rare and brief: the sky whitens twice and a bolt stands behind the towers."""
    times = 'keyTimes="0;0.70;0.705;0.715;0.725;0.75;1"'
    bolt = "M612 0 L598 52 L620 58 L590 128 L610 132 L584 214 L604 218 L592 300"
    return f'''
<rect width="{W}" height="{H}" fill="#d6defa" opacity="0">
  <animate attributeName="opacity" values="0;0;0.14;0.02;0.1;0;0" {times} dur="13s" begin="4s" repeatCount="indefinite"/>
</rect>
<path d="{bolt}" fill="none" stroke="#eef2ff" stroke-width="1.8" opacity="0" filter="url(#glow)">
  <animate attributeName="opacity" values="0;0;1;0.1;0.8;0;0" {times} dur="13s" begin="4s" repeatCount="indefinite"/>
</path>'''


def _bats(rng: random.Random) -> str:
    """A few bats leave the signal now and then, flapping off to the left."""
    out = []
    for i in range(5):
        sx, sy = rng.uniform(780, 900), rng.uniform(150, 200)
        ex, ey = sx - rng.uniform(380, 560), sy - rng.uniform(40, 110)
        scale = rng.uniform(0.07, 0.11)
        begin = 6 + i * 0.5
        flap = rng.uniform(0.22, 0.32)
        out.append(
            f'<g opacity="0">'
            f'<animateTransform attributeName="transform" type="translate" values="{sx:.0f} {sy:.0f};{ex:.0f} {ey:.0f};{ex:.0f} {ey:.0f}" '
            f'keyTimes="0;0.35;1" dur="19s" begin="{begin:.1f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;0.9;0.9;0;0" keyTimes="0;0.03;0.28;0.35;1" dur="19s" begin="{begin:.1f}s" repeatCount="indefinite"/>'
            f'<g><path d="{bat_path(scale)}" fill="#0b0c0f"/>'
            f'<animateTransform attributeName="transform" type="scale" values="1 1;1 0.25;1 1" dur="{flap:.2f}s" repeatCount="indefinite"/></g>'
            '</g>'
        )
    return "".join(out)


def _placed(shape: Shaped, x: float, y: float, fill: str, opacity: float = 1.0) -> str:
    return f'<path transform="translate({x:.1f} {y:.1f})" d="{shape.d}" fill="{fill}" opacity="{opacity}"/>'


def _on_baseline(shape: Shaped, x: float, baseline: float, fill: str) -> str:
    return _placed(shape, x, baseline - shape.ascent, fill)


def _type(fonts: Fonts) -> str:
    x = 84
    label = text_path(fonts.mono, "BENGALURU  ·  INDIA", 12.5, tracking=0.28)
    name = text_path(fonts.display_bold, "HARSHITH PRAMOD", 84, tracking=0.02)
    role = text_path(fonts.sans_medium, "Full-stack Developer", 23)
    focus = text_path(fonts.sans, "React · Next.js · Supabase · applied AI", 23)
    motto = text_path(fonts.italic, "I build full-stack products, with AI where it earns its place.", 17.5)
    return "".join((
        _on_baseline(label, x, 104, "#8a8f9c"),
        _on_baseline(name, x, 190, PAPER),
        f'<path d="{bat_path(0.2, x + 20, 224)}" fill="{SIGNAL}"/>',
        _on_baseline(role, x, 272, PAPER),
        _on_baseline(focus, x, 304, STEEL),
        _on_baseline(motto, x, 350, "#9c9fa8"),
    ))


def render(fonts: Fonts) -> str:
    rng = random.Random(SEED)
    far, near = _skyline(rng)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Harshith Pramod, Full-stack Developer. The bat-signal on the clouds over a rainy Gotham skyline, watched from a ledge.">
<defs>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="16"/></clipPath>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{SKY[0]}"/><stop offset="0.6" stop-color="{SKY[1]}"/><stop offset="1" stop-color="{SKY[2]}"/>
  </linearGradient>
  <radialGradient id="smog" cx="0.72" cy="1" r="0.6"><stop offset="0" stop-color="#c9822e" stop-opacity="0.22"/><stop offset="1" stop-color="#c9822e" stop-opacity="0"/></radialGradient>
  <radialGradient id="spot"><stop offset="0" stop-color="#fff1b0" stop-opacity="0.95"/><stop offset="0.6" stop-color="{SIGNAL}" stop-opacity="0.75"/><stop offset="1" stop-color="{SIGNAL}" stop-opacity="0.25"/></radialGradient>
  <radialGradient id="spotHalo"><stop offset="0" stop-color="{SIGNAL}" stop-opacity="0.16"/><stop offset="1" stop-color="{SIGNAL}" stop-opacity="0"/></radialGradient>
  <linearGradient id="beam" gradientUnits="userSpaceOnUse" x1="{LAMP[0]}" y1="{LAMP[1]}" x2="{SPOT[0]}" y2="{SPOT[1]}">
    <stop offset="0" stop-color="#fff3c0" stop-opacity="0.42"/><stop offset="0.7" stop-color="{SIGNAL}" stop-opacity="0.12"/><stop offset="1" stop-color="{SIGNAL}" stop-opacity="0"/>
  </linearGradient>
  <radialGradient id="vignette" cx="0.5" cy="0.45" r="0.75"><stop offset="0.6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="0.5"/></radialGradient>
  <filter id="cloud" x="-30%" y="-300%" width="160%" height="700%"><feGaussianBlur stdDeviation="10"/></filter>
  <filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="5"/></filter>
  <filter id="softer" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="1.4"/></filter>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="url(#sky)"/>
  <rect width="{W}" height="{H}" fill="url(#smog)"/>
  {_signal()}
  {_clouds(rng)}
  {_lightning()}
  {_bats(rng)}
  {far}
  {_beam()}
  {near}
  {_knight()}
  {_rain(rng)}
  <rect width="{W}" height="{H}" fill="url(#vignette)"/>
  {_type(fonts)}
</g>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="16" fill="none" stroke="#1f242d"/>
</svg>'''
