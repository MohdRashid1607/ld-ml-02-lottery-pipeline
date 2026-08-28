import pytest

from src.validation.validator import load_rules, validate_record


@pytest.fixture
def rules():
    return load_rules()


def test_valid_euromillions_record(rules):
    record = {
        "draw_id": "EUROMILLIONS-1234",
        "game": "euromillions",
        "draw_date": "Tue 21 Jul 2026",
        "main_numbers": [5, 10, 15, 20, 25],
        "lucky_stars": [3, 9],
        "draw_number": 1234,
        "source_url": "http://test",
    }
    reasons = validate_record(record, rules)
    assert not reasons, f"Should be valid, got: {reasons}"


def test_missing_required_field(rules):
    record = {
        "game": "euromillions",
        # missing draw_id
        "draw_date": "Tue 21 Jul 2026",
        "main_numbers": [5, 10, 15, 20, 25],
        "lucky_stars": [3, 9],
        "draw_number": 1234,
    }
    reasons = validate_record(record, rules)
    assert any("Missing required field" in r for r in reasons)


def test_out_of_range_numbers(rules):
    record = {
        "draw_id": "EUROMILLIONS-1234",
        "game": "euromillions",
        "draw_date": "Tue 21 Jul 2026",
        "main_numbers": [5, 10, 15, 20, 99],  # 99 is invalid
        "lucky_stars": [3, 15],  # 15 is invalid
        "draw_number": 1234,
    }
    reasons = validate_record(record, rules)
    assert any("Main numbers out of range" in r for r in reasons)
    assert any("Bonus numbers out of range" in r for r in reasons)


def test_incorrect_ball_count(rules):
    record = {
        "draw_id": "EUROMILLIONS-1234",
        "game": "euromillions",
        "draw_date": "Tue 21 Jul 2026",
        "main_numbers": [5, 10, 15, 20],  # only 4
        "lucky_stars": [3, 9, 11],  # 3 instead of 2
        "draw_number": 1234,
    }
    reasons = validate_record(record, rules)
    assert any("Expected 5 main numbers" in r for r in reasons)
    assert any("Expected 2 bonus numbers" in r for r in reasons)


def test_duplicate_balls(rules):
    record = {
        "draw_id": "EUROMILLIONS-1234",
        "game": "euromillions",
        "draw_date": "Tue 21 Jul 2026",
        "main_numbers": [5, 10, 15, 20, 5],  # 5 is duplicate
        "lucky_stars": [9, 9],  # duplicate
        "draw_number": 1234,
    }
    reasons = validate_record(record, rules)
    assert any("Main numbers contain duplicates" in r for r in reasons)
    assert any("Bonus numbers contain duplicates" in r for r in reasons)
