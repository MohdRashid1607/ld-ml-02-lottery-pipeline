import sys
sys.path.append(".")

from src.collectors.thunderball import ThunderballCollector
from config.settings import get_game_config

collector = ThunderballCollector(get_game_config("thunderball"))
html = collector.fetch_draw_page(3963)

with open("thunderball_debug.html", "w", encoding="utf-8") as f:
    f.write(html)

import re
for match in re.finditer(r'.{80}(?:machine|ball set).{80}', html, re.IGNORECASE):
    print("---MATCH---")
    print(match.group())
    print()