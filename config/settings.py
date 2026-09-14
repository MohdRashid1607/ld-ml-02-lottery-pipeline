from pathlib import Path

import yaml

# Path to our YAML file relative to this script
CONFIG_PATH = Path(__file__).resolve().parent / "game_rules.yaml"


def load_game_rules() -> dict:
    """Loads the game rules configuration from the YAML file."""
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_game_config(game_name: str) -> dict:
    """Returns the specific configuration block for a given game."""
    rules = load_game_rules()
    if game_name not in rules:
        raise ValueError(f"Game '{game_name}' not found in configuration.")
    return rules[game_name]
