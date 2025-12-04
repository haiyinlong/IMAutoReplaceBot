# main.py
from datetime import datetime, timedelta
import time
import random
import sys
import os

# 添加当前目录到路径（确保 core 可导入）
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config import load_config, validate_config
from core.logger import setup_logger
from core.ocr_engine import OCREngine
from core.platform_adapter import ConfigurablePlatformAdapter
from core.utils import find_window_by_titles

# ========================
# 全局状态
# ========================
last_reply_time = None

def should_reply(latest_text: str, is_from_others: bool, trigger_keywords, cooldown_sec) -> bool:
    global last_reply_time
    if not is_from_others or not latest_text.strip():
        return False
    if not any(kw in latest_text for kw in trigger_keywords):
        return False
    if last_reply_time and (datetime.now() - last_reply_time) < timedelta(seconds=cooldown_sec):
        return False
    return True

def main():
    config = load_config()
    validate_config(config)

    global_config = config["global"]
    platforms_config = config["platforms"]
    current_platform_name = config["current_platform"]

    logger = setup_logger()
    logger.info(f"加载配置完成，当前平台: {current_platform_name}")

    # 初始化 OCR
    ocr_engine = OCREngine(
        languages=global_config["ocr_languages"],
        use_gpu=global_config["use_gpu"]
    )

    # 创建适配器
    platform_config = platforms_config[current_platform_name]
    adapter = ConfigurablePlatformAdapter(current_platform_name, platform_config, ocr_engine)

    check_interval = global_config["check_interval_sec"]
    reply_cooldown = global_config["reply_cooldown_sec"]
    reply_msg = global_config["reply_message"]
    trigger_keywords = global_config["trigger_keywords"]

    logger.info(f"🚀 启动 {adapter.name} 自动回复助手...")

    while True:
        try:
            win = adapter.find_main_window()
            if not win:
                logger.warning(f"未找到 {adapter.name} 窗口")
                time.sleep(10)
                continue

            if win.isMinimized:
                win.restore()
                time.sleep(1.5)
            if not win.isActive:
                try:
                    win.activate()
                    time.sleep(1)
                except Exception as e:
                    if "Error code from Windows: 0" not in str(e):
                        raise

            if adapter.config.get("detect_unread", False):
                adapter.click_unread_contact()
                time.sleep(1)

            latest_text, is_from_others = adapter.get_latest_message_info()

            if should_reply(latest_text, is_from_others, trigger_keywords, reply_cooldown):
                global last_reply_time
                adapter.send_reply(reply_msg)
                last_reply_time = datetime.now()
                time.sleep(random.uniform(2, 4))
            else:
                if latest_text.strip():
                    logger.debug(f"[{adapter.name}] 未触发: '{latest_text[:50]}...'")

            time.sleep(check_interval)

        except KeyboardInterrupt:
            logger.info("用户终止程序")
            break
        except Exception as e:
            logger.exception(f"主循环异常: {e}")
            time.sleep(10)

    logger.info("程序退出")

if __name__ == "__main__":
    main()