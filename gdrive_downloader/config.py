"""Persistência simples de configurações em JSON."""
import json
from pathlib import Path

_CONFIG_PATH = Path.home() / ".config" / "gdrive_downloader" / "config.json"


def load_config() -> dict:
    try:
        return json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_config(data: dict) -> None:
    _CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    _CONFIG_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def get_api_key() -> str:
    return load_config().get("api_key", "")


def set_api_key(key: str) -> None:
    cfg = load_config()
    cfg["api_key"] = key.strip()
    save_config(cfg)
