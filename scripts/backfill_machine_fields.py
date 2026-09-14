"""
Backfill machine_number and ball_set for existing draws.
Re-fetches draw pages and does UPDATE (not INSERT) for rows missing these fields.
"""
import sqlite3
import sys
import time
from pathlib import Path

# Allow imports from src/
sys.path.append(str(Path(__file__).resolve().parent.parent))

import requests
from bs4 import BeautifulSoup
from src.collectors.base import BaseCollector

DB_PATH = "data/lottery.db"
HEADERS = {"User-Agent": "LotteryDataCollector/0.2 (educational project)"}

GAME_URLS = {
    "euromillions":  "https://www.national-lottery.co.uk/results/euromillions/draw-details",
    "thunderball":   "https://www.national-lottery.co.uk/results/thunderball/draw-details",
    "set_for_life":  "https://www.national-lottery.co.uk/results/set-for-life/draw-details",
}

def fetch_and_parse_machine_info(url: str, draw_no: int):
    """Fetch a single draw page and extract machine_number and ball_set."""
    full_url = f"{url}?drawNo={draw_no}"
    for attempt in range(3):
        try:
            resp = requests.get(full_url, headers=HEADERS, timeout=12)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                return BaseCollector.parse_machine_info(soup)
            print(f"  ⚠️  HTTP {resp.status_code} for draw {draw_no} (attempt {attempt+1})")
        except Exception as e:
            print(f"  ⚠️  Error fetching draw {draw_no}: {e} (attempt {attempt+1})")
        time.sleep(1)
    return None, None


def backfill():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Find all draws missing machine_number OR ball_set
    rows = conn.execute("""
        SELECT d.draw_id, d.draw_number, g.name as game
        FROM draws d
        JOIN games g ON d.game_id = g.game_id
        WHERE d.machine_number IS NULL OR d.ball_set IS NULL
        ORDER BY g.name, d.draw_number
    """).fetchall()

    if not rows:
        print("✅ All draws already have machine_number and ball_set populated. Nothing to do!")
        conn.close()
        return

    print(f"Found {len(rows)} draws missing machine_number / ball_set. Starting backfill...\n")

    updated = 0
    skipped = 0

    for row in rows:
        game = row["game"]
        draw_no = row["draw_number"]
        draw_id = row["draw_id"]
        url = GAME_URLS.get(game)

        if not url:
            print(f"  ⚠️  Unknown game '{game}', skipping {draw_id}")
            skipped += 1
            continue

        machine_number, ball_set = fetch_and_parse_machine_info(url, draw_no)

        if machine_number or ball_set:
            conn.execute(
                "UPDATE draws SET machine_number = ?, ball_set = ? WHERE draw_id = ?",
                (machine_number, ball_set, draw_id)
            )
            conn.commit()
            print(f"  ✅ {draw_id:35s} machine={machine_number!r:<20} ball_set={ball_set!r}")
            updated += 1
        else:
            print(f"  ℹ️  {draw_id:35s} no machine info on page (older draw, data not published)")
            skipped += 1

        # Be polite - small delay between requests
        time.sleep(0.4)

    conn.close()
    print(f"\n{'='*55}")
    print(f"Backfill complete: {updated} updated, {skipped} skipped (no data on page)")
    print(f"{'='*55}")
    print("\nNow restart Streamlit and click 'Clear cache' to see the updated data.")


if __name__ == "__main__":
    backfill()
