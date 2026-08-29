"""
src/main.py - Day 6: unified CLI entry point for the lottery pipeline.

Orchestrates fetching, validation, and persistence.
Supports command-line arguments for game, draw range, and update mode.

Usage examples:
  # Full historical collection
  python src/main.py --game euromillions --mode full

  # Incremental update (only fetches draws newer than what's in the DB)
  python src/main.py --game euromillions --mode incremental

  # Specific draw range
  python src/main.py --game euromillions --start 1960 --end 1974

  # Custom database path
  python src/main.py --game euromillions --mode full --db data/test.db
"""

import argparse
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from config.settings import get_game_config
from src.collectors.euromillions import EuroMillionsCollector
from src.collectors.set_for_life import SetForLifeCollector
from src.collectors.thunderball import ThunderballCollector
from src.database.db import insert_records
from src.validation.validator import validate_batch

logging.basicConfig(
    filename="logs/activity.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("main")

# Registry: add new games here without changing any other code
COLLECTOR_REGISTRY = {
    "euromillions": EuroMillionsCollector,
    "thunderball": ThunderballCollector,
    "set_for_life": SetForLifeCollector,
}

DRAW_RANGES = {
    "euromillions": (1924, 1974),
    "thunderball": (3850, 3963),  # Valid recent draw numbers
    "set_for_life": (728, 778),  # Valid recent draw numbers (approx 50 draws)
}


def get_latest_draw_in_db(game: str, db_path: str) -> int:
    """Return the highest draw_number stored for a game, or 0 if none."""
    import sqlite3

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        cursor = conn.execute(
            """
            SELECT MAX(d.draw_number)
            FROM draws d
            JOIN games g ON d.game_id = g.game_id
            WHERE g.name = ?
            """,
            (game,),
        )
        result = cursor.fetchone()[0]
        return result if result is not None else 0
    finally:
        conn.close()


def run_pipeline(game: str, start: int, end: int, db_path: str, mode: str) -> None:
    """Fetch, validate, and insert draws for a given range."""
    run_start = datetime.now(timezone.utc)
    print(f"\n[{mode.upper()}] Starting pipeline for '{game}'")
    print(f"  Draw range : {start} → {end}")
    print(f"  Database   : {db_path}")
    print(f"  Start time : {run_start}")

    valid_records = []
    rejected = 0
    fetched = 0

    # 1. Initialize DB and configuration
    from src.database.db import init_db as _init_db
    _init_db()

    config = get_game_config(game)
    collector = COLLECTOR_REGISTRY[game](config)

    # 2. Fetch & Parse
    for draw_no in range(start, end + 1):
        print(f"  Fetching draw {draw_no}...")
        try:
            record = collector.collect_draw(draw_no)
            if record:
                valid_records.append(record)
                fetched += 1
            else:
                rejected += 1
        except Exception as e:
            logger.error(f"Error fetching draw {draw_no}: {e}")
            rejected += 1

    print(f"\n  Fetched {fetched} records.")

    if not valid_records:
        return

    # 3. Validate
    validation_results = validate_batch(valid_records)
    valid_records = validation_results["passed"]
    rejected += len(validation_results["failed"])

    # 4. Persist
    # Override DB_PATH temporarily
    import src.database.db as db_module

    original_path = db_module.DB_PATH
    db_module.DB_PATH = db_path
    summary = insert_records(valid_records)
    db_module.DB_PATH = original_path

    run_end = datetime.now(timezone.utc)
    duration = (run_end - run_start).total_seconds()

    # 5. Print full run summary
    print(f"\n{'='*50}")
    print(f"RUN SUMMARY — {game.upper()} — {mode.upper()}")
    print(f"{'='*50}")
    print(f"  Start time  : {run_start}")
    print(f"  End time    : {run_end}")
    print(f"  Duration    : {duration:.1f}s")
    print(f"  Fetched     : {fetched}")
    print(f"  Valid       : {len(valid_records)}")
    print(f"  Rejected    : {rejected}")
    print(f"  Inserted    : {summary['inserted']}")
    print(f"  Duplicates  : {summary['skipped_duplicate']}")
    print(f"{'='*50}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Lottery Data Collector - unified CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--game",
        required=True,
        choices=list(COLLECTOR_REGISTRY.keys()),
        help="Which lottery game to collect.",
    )
    parser.add_argument(
        "--mode",
        choices=["full", "incremental"],
        default="incremental",
        help="full = entire agreed period; incremental = only new draws.",
    )
    parser.add_argument("--start", type=int, help="Override start draw number.")
    parser.add_argument("--end", type=int, help="Override end draw number.")
    parser.add_argument("--db", default="data/lottery.db", help="Path to SQLite database.")

    args = parser.parse_args()

    default_start, default_end = DRAW_RANGES[args.game]

    # If user explicitly provides --start or --end, just use them directly.
    if args.start or args.end:
        start = args.start or default_start
        end = args.end or default_end
        run_pipeline(args.game, start, end, args.db, mode="custom range")
        return

    if args.mode == "full":
        start = default_start
        end = default_end

    elif args.mode == "incremental":
        latest = get_latest_draw_in_db(args.game, args.db)
        if latest == 0:
            print("[INCREMENTAL] No data found — switching to full collection.")
            start = default_start
        else:
            start = latest + 1
        end = default_end

        if start > end:
            print(f"[INCREMENTAL] Already up to date (latest: {latest}). Nothing to do.")
            return

    run_pipeline(args.game, start, end, args.db, args.mode)


if __name__ == "__main__":
    main()
