"""Tests for custom_dgigovlk"""

import unittest

from nopdf import custom_dgigovlk


class TestCustomDgigovlk(unittest.TestCase):
    """Tests."""

    def test_custom_dgigovlk(self):
        """Test."""
        self.assertTrue(custom_dgigovlk.custom_dgigovlk())


if __name__ == '__main__':
    unittest.main()
    