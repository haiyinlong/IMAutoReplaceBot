# core/ocr_engine.py
import easyocr
from typing import List, Tuple, Any

class OCREngine:
    def __init__(self, languages: List[str], use_gpu: bool = False):
        self.reader = easyocr.Reader(languages, gpu=use_gpu)

    def read_text(self, image) -> List[Tuple[Any, str, float]]:
        return self.reader.readtext(image)