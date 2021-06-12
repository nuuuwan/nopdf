"""Tests for ocr"""

import unittest

from nopdf import ocr

TEST_IMAGE = 'src/assets/test_image.jpeg'


class TestOcr(unittest.TestCase):
    """Tests."""

    def test_ocr(self):
        """Test."""
        text = ocr.ocr(TEST_IMAGE, '/tmp/nopdf.ocr.test_image.txt')
        lines = text.split('\n')
        self.assertEqual(len(lines), 57)

        self.assertEqual(lines[2], 'Department of Government Information')


if __name__ == '__main__':
    unittest.main()
