"""Tests for scrape"""

import unittest

from nopdf import scrape

TEST_URL = 'https://www.dgi.gov.lk' \
    + '/news/press-releases-sri-lanka/covid-19-documents'


class TestScrape(unittest.TestCase):
    """Tests."""

    def test_scrape(self):
        """Test."""
        self.assertGreater(len(scrape.scrape(TEST_URL)), 0)


if __name__ == '__main__':
    unittest.main()
