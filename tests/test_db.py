import pytest

from src.database.db import init_db, insert_records


@pytest.fixture
def mock_db_path(tmp_path):
    db_file = tmp_path / "test_lottery.db"
    # Overwrite the db module's path for testing
    import src.database.db as db_module

    db_module.DB_PATH = str(db_file)
    init_db()
    return str(db_file)


def test_insert_records_and_duplicate_prevention(mock_db_path):
    records = [
        {
            "draw_id": "TEST-1",
            "game": "euromillions",
            "draw_date": "2026-01-01",
            "main_numbers": [1, 2, 3, 4, 5],
            "lucky_stars": [1, 2],
            "draw_number": 1,
            "source_url": "http://test",
        }
    ]

    # First insert should succeed
    summary = insert_records(records)
    assert summary["inserted"] == 1
    assert summary["skipped_duplicate"] == 0

    # Second insert of identical record should skip
    summary2 = insert_records(records)
    assert summary2["inserted"] == 0
    assert summary2["skipped_duplicate"] == 1


def test_insert_different_game_same_draw_number(mock_db_path):
    records = [
        {
            "draw_id": "TEST-EU-1",
            "game": "euromillions",
            "draw_date": "2026-01-01",
            "main_numbers": [1, 2, 3, 4, 5],
            "lucky_stars": [1, 2],
            "draw_number": 1,
            "source_url": "http://test-eu",
        },
        {
            "draw_id": "TEST-TB-1",
            "game": "thunderball",
            "draw_date": "2026-01-01",
            "main_numbers": [1, 2, 3, 4, 5],
            "thunderball": [1],
            "draw_number": 1,
            "source_url": "http://test-tb",
        },
    ]

    # Both should insert perfectly (no collision on draw_number=1 because game differs)
    summary = insert_records(records)
    assert summary["inserted"] == 2
    assert summary["skipped_duplicate"] == 0
