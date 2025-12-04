import os
import time
from datetime import datetime, timedelta

def cleanup_old_files(directory: str, retain_days: int, logger=None):
    if not os.path.exists(directory):
        return
    cutoff = datetime.now() - timedelta(days=retain_days)
    deleted = 0
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if not os.path.isfile(filepath):
            continue
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            if mtime < cutoff:
                os.remove(filepath)
                deleted += 1
        except Exception as e:
            if logger:
                logger.warning(f"清理失败 {filepath}: {e}")
    if deleted > 0 and logger:
        logger.info(f"清理 {deleted} 个旧文件（>{retain_days}天）来自 '{directory}'")

def should_cleanup(last_time: float, interval_sec: int) -> bool:
    return (time.time() - last_time) >= interval_sec