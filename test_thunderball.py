import sys
sys.path.append(".")

from src.collectors.thunderball import ThunderballCollector
from config.settings import get_game_config

collector = ThunderballCollector(get_game_config("thunderball"))
record = collector.collect_draw(3963)
print(record)