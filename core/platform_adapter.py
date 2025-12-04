# core/platform_adapter.py
import re
import cv2
import numpy as np
import pyautogui
from abc import ABC, abstractmethod
from typing import Tuple, List, Optional, Any
from .utils import save_screenshot
from .ocr_engine import OCREngine

class PlatformAdapter(ABC):
    def __init__(self, name: str, config: dict, ocr_engine: OCREngine):
        self.name = name
        self.config = config
        self.ocr_engine = ocr_engine
        self.chat_region = tuple(config["chat_region"])
        self.contact_list_region = tuple(config["contact_list_region"]) if config["contact_list_region"] else None
        self.threshold = config["message_position_threshold"]

    @abstractmethod
    def find_main_window(self):
        pass

    @abstractmethod
    def click_unread_contact(self) -> bool:
        pass

    @abstractmethod
    def get_latest_message_info(self) -> Tuple[str, bool]:
        pass

    def send_reply(self, msg: str):
        from .utils import send_clipboard_message
        send_clipboard_message(msg)


class ConfigurablePlatformAdapter(PlatformAdapter):
    def find_main_window(self):
        from .utils import find_window_by_titles
        return find_window_by_titles(self.config["window_titles"])

    def click_unread_contact(self) -> bool:
        if not self.config.get("detect_unread", False) or not self.contact_list_region:
            return False

        x, y, w, h = self.contact_list_region
        region = (x, y, w, h)
        save_screenshot(region, f"{self.name}_contacts")
        try:
            screenshot = pyautogui.screenshot(region=region)
            img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

            lower_red1 = np.array([0, 50, 50])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([160, 55, 55])
            upper_red2 = np.array([180, 255, 255])
            mask = cv2.bitwise_or(
                cv2.inRange(hsv, lower_red1, upper_red1),
                cv2.inRange(hsv, lower_red2, upper_red2)
            )
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            valid = []
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if 200 <= area <= 350:
                    perimeter = cv2.arcLength(cnt, True)
                    if perimeter > 0:
                        circularity = 4 * np.pi * area / (perimeter ** 2)
                        if circularity >= 0.8:
                            valid.append(cnt)
            if not valid:
                return False
            cnt = max(valid, key=cv2.contourArea)
            bx, by, bw, bh = cv2.boundingRect(cnt)
            cx = x + bx + bw // 2
            cy = y + by + bh // 2
            pyautogui.click(cx, cy)
            return True
        except Exception as e:
            print(f"[{self.name}] 点击未读失败: {e}")
            return False

    def get_latest_message_info(self) -> Tuple[str, bool]:
        left, top, width, height = self.chat_region
        region = (left, top, width, height)
        save_screenshot(region, "ocr")
        try:
            screenshot = pyautogui.screenshot(region=region)
            img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            results = self.ocr_engine.read_text(img)
        except Exception as e:
            print(f"OCR 失败: {e}")
            return "", False

        chat_center_x = width / 2
        valid_msgs = []

        for bbox, text, prob in results:
            text = text.strip()
            if prob < 0.3 or not text:
                continue

            xs = [pt[0] for pt in bbox]
            ys = [pt[1] for pt in bbox]
            cx = sum(xs) / len(xs)
            cy = sum(ys) / len(ys)

            if abs(cx - chat_center_x) < 120:
                if re.fullmatch(r'\d+分钟前|\d+小时前|刚刚|今天|昨天|上午|下午|\d{1,2}:\d{2}', text):
                    continue
            if text.isdigit() and len(text) <= 4:
                continue

            valid_msgs.append((cx, cy, text))

        if not valid_msgs:
            return "", False

        valid_msgs.sort(key=lambda x: x[1], reverse=True)
        latest_x, _, latest_text = valid_msgs[0]
        is_from_others = latest_x < (width * self.threshold)
        return latest_text, is_from_others