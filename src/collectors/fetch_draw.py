"""
EuroMillions collector - Day 2: HTTP request function.

Fetches a single EuroMillions draw page from national-lottery.co.uk
by draw number, with a timeout, a descriptive user agent, status-code
checking, and a small bounded number of retries on transient failures.

Source: https://www.national-lottery.co.uk/results/euromillions/draw-details
Access notes: site allows crawling per robots.txt (checked 2026-08-25).
Known limitation: only the most recent ~180 days of draws are reachable
through this site (confirmed by testing old draw numbers, which return
a "Something went wrong" error rather than draw data).
"""

import logging
import time

import requests

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
        "(educational internship project; contact: 2004.moras@gmail.com)"
    )
}
TIMEOUT_SECONDS = 10
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2


def fetch_draw_page(draw_no: int) -> str | None:
    """
    Fetch the raw HTML for a single EuroMillions draw page.

    Returns the HTML text on success, or None if all retries fail.
    Never raises on network errors - failures are logged instead,
    so a single bad draw number does not crash a batch run.
    """
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


if __name__ == "__main__":
    # Known-working draw range confirmed manually in the browser.
    test_draw_no = 1965
    html = fetch_draw_page(test_draw_no)

    if html:
        print(f"Successfully fetched draw {test_draw_no}, {len(html)} characters")
        # Save one sample page as a fixture for offline parsing/tests
        with open("tests/fixtures/euromillions_draw_1965.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Saved sample to tests/fixtures/euromillions_draw_1965.html")
    else:
        print(f"Failed to fetch draw {test_draw_no} - check logs/activity.log")