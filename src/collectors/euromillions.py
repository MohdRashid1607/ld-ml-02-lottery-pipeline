"""
EuroMillions collector - Day 6 refactor.

Responsibility: parse EuroMillions-specific HTML only.
All generic fetching, retry logic, and rate limiting lives in BaseCollector.
"""

import logging
import re

from bs4 import BeautifulSoup

from src.collectors.base import BaseCollector

logger = logging.getLogger("euromillions_collector")


class EuroMillionsCollector(BaseCollector):
    """
    EuroMillions-specific collector.
    Inherits generic fetch/retry from BaseCollector.
    Only overrides parse_html() with game-specific logic.
    """

    def parse_html(self, html: str, draw_no: int) -> dict:
        """
        Parse one EuroMillions draw page into a normalized record dict.
        Raises ValueError if required fields are missing.
        """
        soup = BeautifulSoup(html, "html.parser")

        main_numbers = [
            int(
                li.select_one(".DrawNumber-module-scss-module__0PF4Jq__number").get_text(strip=True)
            )
            for li in soup.select('li[data-testid^="drawn-ball-"]')
            if li.select_one(".DrawNumber-module-scss-module__0PF4Jq__number")
        ]

        lucky_stars = [
            int(
                li.select_one(".DrawNumber-module-scss-module__0PF4Jq__number").get_text(strip=True)
            )
            for li in soup.select('li[data-testid^="drawn-secondary-ball-"]')
            if li.select_one(".DrawNumber-module-scss-module__0PF4Jq__number")
        ]

        date_span = soup.select_one(".DrawDetails-module-scss-module__ack70W__drawDate")
        draw_date = date_span.get_text(strip=True) if date_span else None

        drawno_span = soup.select_one(".DrawDetails-module-scss-module__ack70W__drawNo")
        parsed_draw_no = None
        if drawno_span:
            match = re.search(r"\d+", drawno_span.get_text())
            if match:
                parsed_draw_no = int(match.group())

        code_span = soup.select_one(".RaffleCode-module-scss-module__zfcKHG__code")
        raffle_code = code_span.get_text(strip=True) if code_span else None
        machine_number, ball_set = self.parse_machine_info(soup)

        if not main_numbers or not lucky_stars or parsed_draw_no is None:
            raise ValueError(
                f"Missing required fields when parsing draw {draw_no}: "
                f"main={main_numbers}, stars={lucky_stars}, draw_no={parsed_draw_no}"
            )

        return {
            "draw_id": f"EUROMILLIONS-{parsed_draw_no}",
            "game": "euromillions",
            "draw_date": draw_date,
            "main_numbers": main_numbers,
            "lucky_stars": lucky_stars,
            "raffle_code": raffle_code,
            "draw_number": parsed_draw_no,
            "machine_number": machine_number,
            "ball_set": ball_set,
            "source_url": f"{self.base_url}?drawNo={parsed_draw_no}",
        }
