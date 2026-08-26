"""
EuroMillions collector - Day 2: raw extraction and parsing.

Reads EuroMillions draw history from a CSV source (downloaded from
national-lottery.co.uk) and parses each row into a plain Python
dictionary representing one draw.

Source: https://www.national-lottery.co.uk/results/euromillions/draw-history
Access date: 2026-08-25
Note: this source provides the most recent ~180 days of draws only.
Deeper historical backfill is a separate concern for Day 5.
"""

import csv
import logging
from pathlib import Path

logging.basicConfig(
    filename="logs/activity.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("euromillions_collector")


def parse_draw_row(row: dict) -> dict:
    """
    Convert one raw CSV row into a normalized draw record dictionary.

    Raises ValueError if required fields are missing or malformed.
    """
    try:
        record = {
            "draw_id": f"EUROMILLIONS-{row['DrawNumber'].strip()}",
            "game": "euromillions",
            "draw_date": row["DrawDate"].strip(),
            "main_numbers": [
                int(row["Ball 1"]),
                int(row["Ball 2"]),
                int(row["Ball 3"]),
                int(row["Ball 4"]),
                int(row["Ball 5"]),
            ],
            "lucky_stars": [
                int(row["Lucky Star 1"]),
                int(row["Lucky Star 2"]),
            ],
            "draw_number": int(row["DrawNumber"]),
            "source_url": "https://www.national-lottery.co.uk/results/euromillions/draw-history",
        }
        return record
    except (KeyError, ValueError) as exc:
        logger.error(f"Failed to parse row: {row} - {exc}")
        raise


def extract_records(csv_path: str) -> list[dict]:
    """
    Read the CSV file and return a list of parsed draw record dicts.
    Rows that fail to parse are logged and skipped, not silently dropped.
    """
    path = Path(csv_path)
    records = []

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                record = parse_draw_row(row)
                records.append(record)
            except ValueError:
                continue  # already logged inside parse_draw_row

    logger.info(f"Extracted {len(records)} records from {csv_path}")
    return records


if __name__ == "__main__":
    results = extract_records("tests/fixtures/euromillions_sample.csv")
    print(f"Parsed {len(results)} records. First 3 examples:\n")
    for r in results[:3]:
        print(r)
