"""Ocr"""
import logging
import pytesseract

from PIL import Image

logging.basicConfig(level=logging.DEBUG)


def ocr(image_file, text_file):
    """Run."""
    text = pytesseract.image_to_string(
        Image.open(image_file),
    )

    with open(text_file, 'w') as fout:
        fout.write(text)
        fout.close()
    logging.debug('Wrote %dB to %s', len(text), text_file)
    return text
