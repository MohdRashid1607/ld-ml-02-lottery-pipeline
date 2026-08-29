import pytest

from config.settings import get_game_config
from src.collectors.euromillions import EuroMillionsCollector
from src.collectors.thunderball import ThunderballCollector


def test_euromillions_parser_missing_fields():
    config = get_game_config("euromillions")
    collector = EuroMillionsCollector(config)

    # Empty HTML should raise ValueError
    with pytest.raises(ValueError, match="Missing required fields"):
        collector.parse_html("<html><body></body></html>", 1234)


def test_thunderball_parser_missing_fields():
    config = get_game_config("thunderball")
    collector = ThunderballCollector(config)

    # Empty HTML should raise ValueError
    with pytest.raises(ValueError, match="Missing required fields"):
        collector.parse_html("<html><body></body></html>", 9999)


# If we had robust fixtures, we would test successful parsing here too,
# but testing the error handling for malformed HTML is the critical path.
