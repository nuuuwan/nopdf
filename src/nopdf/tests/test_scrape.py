"""Tests for scrape"""

import unittest

from nopdf import scrape

TEST_URL = 'https://www.dgi.gov.lk' \
    + '/news/press-releases-sri-lanka/covid-19-documents'


class TestScrape(unittest.TestCase):
    """Tests."""

    def test_scrape(self):
        """Test."""
        media_url_list = scrape.scrape(TEST_URL)
        self.assertGreater(len(media_url_list), 0)
        self.assertIn('http', media_url_list[0])


if __name__ == '__main__':
    unittest.main()
