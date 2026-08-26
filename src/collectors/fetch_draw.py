"""
EuroMillions collector - Day 2: request + parse combined.

Fetches live EuroMillions draw pages from national-lottery.co.uk and
parses each into a normalized dictionary record.

Source: https://www.national-lottery.co.uk/results/euromillions/draw-details
Access notes: site allows crawling per robots.txt (checked 2026-08-25).
Known limitation: only the most recent ~180 days of draws are reachable
through this site.
"""

import logging
import re
import time

import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    filename="logs/activity.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("euromillions_collector")

BASE_URL = "https://www.national-lottery.co.uk/results/euromillions/draw-details"
HEADERS = {
    "User-Agent": (
        "LotteryDataCollector/0.1 "
        "(educational internship project; contact: your-email@example.com)"
    )
}
TIMEOUT_SECONDS = 10
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2


def fetch_draw_page(draw_no: int) -> str | None:
    """Fetch raw HTML for one draw. Returns None if all retries fail."""
    url = f"{BASE_URL}?drawNo={draw_no}"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT_SECONDS)
            if response.status_code == 200:
                logger.info(f"Fetched draw {draw_no} successfully (attempt {attempt})")
                return response.text
            logger.warning(
                f"Draw {draw_no} returned status {response.status_code} "
                f"(attempt {attempt}/{MAX_RETRIES})"
            )
        except requests.exceptions.RequestException as exc:
            logger.error(
                f"Request error fetching draw {draw_no} "
                f"(attempt {attempt}/{MAX_RETRIES}): {exc}"
            )
        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY_SECONDS)

    logger.error(f"Giving up on draw {draw_no} after {MAX_RETRIES} attempts")
    return None


def parse_draw_html(html: str) -> dict:
    """Parse one draw's HTML page into a normalized draw record dict."""
    soup = BeautifulSoup(html, "html.parser")

    main_numbers = []
    for li in soup.select('li[data-testid^="drawn-ball-"]'):
        num_div = li.select_one(".DrawNumber-module-scss-module__0PF4Jq__number")
        if num_div:
            main_numbers.append(int(num_div.get_text(strip=True)))

    lucky_stars = []
    for li in soup.select('li[data-testid^="drawn-secondary-ball-"]'):
        num_div = li.select_one(".DrawNumber-module-scss-module__0PF4Jq__number")
        if num_div:
            lucky_stars.append(int(num_div.get_text(strip=True)))

    date_span = soup.select_one(".DrawDetails-module-scss-module__ack70W__drawDate")
    draw_date = date_span.get_text(strip=True) if date_span else None

    drawno_span = soup.select_one(".DrawDetails-module-scss-module__ack70W__drawNo")
    draw_no = None
    if drawno_span:
        match = re.search(r"\d+", drawno_span.get_text())
        if match:
            draw_no = int(match.group())

    code_span = soup.select_one(".RaffleCode-module-scss-module__zfcKHG__code")
    raffle_code = code_span.get_text(strip=True) if code_span else None

    if not main_numbers or not lucky_stars or draw_no is None:
        raise ValueError(f"Missing required fields when parsing draw page (draw_no={draw_no})")

    return {
        "draw_id": f"EUROMILLIONS-{draw_no}",
        "game": "euromillions",
        "draw_date": draw_date,
        "main_numbers": main_numbers,
        "lucky_stars": lucky_stars,
        "raffle_code": raffle_code,
        "draw_number": draw_no,
        "source_url": f"{BASE_URL}?drawNo={draw_no}",
    }


def collect_draw_range(start_draw_no: int, end_draw_no: int) -> list[dict]:
    """
    Fetch and parse a range of draws (inclusive). Skips and logs any
    draw that fails to fetch or parse, rather than crashing the batch.
    """
    records = []
    for draw_no in range(start_draw_no, end_draw_no + 1):
        print(f"Fetching draw {draw_no}...")
        html = fetch_draw_page(draw_no)
        if html is None:
            continue
        try:
            record = parse_draw_html(html)
            records.append(record)
        except ValueError as exc:
            logger.error(f"Failed to parse draw {draw_no}: {exc}")
            continue
    return records


if __name__ == "__main__":
    # Known-working draw range confirmed manually (draws 1965-1974)
    results = collect_draw_range(1965, 1974)
    print(f"Collected {len(results)} records. First 3 examples:\n")
    for r in results[:3]:
        print(r)