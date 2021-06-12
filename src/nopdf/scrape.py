"""Scrape."""
import logging

from urllib.parse import urlparse
from bs4 import BeautifulSoup

from utils import www
from utils.cache import cache

logging.basicConfig(level=logging.DEBUG)


@cache('nopdf', 86400)
def scrape(url):
    """Run."""
    html = www.read(url)
    soup = BeautifulSoup(html, 'html.parser')
    domain = urlparse(url).netloc
    media_url_list = list(map(
        lambda img: 'https:/%s%s' % (domain, img.get('src')),
        soup.find_all('img'),
    ))

    logging.debug('Scraped %d images from %s', len(media_list), url)
    return media_url_list
