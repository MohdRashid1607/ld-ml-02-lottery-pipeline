"""
Database module - Day 3: schema, connection, and insert logic.

Normalized schema:
- games: one row per lottery game (e.g. EuroMillions)
- draws: one row per draw, linked to a game
- draw_numbers: one row per number drawn (main or bonus), linked to a draw

This normalization avoids storing numbers as a comma-separated string,
and makes querying individual numbers (e.g. "how often has 7 appeared")
straightforward with plain SQL instead of string parsing.
"""

import logging
import sqlite3
from pathlib import Path

logging.basicConfig(
    filename="logs/activity.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("database")

DB_PATH = "data/lottery.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS games (
    game_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS draws (
    draw_id TEXT PRIMARY KEY,
    game_id INTEGER NOT NULL,
    draw_number INTEGER NOT NULL,
    draw_date TEXT NOT NULL,
    raffle_code TEXT,
    source_url TEXT,
    scraped_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_id) REFERENCES games (game_id),
    UNIQUE (game_id, draw_number)
);

CREATE TABLE IF NOT EXISTS draw_numbers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    draw_id TEXT NOT NULL,
    number_type TEXT NOT NULL CHECK (number_type IN ('main', 'bonus')),
    position INTEGER NOT NULL,
    value INTEGER NOT NULL,
    FOREIGN KEY (draw_id) REFERENCES draws (draw_id),
    UNIQUE (draw_id, number_type, position)
);
"""


def get_connection() -> sqlite3.Connection:
    """Open a connection to the SQLite database, creating the folder if needed."""
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Create all tables if they don't already exist."""
    conn = get_connection()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
        logger.info(f"Database initialized at {DB_PATH}")
    finally:
        conn.close()


def get_or_create_game(conn: sqlite3.Connection, game_name: str) -> int:
    """Return the game_id for a game name, inserting it if it doesn't exist."""
    cursor = conn.execute("SELECT game_id FROM games WHERE name = ?", (game_name,))
    row = cursor.fetchone()
    if row:
        return row[0]

    cursor = conn.execute("INSERT INTO games (name) VALUES (?)", (game_name,))
    conn.commit()
    return cursor.lastrowid


def insert_draw(conn: sqlite3.Connection, record: dict) -> str:
    """
    Insert one parsed draw record (dict) into the database.

    Returns one of: "inserted", "skipped_duplicate".
    Uses parameterized SQL throughout - never string-formats values
    directly into a query.
    """
    game_id = get_or_create_game(conn, record["game"])

    try:
        conn.execute(
            """
            INSERT INTO draws (draw_id, game_id, draw_number, draw_date, raffle_code, source_url)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                record["draw_id"],
                game_id,
                record["draw_number"],
                record["draw_date"],
                record.get("raffle_code"),
                record.get("source_url"),
            ),
        )
    except sqlite3.IntegrityError:
        # UNIQUE constraint on (game_id, draw_number) or draw_id already exists
        logger.info(f"Skipped duplicate draw: {record['draw_id']}")
        return "skipped_duplicate"

    # Insert main numbers
    for position, value in enumerate(record["main_numbers"], start=1):
        conn.execute(
            """
            INSERT INTO draw_numbers (draw_id, number_type, position, value)
            VALUES (?, 'main', ?, ?)
            """,
            (record["draw_id"], position, value),
        )

    # Insert bonus numbers - field name varies by game (lucky_stars,
    # thunderball, etc.), so look it up from game_rules.yaml the same
    # way the validator does, instead of hardcoding one game's key.
    from src.validation.validator import load_rules
    rules = load_rules()
    bonus_field = rules[record["game"]]["bonus_numbers"].get("name", "lucky_stars")
    bonus_numbers = record.get(bonus_field, [])
    for position, value in enumerate(bonus_numbers, start=1):
        conn.execute(
            """
            INSERT INTO draw_numbers (draw_id, number_type, position, value)
            VALUES (?, 'bonus', ?, ?)
            """,
            (record["draw_id"], position, value),
        )

    conn.commit()
    logger.info(f"Inserted draw: {record['draw_id']}")
    return "inserted"


def insert_records(records: list[dict]) -> dict:
    """
    Insert a list of parsed draw records. Returns a summary count of
    how many were inserted vs skipped as duplicates.
    """
    conn = get_connection()
    summary = {"inserted": 0, "skipped_duplicate": 0}
    try:
        for record in records:
            result = insert_draw(conn, record)
            summary[result] += 1
    finally:
        conn.close()

    logger.info(
        f"Insert run complete: {summary['inserted']} inserted, "
        f"{summary['skipped_duplicate']} skipped as duplicates"
    )
    return summary