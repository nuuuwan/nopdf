"""Ocr"""
import pytesseract

from PIL import Image

def ocr(image_file, text_file):
    """Run."""
    text = pytesseract.image_to_string(
        Image.open(image_file),
    )

    with open(text_file, 'w') as fout:
        fout.write(text)
        fout.close()
    return text
