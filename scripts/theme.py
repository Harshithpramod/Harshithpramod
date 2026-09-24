"""One palette per GitHub theme. Gotham at night: soot, rain-grey, and the signal's yellow."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    name: str
    page: str      # GitHub's own background, so cards sit flush
    surface: str   # card fill
    border: str
    ink: str       # primary text
    muted: str     # labels, secondary text
    faint: str     # rules, the sparsest ASCII tone
    accent: str    # the bat-signal: prompts, metrics, highlights
    steel: str     # cold rain-blue, the second voice in diagrams
    live: str      # "online" dot
    bloom: str     # the signal behind the gargoyle


DARK = Theme(
    name="dark",
    page="#0d1117",
    surface="#0a0c10",
    border="#1f242d",
    ink="#e9e6dc",
    muted="#7c8290",
    faint="#2a2f38",
    accent="#f5c518",
    steel="#7f9cc2",
    live="#6fd3a1",
    bloom="#f5c518",
)

LIGHT = Theme(
    name="light",
    page="#ffffff",
    surface="#fbfbf9",
    border="#e4e4df",
    ink="#15171c",
    muted="#666a74",
    faint="#d6d7da",
    accent="#a67a00",
    steel="#3f5f8a",
    live="#1f8f5f",
    bloom="#a67a00",
)

THEMES = (DARK, LIGHT)

MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"


def mix(a: str, b: str, t: float) -> str:
    """Blend two hex colours; t=0 gives a, t=1 gives b."""
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(ca, cb))
