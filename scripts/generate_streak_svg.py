import json
from pathlib import Path


# ============================================================
# FILES
# ============================================================

INPUT_FILE = Path(
    "data/contributions.json"
)

OUTPUT_FILE = Path(
    "contrib-heatmap.svg"
)


# ============================================================
# SVG SETTINGS
# ============================================================

WIDTH = 860
HEIGHT = 190

CELL_SIZE = 11
GAP = 4

LEFT = 25
TOP = 35


# GitHub-style contribution colors
PALETTE = [
    "#161b22",  # 0
    "#0e4429",  # 1
    "#006d32",  # 2
    "#26a641",  # 3
    "#39d353"   # 4
]


# ============================================================
# LOAD JSON
# ============================================================

def load_data():

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"{INPUT_FILE} does not exist.\n"
            "Run fetch_contributions.py first."
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# COLOR
# ============================================================

def get_color(level):

    level = max(
        0,
        min(
            level,
            len(PALETTE) - 1
        )
    )

    return PALETTE[level]


# ============================================================
# CREATE CELLS
# ============================================================

def create_cells(days):

    cells = []

    # We only need approximately one year
    # of contribution data.
    days = days[-371:]

    for index, day in enumerate(days):

        # 7 days per column
        week = index // 7

        weekday = index % 7

        x = (
            LEFT
            + week * (
                CELL_SIZE + GAP
            )
        )

        y = (
            TOP
            + weekday * (
                CELL_SIZE + GAP
            )
        )

        color = get_color(
            day["level"]
        )

        # Diagonal animation
        delay = (
            week * 0.025
            + weekday * 0.015
        )

        cell = f"""
        <rect
            x="{x}"
            y="{y}"
            width="{CELL_SIZE}"
            height="{CELL_SIZE}"
            rx="2"
            fill="{color}"
            opacity="0">

            <animate
                attributeName="opacity"
                from="0"
                to="1"
                dur="0.25s"
                begin="{delay:.3f}s"
                fill="freeze"/>

        </rect>
        """

        cells.append(cell)

    return "".join(cells)


# ============================================================
# CREATE SVG
# ============================================================

def create_svg(data):

    username = data["username"]

    total = data["stats"]["total"]

    days = data["days"]

    cells = create_cells(
        days
    )

    svg = f'''<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{WIDTH}"
    height="{HEIGHT}"
    viewBox="0 0 {WIDTH} {HEIGHT}">

    <!-- Background -->

    <rect
        width="{WIDTH}"
        height="{HEIGHT}"
        rx="12"
        fill="#0d1117"
        stroke="#30363d"
        stroke-width="2"/>


    <!-- Header -->

    <text
        x="25"
        y="22"
        fill="#c9d1d9"
        font-family="monospace"
        font-size="13">

        {username} • contributions
    </text>


    <!-- Contribution cells -->

    {cells}


    <!-- Legend -->

    <text
        x="25"
        y="158"
        fill="#8b949e"
        font-family="monospace"
        font-size="12">

        Less
    </text>


    <rect
        x="60"
        y="148"
        width="11"
        height="11"
        rx="2"
        fill="#161b22"/>

    <rect
        x="77"
        y="148"
        width="11"
        height="11"
        rx="2"
        fill="#0e4429"/>

    <rect
        x="94"
        y="148"
        width="11"
        height="11"
        rx="2"
        fill="#006d32"/>

    <rect
        x="111"
        y="148"
        width="11"
        height="11"
        rx="2"
        fill="#26a641"/>

    <rect
        x="128"
        y="148"
        width="11"
        height="11"
        rx="2"
        fill="#39d353"/>


    <text
        x="150"
        y="158"
        fill="#8b949e"
        font-family="monospace"
        font-size="12">

        More
    </text>


    <!-- Footer -->

    <text
        x="25"
        y="180"
        fill="#39d353"
        font-family="monospace"
        font-size="13">

        {total:,} contributions in the last year
    </text>

</svg>
'''

    return svg


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "Generating contribution heatmap..."
    )

    data = load_data()

    svg = create_svg(
        data
    )

    OUTPUT_FILE.write_text(
        svg,
        encoding="utf-8"
    )

    print(
        f"Generated: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()