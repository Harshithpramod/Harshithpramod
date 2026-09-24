"""The terminal cards: whoami, the case files, protocols, section headers and links."""

from html import escape

from banner import Fonts, bat_path
from content import PRINCIPLES, STATUS, WHOAMI, Project
from fontpaths import Shaped, text_path
from theme import MONO, SANS, Theme

CARD_W = 860
PAD = 40
MONO_ADVANCE = 0.6  # JetBrains Mono / Menlo advance width, in ems
# Cards are drawn at 860 wide and shown at about half that, so text is sized for 2x.
ROW_SIZE = 19
HOST = "harshith@batcave"


def _path(shape: Shaped, x: float, baseline: float, fill: str) -> str:
    return f'<path transform="translate({x:.1f} {baseline - shape.ascent:.1f})" d="{shape.d}" fill="{fill}"/>'


def _text(x: float, y: float, body: str, fill: str, size: float = 15, family: str = MONO,
          anchor: str = "start", extra: str = "") -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" fill="{fill}" '
        f'text-anchor="{anchor}" xml:space="preserve"{extra}>{body}</text>'
    )


def _svg(width: float, height: float, label: str, body: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
        f'viewBox="0 0 {width:.0f} {height:.0f}" role="img" aria-label="{escape(label)}">{body}</svg>'
    )


def _emblem(theme: Theme, cx: float, cy: float, scale: float = 0.075) -> str:
    return f'<path d="{bat_path(scale, cx, cy)}" fill="{theme.accent}"/>'


def _chrome(theme: Theme, width: int, height: int, title: str, right: str) -> str:
    return (
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="14" fill="{theme.surface}" stroke="{theme.border}"/>'
        f'<line x1="1" y1="44" x2="{width - 1}" y2="44" stroke="{theme.border}"/>'
        + _emblem(theme, 30, 22)
        + _text(46, 27, f'{HOST} <tspan fill="{theme.faint}">·</tspan> {escape(title)}', theme.muted, 12.5)
        + _text(width - 22, 27, escape(right), theme.muted, 12.5, anchor="end")
    )


def _fade_in(delay: float) -> str:
    return (
        f'<animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="{delay:.2f}s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" from="-6 0" to="0 0" dur="0.5s" '
        f'begin="{delay:.2f}s" fill="freeze"/>'
    )


# ---- whoami ----------------------------------------------------------------------------

def _rows(theme: Theme, top: float) -> tuple[list[str], float, float]:
    """The key/value groups, each row fading in after the last. Returns (svg, next y, next delay)."""
    body, y, delay = [], top, 0.35
    for group_index, group in enumerate(WHOAMI):
        body.append(f'<line x1="{PAD}" y1="{y - 22:.0f}" x2="{CARD_W - PAD}" y2="{y - 22:.0f}" stroke="{theme.border}"/>')
        y += 14
        for key, value in group:
            row = _text(PAD, y, escape(key), theme.muted, ROW_SIZE) + _text(PAD + 150, y, escape(value), theme.ink, ROW_SIZE)
            body.append(f'<g opacity="0">{row}{_fade_in(delay)}</g>')
            y += 37
            delay += 0.07
        if group_index < len(WHOAMI) - 1:
            y += 20
    return body, y, delay


def whoami(theme: Theme, fonts: Fonts, footer_left: str, footer_right: str) -> str:
    height = 1000
    name = text_path(fonts.display_bold, "HARSHITH PRAMOD", 60, tracking=0.02)
    body = [
        _chrome(theme, CARD_W, height, "~/whoami", "zsh"),
        _text(PAD, 94, f'<tspan fill="{theme.accent}">$</tspan> whoami', theme.ink, ROW_SIZE),
        _path(name, PAD, 164, theme.ink),
    ]
    rows, y, delay = _rows(theme, 222)
    body.extend(rows)

    y += 16
    status = (
        f'<circle cx="{PAD + 6}" cy="{y - 5:.0f}" r="5" fill="{theme.live}">'
        '<animate attributeName="opacity" values="1;0.35;1" dur="2.4s" repeatCount="indefinite"/></circle>'
        + _text(PAD + 22, y, escape(STATUS), theme.live, ROW_SIZE)
    )
    body.append(f'<g opacity="0">{status}{_fade_in(delay)}</g>')
    prompt_y = y + 44
    dollar = _text(PAD, prompt_y, "$", theme.accent, ROW_SIZE)
    cursor = (
        f'<rect x="{PAD + 22}" y="{prompt_y - 17:.0f}" width="11" height="22" fill="{theme.ink}">'
        '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.1s" repeatCount="indefinite"/></rect>'
    )
    body.append(f'<g opacity="0">{dollar}{cursor}{_fade_in(delay + 0.1)}</g>')

    body.append(f'<line x1="22" y1="{height - 44}" x2="{CARD_W - 22}" y2="{height - 44}" stroke="{theme.border}"/>')
    body.append(_text(22, height - 18, escape(footer_left), theme.muted, 12))
    body.append(_text(CARD_W - 22, height - 18, escape(footer_right), theme.muted, 12, anchor="end"))
    return _svg(CARD_W, height, "Harshith Pramod: Full-stack Developer, full-stack products with applied AI", "".join(body))


