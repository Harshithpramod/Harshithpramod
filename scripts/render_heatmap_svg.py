#!/usr/bin/env python3
"""
render_heatmap_svg.py — draw data/contributions.json as the classic
53-week x 7-day calendar, revealed once with a diagonal slide-down.

Usage:
    python scripts/render_heatmap_svg.py
    STATIC=1 python scripts/render_heatmap_svg.py     # frozen frame

Output:
    contrib-heatmap.svg

The reveal is a CSS keyframe with a per-box animation-delay. It plays on
load and freezes (animation-fill-mode: both) — no looping glow, which reads
as a broken GIF on a profile.
"""

import json
import os
from datetime import date
from pathlib import Path

SRC = Path("data/contributions.json")
OUT = "contrib-heatmap.svg"
STATIC = os.environ.get("STATIC") == "1"

# ---------------------------------------------------------------- geometry --
BOX = 12.0
GAP = 3.2
CELL = BOX + GAP
LEFT = 34.0          # room for Mon / Wed / Fri labels
TOP = 22.0           # room for month labels
PAD = 12.0
RADIUS = 2.6

# none -> brightest. Level 5 is a neon top end for your best days.
PALETTE_DARK = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
PALETTE_LIGHT = ["#ebedf0", "#aceebb", "#4ac26b", "#2da44e", "#116329", "#033a16"]

TEXT_DARK = "#8b949e"
TEXT_LIGHT = "#59636e"

STEP = 0.012         # seconds added per diagonal step
DUR = 0.45
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
# ---------------------------------------------------------------------------


def build(data: dict) -> str:
    days = data["days"]
    best = max(1, data["best_day"]["count"])

    # Bucket every day into (week index, weekday index).
    first = date.fromisoformat(days[0]["date"])
    start = first.toordinal() - first.weekday() - 1  # back up to a Sunday
    if date.fromordinal(start + 1).weekday() != 6:
        start = first.toordinal() - ((first.weekday() + 1) % 7)

    cells = []
    for d in days:
        dt = date.fromisoformat(d["date"])
        offset = dt.toordinal() - start
        week, dow = divmod(offset, 7)
        level = d["level"]
        if level >= 4 and d["count"] >= best * 0.8:
            level = 5
        cells.append((week, dow, level, d))

    weeks = max(c[0] for c in cells) + 1
    grid_w = weeks * CELL - GAP
    w = LEFT + grid_w + PAD
    h = TOP + 7 * CELL - GAP + 46

    anim = "" if STATIC else " animation: pop var(--d) ease-out both;"
    css = [
        "<style>",
        "  text { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "
        '"DejaVu Sans Mono", monospace; font-size: 10px; fill: ' + TEXT_DARK + "; }",
        f"  rect.d {{ rx: {RADIUS}px;{anim} }}",
    ]
    for i, c in enumerate(PALETTE_DARK):
        css.append(f"  .l{i} {{ fill: {c}; }}")
    css.append("  @media (prefers-color-scheme: light) {")
    css.append(f"    text {{ fill: {TEXT_LIGHT}; }}")
    for i, c in enumerate(PALETTE_LIGHT):
        css.append(f"    .l{i} {{ fill: {c}; }}")
    css.append("  }")
    if not STATIC:
        css.append(
            "  @keyframes pop { from { opacity: 0; transform: translateY(-7px) "
            "scale(.72); } to { opacity: 1; transform: none; } }"
        )
        css.append("  @media (prefers-reduced-motion: reduce) { rect.d { animation: none; } }")
    css.append("</style>")

    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" '
        f'viewBox="0 0 {w:.0f} {h:.0f}" role="img" '
        f'aria-label="{data["total"]} contributions in the last year">',
        "\n".join(css),
    ]

    # month labels
    seen = set()
    for week, dow, _lvl, d in cells:
        month = d["date"][:7]
        if month in seen or dow > 3:
            continue
        seen.add(month)
        mi = int(d["date"][5:7]) - 1
        p.append(
            f'<text x="{LEFT + week * CELL:.1f}" y="{TOP - 8:.1f}">{MONTHS[mi]}</text>'
        )

    # weekday labels
    for dow, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        y = TOP + dow * CELL + BOX * 0.8
        p.append(f'<text x="0" y="{y:.1f}">{label}</text>')

    # the grid
    for week, dow, level, d in cells:
        x = LEFT + week * CELL
        y = TOP + dow * CELL
        delay = (week + dow) * STEP
        style = "" if STATIC else f' style="--d:{DUR}s;animation-delay:{delay:.2f}s"'
        p.append(
            f'<rect class="d l{level}" x="{x:.1f}" y="{y:.1f}" '
            f'width="{BOX}" height="{BOX}"{style}>'
            f'<title>{d["count"]} on {d["date"]}</title></rect>'
        )

    # footer: stats on the left, legend on the right
    fy = TOP + 7 * CELL + 18
    p.append(
        f'<text x="0" y="{fy:.1f}">'
        f'{data["total"]:,} contributions in the last year  ·  '
        f'{data["active_days"]} active days  ·  '
        f'current streak {data["current_streak"]}  ·  '
        f'longest {data["longest_streak"]}</text>'
    )

    lx = w - PAD - (6 * CELL + 62)
    p.append(f'<text x="{lx:.1f}" y="{fy:.1f}">Less</text>')
    for i in range(6):
        p.append(
            f'<rect class="d l{i}" x="{lx + 30 + i * CELL:.1f}" y="{fy - 9:.1f}" '
            f'width="{BOX}" height="{BOX}"/>'
        )
    p.append(f'<text x="{lx + 30 + 6 * CELL + 4:.1f}" y="{fy:.1f}">More</text>')

    p.append("</svg>")
    return "\n".join(p)


if __name__ == "__main__":
    if not SRC.exists():
        raise SystemExit("data/contributions.json missing — run fetch_contributions.py first")
    payload = json.loads(SRC.read_text(encoding="utf-8"))
    Path(OUT).write_text(build(payload), encoding="utf-8")
    print(f"wrote {OUT}  ({payload['total']} contributions, static={STATIC})")
