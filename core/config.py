# core/config.py
import json
from typing import Dict, Any

CONFIG_FILE = "config.json"

def load_config() -> Dict[str, Any]:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def validate_config(config: Dict[str, Any]) -> None:
    required_keys = ["global", "platforms", "current_platform"]
    for key in required_keys:
        assert key in config, f"配置缺少必要字段: {key}"
    assert config["current_platform"] in config["platforms"], "当前平台未在 platforms 中定义"