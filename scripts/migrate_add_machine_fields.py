"""
Migration: Add machine_number and ball_set columns to existing draws table.
Safe to run multiple times - ignores errors if columns already exist.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path("data/lottery.db")

def migrate():
    if not DB_PATH.exists():
        print("❌ data/lottery.db not found. Run the collectors first.")
        return

    conn = sqlite3.connect(DB_PATH)
    
    for col in ["machine_number TEXT", "ball_set TEXT"]:
        col_name = col.split()[0]
        try:
            conn.execute(f"ALTER TABLE draws ADD COLUMN {col}")
            print(f"✅ Added column: {col_name}")
        except sqlite3.OperationalError:
            print(f"ℹ️  Column already exists (skipped): {col_name}")

    conn.commit()
    conn.close()
    print("\n✅ Migration complete! Run your collectors again to populate machine_number and ball_set.")
    print("   Example:  python src\\main.py --game thunderball --mode full")
    print("   Example:  python src\\main.py --game euromillions --mode full")
    print("   Example:  python src\\main.py --game set_for_life --mode full")

if __name__ == "__main__":
    migrate()