# ---- case files ------------------------------------------------------------------------

def _draw_in(path: str, stroke: str, delay: float, width: float = 1.6) -> str:
    """A stroke that draws itself once, then stays."""
    return (
        f'<path d="{path}" fill="none" stroke="{stroke}" stroke-width="{width}" stroke-linecap="round" '
        f'stroke-dasharray="400" stroke-dashoffset="400">'
        f'<animate attributeName="stroke-dashoffset" from="400" to="0" dur="1.4s" begin="{delay:.2f}s" fill="freeze"/></path>'
    )


def _node(x: float, y: float, fill: str, r: float = 5) -> str:
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"/>'


def _diagram(slug: str, theme: Theme) -> str:
    """A small signature drawing per project, about 170 x 90."""
    accent, steel, quiet = theme.accent, theme.steel, theme.muted
    if slug == "pentestai":  # many suspects, one gate, two dismissed, one proven in the sandbox
        suspects = [(0, 8 + i * 13) for i in range(7)]
        body = "".join(_draw_in(f"M{x} {y} L66 45", quiet, 0.4 + i * 0.05, 1.1) for i, (x, y) in enumerate(suspects))
        body += "".join(_node(x, y, quiet, 3) for x, y in suspects)
        body += f'<rect x="66" y="25" width="9" height="40" rx="2" fill="{steel}"/>'
        body += _draw_in("M80 38 L100 16", quiet, 0.9, 1.2) + _draw_in("M80 52 L100 74", quiet, 0.95, 1.2)
        body += "".join(
            f'<path d="M{x - 4} {y - 4} L{x + 4} {y + 4} M{x - 4} {y + 4} L{x + 4} {y - 4}" stroke="{quiet}" stroke-width="1.4"/>'
            for x, y in ((104, 12), (104, 78))
        )
        body += _draw_in("M80 45 L114 45", accent, 1.0)
        body += f'<rect x="114" y="29" width="32" height="32" rx="4" fill="none" stroke="{accent}" stroke-width="1.6" stroke-dasharray="4 3"/>'
        return body + _draw_in("M146 45 L160 45", accent, 1.3) + _node(166, 45, accent, 6)
    if slug == "adforge":  # one photo in; an image ad and a narrated video out
        photo = (
            f'<rect x="0" y="22" width="50" height="46" rx="4" fill="none" stroke="{quiet}" stroke-width="1.4"/>'
            f'<path d="M6 60 L20 42 L30 52 L36 46 L44 60 Z" fill="{quiet}" opacity="0.6"/>'
            f'<circle cx="37" cy="33" r="4" fill="{quiet}" opacity="0.6"/>'
        )
        wires = _draw_in("M54 45 C84 45 84 22 112 22", steel, 0.5, 1.3) + _draw_in("M54 45 C84 45 84 68 112 68", steel, 0.6, 1.3)
        ad = (
            f'<rect x="114" y="4" width="54" height="36" rx="4" fill="none" stroke="{accent}" stroke-width="1.6"/>'
            f'<rect x="121" y="12" width="22" height="3" rx="1" fill="{accent}"/><rect x="121" y="19" width="34" height="3" rx="1" fill="{accent}" opacity="0.5"/>'
            f'<rect x="121" y="28" width="16" height="6" rx="2" fill="{accent}"/>'
        )
        video = (
            f'<rect x="114" y="50" width="54" height="36" rx="4" fill="none" stroke="{accent}" stroke-width="1.6"/>'
            f'<path d="M136 60 L148 68 L136 76 Z" fill="{accent}"/>'
        )
        return photo + wires + ad + video
    # smartpantry: barcode, receipt and voice all feed one walled-off database
    barcode = "".join(f'<rect x="{x}" y="4" width="{w}" height="20" fill="{quiet}"/>' for x, w in ((0, 2), (4, 1), (7, 3), (12, 1), (15, 2), (19, 1), (22, 3), (27, 1)))
    receipt = (
        f'<path d="M2 34 L28 34 L28 58 L24 55 L20 58 L16 55 L12 58 L8 55 L2 58 Z" fill="none" stroke="{quiet}" stroke-width="1.3"/>'
        + "".join(f'<rect x="7" y="{y}" width="{w}" height="2" fill="{quiet}"/>' for y, w in ((39, 16), (44, 12), (49, 14)))
    )
    voice = f'<path d="M0 76 C4 66 8 66 10 76 S16 86 20 76 S26 66 30 76" fill="none" stroke="{quiet}" stroke-width="1.4"/>'
    wires = "".join(_draw_in(f"M36 {y} C80 {y} 80 45 118 45", steel, 0.5 + i * 0.1, 1.3) for i, y in enumerate((14, 46, 76)))
    db = (
        f'<path d="M120 28 L120 66 A24 7 0 0 0 168 66 L168 28" fill="none" stroke="{accent}" stroke-width="1.6"/>'
        f'<ellipse cx="144" cy="28" rx="24" ry="7" fill="none" stroke="{accent}" stroke-width="1.6"/>'
        f'<path d="M120 47 A24 7 0 0 0 168 47" fill="none" stroke="{accent}" stroke-width="1.2" opacity="0.6"/>'
    )
    return barcode + receipt + voice + wires + db


