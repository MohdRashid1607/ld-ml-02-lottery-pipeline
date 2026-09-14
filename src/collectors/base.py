import logging
import time
from abc import ABC, abstractmethod
import re
import requests

logger = logging.getLogger("collector_base")


class BaseCollector(ABC):
    """
    Abstract base class for lottery collectors.
    Handles generic HTTP fetching, retries, and rate limiting.
    Forces child classes to implement game-specific HTML parsing.
    """

    def __init__(self, config: dict):
        self.config = config
        self.base_url = config["source_url"]
        self.headers = {"User-Agent": "LotteryDataCollector/0.2 (educational project)"}
        self.max_retries = 3
        self.retry_delay = 2

    def fetch_draw_page(self, draw_no: int) -> str | None:
        """Generic method to fetch HTML with retry logic."""
        url = f"{self.base_url}?drawNo={draw_no}"

        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    return response.text
                logger.warning(
                    f"Draw {draw_no} returned {response.status_code} (attempt {attempt})"
                )
            except requests.exceptions.RequestException as exc:
                logger.error(f"Request error on draw {draw_no}: {exc}")

            if attempt < self.max_retries:
                time.sleep(self.retry_delay)

        logger.error(f"Failed to fetch draw {draw_no} after {self.max_retries} attempts.")
        return None

    @staticmethod
    def parse_machine_info(soup) -> tuple[str | None, str | None]:
        """
        Extract the draw machine name and ball set identifier.

        These are alphanumeric identifiers (e.g. "13" for EuroMillions,
        "Excalibur4" for Thunderball), not necessarily pure numbers, so
        both are kept as strings rather than cast to int.

        Returns (machine_name, ball_set). Either may be None if the
        page doesn't expose this section.
        """
        container = soup.select_one('[data-testid="draw-machines"]')
        if not container:
            return None, None

        text = container.get_text(" ", strip=True)
        machine_match = re.search(r"Draw machine:\s*([A-Za-z0-9]+)", text)
        ball_set_match = re.search(r"Ball set:\s*([A-Za-z0-9]+)", text)

        machine_name = machine_match.group(1) if machine_match else None
        ball_set = ball_set_match.group(1) if ball_set_match else None
        return machine_name, ball_set
    
    @abstractmethod
    def parse_html(self, html: str, draw_no: int) -> dict:
        """
        Must be implemented by subclasses.
        Takes raw HTML and returns a normalized dictionary record.
        """

    def collect_draw(self, draw_no: int) -> dict | None:
        """Orchestrates fetching and parsing for a single draw."""
        html = self.fetch_draw_page(draw_no)
        if not html:
            return None
        try:
            return self.parse_html(html, draw_no)
        except ValueError as exc:
            logger.error(f"Failed to parse draw {draw_no}: {exc}")
            return None
