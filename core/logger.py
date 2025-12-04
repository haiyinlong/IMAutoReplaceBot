# core/logger.py
import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logger(
    log_file: str = "auto_reply_bot.log",
    log_dir: str = "logs",
    max_bytes: int = 5 * 1024 * 1024,   # 5 MB
    backup_count: int = 3,
    level: int = logging.INFO
) -> logging.Logger:
    """
    配置带滚动功能的日志记录器。
    
    Args:
        log_file: 日志文件名（不含路径）
        log_dir: 日志目录路径
        max_bytes: 单个日志文件最大字节数（超过则轮转）
        backup_count: 保留的历史日志文件数量
        level: 日志级别
    
    Returns:
        配置好的 Logger 实例
    """
    # 确保日志目录存在
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    full_log_path = log_path / log_file

    # 创建滚动处理器
    file_handler = RotatingFileHandler(
        filename=full_log_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'  # 关键：支持中文
    )

    # 设置格式
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)

    # 创建控制台处理器（可选，便于调试）
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # 创建并配置 logger
    logger = logging.getLogger("AutoReplyBot")
    logger.setLevel(level)

    # 避免重复添加 handler（防止多次调用时日志重复）
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger