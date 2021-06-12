"""Ocr"""

import pytesseract

from PIL import Image


def ocr(image_file):
    """Run."""
    return pytesseract.image_to_string(
        Image.open(image_file),
    )
