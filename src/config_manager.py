import json
from pathlib import Path

def load_config():
    config_path = Path(__file__).parent.parent / 'config.json'
    with open(config_path, 'r') as f:
        return json.load(f)

CONFIG = load_config()
