"""Scrape."""
import logging

from urllib.parse import urlparse
from bs4 import BeautifulSoup

from utils import www
from utils.cache import cache

log.basicConfig(level=log.DEBUG)


@cache('nopdf', 3600)
def scrape(url):
    """Run."""
    html = www.read(url)
    soup = BeautifulSoup(html, 'html.parser')
    domain = urlparse(url).netloc
    media_url_list = list(map(
        lambda img: 'https://%s%s' % (domain, img.get('src')),
        soup.find_all('img'),
    ))

    log.debug('Scraped %d images from %s', len(media_url_list), url)
    return media_url_list
