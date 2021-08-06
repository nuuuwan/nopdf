"""Ocr"""
import pytesseract
from PIL import Image


def ocr(image_file, text_file):
    """Run."""
    img = Image.open(image_file)
    text = pytesseract.image_to_string(img)

    with open(text_file, 'w') as fout:
        fout.write(text)
        fout.close()
    return text
