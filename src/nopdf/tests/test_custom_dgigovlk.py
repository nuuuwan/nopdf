"""Tests for custom_dgigovlk"""

import unittest

from nopdf import custom_dgigovlk


class TestCustomDgigovlk(unittest.TestCase):
    """Tests."""

    def test_custom_dgigovlk(self):
        """Test."""
        self.assertIn('ref_no', custom_dgigovlk.custom_dgigovlk()[0])


if __name__ == '__main__':
    unittest.main()
