"""
Validation module - Day 4: defensive checks against game rules.

Validates a parsed draw record dict against the rules defined in
config/game_rules.yaml. Never silently accepts bad data - every
rejection comes with a specific, human-readable reason.
"""

import logging
from datetime import datetime

import yaml

logging.basicConfig(
    filename="logs/activity.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("validator")

RULES_PATH = "config/game_rules.yaml"


def load_rules() -> dict:
    """Load game rules from the YAML config file."""
    with open(RULES_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_record(record: dict, rules: dict) -> list[str]:
    """
    Validate one draw record against its game's rules.

    Returns a list of rejection reasons. An empty list means the
    record passed all checks.
    """
    reasons = []

    game = record.get("game")
    if not game or game not in rules:
        return [f"Unknown or missing game: {game!r}"]

    game_rules = rules[game]

    # --- Required fields ---
    required_fields = ["draw_id", "draw_date", "main_numbers", "draw_number"]
    for field in required_fields:
        if field not in record or record[field] in (None, "", []):
            reasons.append(f"Missing required field: {field}")

    if reasons:
        # Can't safely continue checking types/ranges if fields are missing
        return reasons

    # --- Date format ---
    date_format = game_rules.get("date_format", "%a %d %b %Y")
    try:
        from datetime import timezone

        datetime.strptime(record["draw_date"], date_format).replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        reasons.append(
            f"Invalid date format: {record['draw_date']!r} (expected format like '{date_format}')"
        )

    # --- Main numbers: type, count, range, uniqueness ---
    main_numbers = record.get("main_numbers", [])
    main_rules = game_rules["main_numbers"]

    if not all(isinstance(n, int) for n in main_numbers):
        reasons.append(f"Main numbers must all be integers: {main_numbers}")
    else:
        if len(main_numbers) != main_rules["count"]:
            reasons.append(f"Expected {main_rules['count']} main numbers, got {len(main_numbers)}")
        out_of_range = [
            n for n in main_numbers if not (main_rules["min"] <= n <= main_rules["max"])
        ]
        if out_of_range:
            reasons.append(
                f"Main numbers out of range [{main_rules['min']}-{main_rules['max']}]: {out_of_range}"
            )
        if len(set(main_numbers)) != len(main_numbers):
            reasons.append(f"Main numbers contain duplicates: {main_numbers}")

    # --- Bonus numbers: type, count, range, uniqueness ---
    bonus_field = game_rules["bonus_numbers"].get("name", "lucky_stars")
    bonus_numbers = record.get(bonus_field, [])
    bonus_rules = game_rules["bonus_numbers"]

    if not all(isinstance(n, int) for n in bonus_numbers):
        reasons.append(f"Bonus numbers must all be integers: {bonus_numbers}")
    else:
        if len(bonus_numbers) != bonus_rules["count"]:
            reasons.append(
                f"Expected {bonus_rules['count']} bonus numbers, got {len(bonus_numbers)}"
            )
        out_of_range = [
            n for n in bonus_numbers if not (bonus_rules["min"] <= n <= bonus_rules["max"])
        ]
        if out_of_range:
            reasons.append(
                f"Bonus numbers out of range [{bonus_rules['min']}-{bonus_rules['max']}]: {out_of_range}"
            )
        if len(set(bonus_numbers)) != len(bonus_numbers):
            reasons.append(f"Bonus numbers contain duplicates: {bonus_numbers}")

    # --- draw_number type check ---
    if not isinstance(record.get("draw_number"), int):
        reasons.append(f"draw_number must be an integer: {record.get('draw_number')!r}")

    return reasons


def validate_batch(records: list[dict]) -> dict:
    """
    Validate a list of records. Returns a summary dict with
    'passed' and 'failed' lists, where each failed entry includes
    the record and its rejection reasons.
    """
    rules = load_rules()
    passed = []
    failed = []

    for record in records:
        reasons = validate_record(record, rules)
        if reasons:
            failed.append({"record": record, "reasons": reasons})
            logger.warning(f"Rejected record {record.get('draw_id', '?')}: {'; '.join(reasons)}")
        else:
            passed.append(record)
            logger.info(f"Validated record {record['draw_id']}: passed")

    logger.info(f"Validation batch complete: {len(passed)} passed, {len(failed)} failed")
    return {"passed": passed, "failed": failed}
