import json
from pathlib import Path
from platformdirs import user_config_dir

APP_NAME = "LT200B-GUI"
CONFIG_FILENAME = "config.json"

def get_config_path() -> Path:
    config_dir = Path(user_config_dir(APP_NAME))
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / CONFIG_FILENAME

def load_config() -> dict:
    path = get_config_path()
    if path.exists():
        with open(path, "r") as f:
            return json.load(f)
    return {}

def save_config(data: dict):
    path = get_config_path()
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
