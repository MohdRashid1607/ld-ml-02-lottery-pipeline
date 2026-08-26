"""
Day 4 - run validation against real collected records plus 5
deliberately invalid test records, and print a summary report.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.collectors.fetch_draw import collect_draw_range
from src.validation.validator import validate_batch

# Five deliberately invalid records, each breaking exactly one rule
INVALID_TEST_RECORDS = [
    {
        "draw_id": "BAD-1-OUT-OF-RANGE",
        "game": "euromillions",
        "draw_date": "Tue 21 Jul 2026",
        "main_numbers": [2, 3, 8, 28, 51],  # 51 is above max of 50
        "lucky_stars": [2, 11],
        "draw_number": 90001,
    },
    {
        "draw_id": "BAD-2-WRONG-COUNT",
        "game": "euromillions",
        "draw_date": "Tue 21 Jul 2026",
        "main_numbers": [2, 3, 8, 28],  # only 4, should be 5
        "lucky_stars": [2, 11],
        "draw_number": 90002,
    },
    {
        "draw_id": "BAD-3-DUPLICATE",
        "game": "euromillions",
        "draw_date": "Tue 21 Jul 2026",
        "main_numbers": [2, 2, 8, 28, 39],  # 2 appears twice
        "lucky_stars": [2, 11],
        "draw_number": 90003,
    },
    {
        "draw_id": "BAD-4-BAD-DATE",
        "game": "euromillions",
        "draw_date": "2026-07-21",  # wrong format
        "main_numbers": [2, 3, 8, 28, 39],
        "lucky_stars": [2, 11],
        "draw_number": 90004,
    },
    {
        "draw_id": "BAD-5-MISSING-FIELD",
        "game": "euromillions",
        "draw_date": None,  # missing required field
        "main_numbers": [2, 3, 8, 28, 39],
        "lucky_stars": [2, 11],
        "draw_number": 90005,
    },
]


def main():
    print("Collecting real EuroMillions draws (1965-1974)...")
    real_records = collect_draw_range(1965, 1974)
    print(f"Collected {len(real_records)} real records.")

    all_records = real_records + INVALID_TEST_RECORDS
    print(f"Validating {len(all_records)} records "
          f"({len(real_records)} real + {len(INVALID_TEST_RECORDS)} deliberately invalid)...\n")

    results = validate_batch(all_records)

    print("=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Passed: {len(results['passed'])}")
    print(f"Failed: {len(results['failed'])}")
    print()

    if results["failed"]:
        print("Rejected records and reasons:")
        for failure in results["failed"]:
            draw_id = failure["record"].get("draw_id", "?")
            print(f"\n  {draw_id}:")
            for reason in failure["reasons"]:
                print(f"    - {reason}")


if __name__ == "__main__":
    main()