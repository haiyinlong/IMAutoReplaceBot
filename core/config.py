import json
from typing import Dict, Any

CONFIG_FILE = "config.json"

def load_config() -> Dict[str, Any]:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def validate_config(config: Dict[str, Any]) -> None:
    assert "global" in config, "缺少 global 配置"
    assert "platforms" in config, "缺少 platforms 配置"
    assert "current_platform" in config, "缺少 current_platform"
    assert config["current_platform"] in config["platforms"], "当前平台未定义"