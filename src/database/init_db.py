"""
Day 3 - initialize the database and load Day 2's collected records.

Run this script to:
1. Create the database and tables if they don't exist.
2. Fetch and parse the same draw range from Day 2 (draws 1965-1974).
3. Insert them, with duplicate prevention.

Run it twice in a row to confirm the second run inserts zero new
records (idempotence check).
"""

import sys
from pathlib import Path

# Allow running this script directly from the project root
sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.collectors.fetch_draw import collect_draw_range
from src.database.db import init_db, insert_records
from src.validation.validator import validate_batch


def main():
    print("Initializing database...")
    init_db()

    print("Collecting EuroMillions draws 1965-1974...")
    records = collect_draw_range(1965, 1974)
    print(f"Collected {len(records)} records from source.")

    print("Validating records before insert...")
    results = validate_batch(records)
    print(f"  Valid: {len(results['passed'])}")
    print(f"  Invalid (rejected, not inserted): {len(results['failed'])}")
    for failure in results["failed"]:
        print(f"    - {failure['record'].get('draw_id', '?')}: {failure['reasons']}")

    print("Inserting only validated records into database...")
    summary = insert_records(results["passed"])

    print(f"\nRun summary:")
    print(f"  Inserted: {summary['inserted']}")
    print(f"  Skipped (duplicates): {summary['skipped_duplicate']}")


if __name__ == "__main__":
    main()