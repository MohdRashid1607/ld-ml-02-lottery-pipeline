import logging
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo
import requests
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[2]))
from config.settings import load_game_rules

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("weather")

DB_PATH = "data/lottery.db"

def fetch_weather_for_draws():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    rules = load_game_rules()
    
    # 1. Get all venues to map city name to venue_id
    venues = {row["city"]: row["venue_id"] for row in conn.execute("SELECT * FROM venues").fetchall()}
    
    # 2. Get all draws that don't have weather readings
    cursor = conn.execute("""
        SELECT d.draw_id, d.draw_date, g.name as game_name 
        FROM draws d
        JOIN games g ON d.game_id = g.game_id
        LEFT JOIN weather_readings w ON d.draw_id = w.draw_id
        WHERE w.draw_id IS NULL
    """)
    draws = cursor.fetchall()
    
    if not draws:
        logger.info("All draws already have weather enrichment! No new API calls needed.")
        return

    logger.info(f"Found {len(draws)} draws needing weather enrichment.")

    for draw in draws:
        game_name = draw["game_name"]
        game_rules = rules[game_name]
        
        venue_city = game_rules["venue"]
        venue_id = venues[venue_city]
        lat = rules["venues"][venue_city]["latitude"]
        lon = rules["venues"][venue_city]["longitude"]
        tz_name = game_rules["timezone"]
        
        # Parse local datetime
        date_str = draw["draw_date"]
        time_str = game_rules["draw_time"]
        
        # format: "Tue 21 Jul 2026"
        date_format = game_rules.get("date_format", "%a %d %b %Y")
        try:
            local_dt = datetime.strptime(f"{date_str} {time_str}", f"{date_format} %H:%M")
        except ValueError:
            logger.error(f"Could not parse date {date_str} for {draw['draw_id']}")
            continue
            
        local_dt = local_dt.replace(tzinfo=ZoneInfo(tz_name))
        utc_dt = local_dt.astimezone(ZoneInfo("UTC"))
        
        # Open-Meteo expects YYYY-MM-DD
        iso_date = local_dt.strftime("%Y-%m-%d")
        
        # Update draws table with datetime info and venue_id
        conn.execute("""
            UPDATE draws 
            SET venue_id = ?, draw_local_datetime = ?, draw_datetime_utc = ?
            WHERE draw_id = ?
        """, (venue_id, local_dt.isoformat(), utc_dt.isoformat(), draw["draw_id"]))
        
        # Fetch weather from Open-Meteo
        api_url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={iso_date}&end_date={iso_date}&hourly=temperature_2m&timezone=UTC"
        
        try:
            resp = requests.get(api_url, timeout=10)
            if resp.status_code != 200:
                logger.warning(f"Weather API error {resp.status_code} for {iso_date}")
                continue
                
            data = resp.json()
            if "hourly" not in data:
                logger.warning(f"No hourly weather data found for {iso_date}")
                continue
                
            # Find the closest hour
            times = data["hourly"]["time"]
            temps = data["hourly"]["temperature_2m"]
            
            # Match the hour of the UTC draw time
            target_hour_str = utc_dt.strftime("%Y-%m-%dT%H:00")
            
            if target_hour_str in times:
                idx = times.index(target_hour_str)
                temp = temps[idx]
                
                if temp is not None:
                    conn.execute("""
                        INSERT INTO weather_readings (draw_id, provider, observed_at, temperature_c, match_minutes, status)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (draw["draw_id"], "Open-Meteo", target_hour_str, temp, 0, "verified"))
                    logger.info(f"✅ Enriched {draw['draw_id']} | {venue_city} | {temp}°C")
                else:
                    logger.warning(f"Null temperature found for {target_hour_str}")
            
        except Exception as e:
            logger.error(f"Failed to fetch weather for {draw['draw_id']}: {e}")
            
        # Commit every draw so we don't lose progress
        conn.commit()

if __name__ == "__main__":
    fetch_weather_for_draws()
