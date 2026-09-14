import sys
import sqlite3
import pandas as pd
from pathlib import Path

def test():
    db_path = Path("data/lottery.db").resolve()
    conn = sqlite3.connect(db_path)
    
    query = """
        SELECT 
            d.draw_id,
            g.name as game,
            d.draw_number,
            d.draw_date,
            d.draw_local_datetime,
            d.draw_datetime_utc,
            d.machine_number,
            d.ball_set,
            v.city,
            v.country_code,
            v.latitude,
            v.longitude,
            v.timezone,
            w.temperature_c,
            w.observed_at as weather_observed_at,
            w.provider as weather_provider,
            w.match_minutes,
            w.status as quality_status,
            d.source_url,
            d.scraped_at
        FROM draws d
        JOIN games g ON d.game_id = g.game_id
        LEFT JOIN venues v ON d.venue_id = v.venue_id
        LEFT JOIN weather_readings w ON d.draw_id = w.draw_id
        ORDER BY d.draw_number DESC
    """
    df = pd.read_sql(query, conn)
    print(f"Total rows in df: {len(df)}")
    
    export_columns = [
        "draw_id", "game", "draw_number", "draw_date", "draw_local_datetime",
        "timezone", "draw_datetime_utc", "main_numbers", "bonus_numbers",
        "machine_number", "ball_set", "city", "country_code", "latitude",
        "longitude", "temperature_c", "weather_observed_at", "match_minutes",
        "quality_status", "source_url", "weather_provider", "scraped_at",
    ]
    
    export_df = df[[c for c in export_columns if c in df.columns]].copy()
    print(f"Total rows in export_df: {len(export_df)}")
    
    csv_out = export_df.to_csv(index=False)
    print(f"CSV lines: {len(csv_out.splitlines())}")

if __name__ == "__main__":
    test()
