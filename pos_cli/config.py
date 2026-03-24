"""Configuration management for POS CLI."""

import json
import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".pos-cli"
CONFIG_FILE = CONFIG_DIR / "config.json"
SESSION_FILE = CONFIG_DIR / "session.json"

DEFAULT_CONFIG = {
    "base_url": "http://localhost:8000",
}


def ensure_config_dir():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    ensure_config_dir()
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    return DEFAULT_CONFIG.copy()


def save_config(config: dict):
    ensure_config_dir()
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def load_session() -> dict | None:
    if SESSION_FILE.exists():
        with open(SESSION_FILE) as f:
            return json.load(f)
    return None


def save_session(session: dict):
    ensure_config_dir()
    with open(SESSION_FILE, "w") as f:
        json.dump(session, f, indent=2)


def clear_session():
    if SESSION_FILE.exists():
        SESSION_FILE.unlink()


def get_base_url() -> str:
    return os.environ.get("POS_URL", load_config()["base_url"])
