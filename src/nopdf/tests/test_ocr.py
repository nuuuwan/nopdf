"""Tests for ocr"""

import unittest

from nopdf import ocr


class TestOcr(unittest.TestCase):
    """Tests."""

    def test_ocr(self):
        """Test."""
        self.assertTrue(ocr.ocr())


if __name__ == '__main__':
    unittest.main()
    