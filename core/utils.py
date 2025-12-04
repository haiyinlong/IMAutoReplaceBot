# core/utils.py
import pyautogui
import pyperclip
import pygetwindow as gw
import time
import cv2
import numpy as np
import os
from datetime import datetime
from typing import Tuple, Optional, List

def save_screenshot(region: Tuple[int, int, int, int], prefix: str = "screenshot") -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    filename = f"{prefix}_{timestamp}.png"
    filepath = os.path.join("screenshots", filename)
    os.makedirs("screenshots", exist_ok=True)
    screenshot = pyautogui.screenshot(region=region)
    screenshot.save(filepath)
    return filepath

def find_window_by_titles(titles: List[str]) -> Optional[gw.Window]:
    for title in titles:
        candidates = gw.getWindowsWithTitle(title)
        for win in candidates:
            if win.width > 0 and win.height > 0:
                return win
    return None

def send_clipboard_message(msg: str):
    pyperclip.copy(msg)
    time.sleep(0.5)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    pyautogui.press('enter')