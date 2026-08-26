# Day 3 - Example SQL Queries and Results

## Query 1: List all games
Command run:
python -c "import sqlite3; conn = sqlite3.connect('data/lottery.db'); [print(r) for r in conn.execute('SELECT * FROM games')]"

Result:
(1, 'euromillions')

## Query 2: List all draws, ordered by draw number
Command run:

python -c "import sqlite3; conn = sqlite3.connect('data/lottery.db'); [print(r) for r in conn.execute('SELECT draw_id, draw_date, draw_number FROM draws ORDER BY draw_number')]"

Result:

('EUROMILLIONS-1965', 'Tue 21 Jul 2026', 1965)
('EUROMILLIONS-1966', 'Fri 24 Jul 2026', 1966)
('EUROMILLIONS-1967', 'Tue 28 Jul 2026', 1967)
('EUROMILLIONS-1968', 'Fri 31 Jul 2026', 1968)
('EUROMILLIONS-1969', 'Tue 04 Aug 2026', 1969)
('EUROMILLIONS-1970', 'Fri 07 Aug 2026', 1970)
('EUROMILLIONS-1971', 'Tue 11 Aug 2026', 1971)
('EUROMILLIONS-1972', 'Fri 14 Aug 2026', 1972)
('EUROMILLIONS-1973', 'Tue 18 Aug 2026', 1973)
('EUROMILLIONS-1974', 'Fri 21 Aug 2026', 1974)

## Query 3: Get main numbers for one specific draw
Command run:

python -c "import sqlite3; conn = sqlite3.connect('data/lottery.db'); [print(r) for r in conn.execute("SELECT draw_id, value FROM draw_numbers WHERE number_type='main' AND draw_id='EUROMILLIONS-1965' ORDER BY position")]"

Result:

('EUROMILLIONS-1965', 2)
('EUROMILLIONS-1965', 3)
('EUROMILLIONS-1965', 8)
('EUROMILLIONS-1965', 28)
('EUROMILLIONS-1965', 39)

This matches draw 1965's numbers exactly as shown on the official site.

## Duplicate Prevention Test
Ran `src/database/init_db.py` twice in a row.

**First run:**

Inserted: 10
Skipped (duplicates): 0


**Second run (same command, no changes):**

Inserted: 0
Skipped (duplicates): 10


This confirms the UNIQUE constraint on (game_id, draw_number) correctly
prevents duplicate draws from being inserted when the collector runs
again.