def _chip(x: float, y: float, label: str, theme: Theme) -> tuple[str, float]:
    width = len(label) * 15 * MONO_ADVANCE + 28
    svg = (
        f'<rect x="{x:.1f}" y="{y}" width="{width:.1f}" height="34" rx="17" fill="none" stroke="{theme.border}"/>'
        + _text(x + width / 2, y + 22.5, escape(label), theme.muted, 15, anchor="middle")
    )
    return svg, width


def project(theme: Theme, fonts: Fonts, index: int, p: Project) -> str:
    height = 480
    name = text_path(fonts.display_bold, p.name.upper(), 52, tracking=0.02)
    metric = text_path(fonts.display_bold, p.metric, 72)
    if p.live:
        badge = (
            f'<circle cx="{CARD_W - PAD - 56}" cy="43" r="5" fill="{theme.live}"/>'
            + _text(CARD_W - PAD, 48, "LIVE", theme.live, 14.5, anchor="end", extra=' letter-spacing="2"')
        )
    else:
        badge = _text(CARD_W - PAD, 48, "CASE STUDY", theme.muted, 14.5, anchor="end", extra=' letter-spacing="2"')
    body = [
        f'<rect x="0.5" y="0.5" width="{CARD_W - 1}" height="{height - 1}" rx="14" fill="{theme.surface}" stroke="{theme.border}"/>',
        _text(PAD, 48, f"CASE {index:02d}  ·  {escape(p.kind.upper())}", theme.muted, 14.5, extra=' letter-spacing="1.5"'),
        badge,
        _path(name, PAD, 116, theme.ink),
        _text(PAD, 148, escape(p.context), theme.muted, 16),
        f'<g transform="translate({CARD_W - PAD - 172} 72)">{_diagram(p.slug, theme)}</g>',
    ]
    body += [_text(PAD, 196 + i * 31, escape(line), theme.ink, 22, SANS, extra=' opacity="0.86"') for i, line in enumerate(p.lines)]
    body.append(f'<line x1="{PAD}" y1="296" x2="{CARD_W - PAD}" y2="296" stroke="{theme.border}"/>')
    body.append(_path(metric, PAD, 374, theme.accent))
    label_x = PAD + metric.width + 24
    body += [_text(label_x, 342 + i * 27, escape(line), theme.muted, 19, SANS) for i, line in enumerate(p.metric_label)]
    x = PAD
    for label in p.stack:
        chip, width = _chip(x, 408, label, theme)
        body.append(chip)
        x += width + 10
    return _svg(CARD_W, height, f"{p.name}: {p.kind}", "".join(body))


# ---- protocols, headers, links --------------------------------------------------------

WIDE = 1740


def principles(theme: Theme, fonts: Fonts) -> str:
    height = 230
    column = (WIDE - 2 * PAD) / 3
    body = [f'<rect x="0.5" y="0.5" width="{WIDE - 1}" height="{height - 1}" rx="14" fill="{theme.surface}" stroke="{theme.border}"/>']
    for i, (title, evidence) in enumerate(PRINCIPLES):
        x = PAD + i * column + (28 if i else 0)
        if i:
            body.append(f'<line x1="{x - 28:.0f}" y1="40" x2="{x - 28:.0f}" y2="{height - 40}" stroke="{theme.border}"/>')
        numeral = text_path(fonts.display_bold, ("I", "II", "III")[i], 48)
        heading = text_path(fonts.display_bold, title.upper(), 42, tracking=0.02)
        group = (
            _path(numeral, x, 104, theme.accent) + _path(heading, x + 58, 102, theme.ink)
            + _text(x, 164, escape(evidence), theme.muted, 23, SANS)
        )
        body.append(f'<g opacity="0">{group}{_fade_in(0.3 + i * 0.25)}</g>')
    return _svg(WIDE, height, "How I build: " + "; ".join(t for t, _ in PRINCIPLES), "".join(body))


def header(theme: Theme, command: str) -> str:
    height, size = 70, 26
    prompt = f"{HOST} ~ $ "
    text_end = (len(prompt) + len(command)) * size * MONO_ADVANCE
    body = (
        _text(0, 44, f'<tspan fill="{theme.muted}">{HOST}</tspan> <tspan fill="{theme.accent}">~ $</tspan> '
              f'{escape(command)}', theme.ink, size)
        + f'<line x1="{text_end + 28:.0f}" y1="36" x2="{WIDE - 70}" y2="36" stroke="{theme.border}"/>'
        + _emblem(theme, WIDE - 30, 36, 0.2)
    )
    return _svg(WIDE, height, f"$ {command}", body)


def link_button(theme: Theme, label: str) -> str:
    width, height = 300, 72
    body = (
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="36" fill="{theme.surface}" stroke="{theme.border}"/>'
        + _text(34, 45, escape(label), theme.ink, 21, SANS)
        + _text(width - 32, 45, "↗", theme.accent, 22, SANS, anchor="end")
    )
    return _svg(width, height, label, body)
