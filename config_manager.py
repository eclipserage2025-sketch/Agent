import json
import os

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "host": "litecoinpool.org",
    "port": 3333,
    "user": "",
    "threads": 4,
    "v2": False,
    "autotune": True,
    "autostart": False
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_FILE, 'r') as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    except Exception:
        return DEFAULT_CONFIG

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception:
        return False
