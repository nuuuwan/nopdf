"""Tests for scrape"""

import unittest

from nopdf import scrape


class TestScrape(unittest.TestCase):
    """Tests."""

    def test_scrape(self):
        """Test."""
        self.assertTrue(scrape.scrape())


if __name__ == '__main__':
    unittest.main()
    