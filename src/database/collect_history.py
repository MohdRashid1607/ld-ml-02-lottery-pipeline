"""
Day 5 - complete first lottery: full historical collection,
incremental updates, and run summary logging.

Source only exposes ~180 days of EuroMillions draws (documented
limitation). "Agreed historical period" = full available window,
draws 1924 through 1974 (27 Feb 2026 - 21 Aug 2026).
"""

import sys
import logging
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.collectors.fetch_draw import collect_draw_range
from src.database.db import get_connection, init_db, insert_records
from src.validation.validator import validate_batch

FIRST_AVAILABLE_DRAW = 1924
LATEST_KNOWN_DRAW = 1974


def get_latest_draw_number_in_db() -> int:
    """Return the highest draw_number currently stored, or 0 if empty."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT MAX(draw_number) FROM draws WHERE game_id = "
            "(SELECT game_id FROM games WHERE name = 'euromillions')"
        )
        result = cursor.fetchone()[0]
        return result if result is not None else 0
    finally:
        conn.close()


def run_collection(start_draw: int, end_draw: int, mode: str) -> None:
    run_start = datetime.now(timezone.utc)
    print(f"[{mode}] Run started at {run_start}")
    print(f"[{mode}] Fetching draws {start_draw} to {end_draw}...")

    # 1. Fetch & Parse (raw list of dicts)
    init_db()
    records = collect_draw_range(start_draw, end_draw)
    print(f"[{mode}] Fetched {len(records)} records.")

    if not records:
        return

    # 2. Validate
    results = validate_batch(records)
    valid_records = results["passed"]
    rejected_count = len(results["failed"])

    # 3. Persist
    summary = insert_records(valid_records)

    run_end = datetime.now(timezone.utc)
    duration = (run_end - run_start).total_seconds()

    print(f"\n[{mode}] Run summary")
    print(f"  Start time:  {run_start}")
    print(f"  End time:    {run_end}")
    print(f"  Duration:    {duration:.1f}s")
    print(f"  Fetched:     {fetched_count}")
    print(f"  Valid:       {len(valid_records)}")
    print(f"  Rejected:    {rejected_count}")
    print(f"  Inserted:    {summary['inserted']}")
    print(f"  Skipped (duplicates): {summary['skipped_duplicate']}")


def full_historical_collection():
    """Day 5: collect the full available historical period."""
    run_collection(FIRST_AVAILABLE_DRAW, LATEST_KNOWN_DRAW, mode="FULL HISTORY")


def incremental_update():
    """
    Only fetch draws newer than what's already stored.
    Safe to run repeatedly - fetches nothing new if already up to date.
    """
    latest_stored = get_latest_draw_number_in_db()
    if latest_stored == 0:
        print("[INCREMENTAL] No existing data found - run full_historical_collection first.")
        return

    start = latest_stored + 1
    end = LATEST_KNOWN_DRAW

    if start > end:
        print(
            f"[INCREMENTAL] Already up to date (latest stored: {latest_stored}). Nothing to fetch."
        )
        return

    run_collection(start, end, mode="INCREMENTAL")


if __name__ == "__main__":
    import sys as _sys

    if len(_sys.argv) > 1 and _sys.argv[1] == "incremental":
        incremental_update()
    else:
        full_historical_collection()
