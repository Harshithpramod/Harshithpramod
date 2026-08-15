import json
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup


# ============================================================
# CONFIGURATION
# ============================================================

USERNAME = "harshithpramod"

URL = f"https://github.com/users/{USERNAME}/contributions"

OUTPUT_FILE = Path("data/contributions.json")


# ============================================================
# FETCH GITHUB PAGE
# ============================================================

def fetch_contribution_page():
    print(f"Fetching contributions for @{USERNAME}...")

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        URL,
        headers=headers,
        timeout=30
    )

    print(f"GitHub response: {response.status_code}")

    response.raise_for_status()

    return response.text


# ============================================================
# PARSE CONTRIBUTION CELLS
# ============================================================

def parse_contributions(html):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    days = []

    # GitHub contribution calendar cells
    cells = soup.select(
        "td.ContributionCalendar-day"
    )

    print(f"Found {len(cells)} contribution cells.")

    for cell in cells:

        date = cell.get("data-date")

        if not date:
            continue

        # GitHub uses data-level for the intensity.
        level = cell.get(
            "data-level",
            "0"
        )

        try:
            level = int(level)
        except ValueError:
            level = 0

        # GitHub exposes the contribution count
        # through the accessible label.
        label = cell.get(
            "aria-label",
            ""
        )

        count = 0

        # Examples:
        #
        # "1 contribution on August 10, 2026"
        # "5 contributions on August 11, 2026"
        #
        match = re.search(
            r"(\d+)\s+contribution",
            label
        )

        if match:
            count = int(
                match.group(1)
            )

        days.append({
            "date": date,
            "count": count,
            "level": level
        })

    return days


# ============================================================
# CALCULATE BASIC STATS
# ============================================================

def calculate_stats(days):

    total = sum(
        day["count"]
        for day in days
    )

    best_day = None

    if days:
        best_day = max(
            days,
            key=lambda day: day["count"]
        )

    return {
        "total": total,
        "best_day": best_day
    }


# ============================================================
# MAIN
# ============================================================

def main():

    html = fetch_contribution_page()

    days = parse_contributions(
        html
    )

    if not days:

        raise RuntimeError(
            "\nNo contribution cells were found.\n"
            "Possible reasons:\n"
            "1. GitHub changed its HTML structure.\n"
            "2. Username is incorrect.\n"
            "3. GitHub returned a different page.\n"
        )

    stats = calculate_stats(
        days
    )

    result = {

        "username": USERNAME,

        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "days": days,

        "stats": stats
    }

    # Make sure data/ exists
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_FILE.write_text(
        json.dumps(
            result,
            indent=2
        ),
        encoding="utf-8"
    )

    print()
    print("====================================")
    print(" Contribution data generated")
    print("====================================")
    print(f"Username : {USERNAME}")
    print(f"Days     : {len(days)}")
    print(f"Total    : {stats['total']}")
    print(f"Output   : {OUTPUT_FILE}")
    print("====================================")


if __name__ == "__main__":
    main()