"""
Set For Life collector - Day 8.

Responsibility: parse Set For Life-specific HTML only.
All generic fetching, retry logic, and rate limiting lives in BaseCollector.

Source: https://www.national-lottery.co.uk/results/set-for-life/draw-details
"""

import logging
import re

from bs4 import BeautifulSoup

from src.collectors.base import BaseCollector

logger = logging.getLogger("set_for_life_collector")


class SetForLifeCollector(BaseCollector):
    """
    Set For Life-specific collector.
    Inherits generic fetch/retry from BaseCollector.
    Only overrides parse_html() with game-specific logic.
    """

    def parse_html(self, html: str, draw_no: int) -> dict:
        """
        Parse one Set For Life draw page into a normalized record dict.
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

        # The Life Ball uses the same secondary ball selector
        life_ball = [
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

        if not main_numbers or not life_ball or parsed_draw_no is None:
            raise ValueError(
                f"Missing required fields when parsing Set For Life draw {draw_no}: "
                f"main={main_numbers}, life_ball={life_ball}, draw_no={parsed_draw_no}"
            )

        return {
            "draw_id": f"SET-FOR-LIFE-{parsed_draw_no}",
            "game": "set_for_life",
            "draw_date": draw_date,
            "main_numbers": main_numbers,
            "life_ball": life_ball,
            "draw_number": parsed_draw_no,
            "source_url": f"{self.base_url}?drawNo={parsed_draw_no}",
        }
