"""CustomDgigovlk."""
import re
import logging

from utils import www

from nopdf import scrape, ocr

URL = 'https://www.dgi.gov.lk/news/press-releases-sri-lanka/covid-19-documents'

REGEX_MEDIA_URL = r'.+/(?P<date>\d{4}\.\d{2}\.\d{2})/.+' \
    + r'(?P<ref_no>\d{3}).+-page-(?P<page_no>\d{3}).+'


def custom_dgigovlk():
    """Run custom."""
    media_url_list = scrape.scrape(URL)
    for media_url in media_url_list:
        if not any([
            'Press_Release' in media_url,
            'PR_' in media_url,
        ]):
            continue

        result = re.search(REGEX_MEDIA_URL, media_url)
        if not result:
            logging.error('Invalid URL format: %s', media_url)
            break

        info = result.groupdict()
        date = info['date'].replace('.', '')
        ref_no = info['ref_no']
        page_no = info['page_no']

        base_name = '/tmp/nopdf.dgigovlk.%s.ref%s.page%s' % (
            date,
            ref_no,
            page_no,
        )
        text_file = '%s.txt' % (base_name)
        image_file = '%s.jpeg' % (base_name)

        www.download_binary(media_url, image_file)
        ocr.ocr(image_file, text_file)


if __name__ == '__main__':
    custom_dgigovlk()
