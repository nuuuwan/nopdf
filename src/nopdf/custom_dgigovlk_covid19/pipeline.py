"""CustomDgigovlk."""
import os
import re
import datetime

from utils import filex, www, timex, jsonx
from gig import ents

from nopdf import scrape, ocr

from nopdf.custom_dgigovlk_covid19.common import _get_ref_prefix, log
from nopdf.custom_dgigovlk_covid19.render_data_as_markdown \
    import render_data_as_markdown
from nopdf.custom_dgigovlk_covid19.parse_text_and_save_data \
    import parse_text_and_save_data

URL = 'https://www.dgi.gov.lk/news/press-releases-sri-lanka/covid-19-documents'
GITHUB_URL = 'https://raw.githubusercontent.com/nuuuwan/nopdf_data/main'
REGEX_MEDIA_URL = r'.+/(?P<date>\d{4}\.\d{2}\.\d{2})/.+' \
    + r'(?P<ref_no>\d{3}).+-page-(?P<page_no>\d{3}).+'


def _filter_press_releases(url_list):
    def _is_press_release(url):
        return any([
            'Press_Release' in url,
            'PR_' in url,
        ])
    return list(filter(_is_press_release, url_list))


def _get_image_urls():
    log.debug('Scraping %s for urls', URL)
    media_url_list = scrape.scrape(URL)
    image_urls = _filter_press_releases(media_url_list)
    log.debug('Found %d press-release urls', len(image_urls))
    return image_urls


def group_images_by_ref_and_page(image_urls):
    ref_to_page_to_url = {}
    for url in image_urls:
        result = re.search(REGEX_MEDIA_URL, url)
        if not result:
            log.error('Invalid URL format: %s', url)
            continue

        info = result.groupdict()
        ref_no = info['ref_no']
        page_no = info['page_no']

        if ref_no not in ref_to_page_to_url:
            ref_to_page_to_url[ref_no] = {}
        ref_to_page_to_url[ref_no][page_no] = url
    log.debug(
        'Found %d press-releases.',
        len(ref_to_page_to_url.keys()),
    )
    return ref_to_page_to_url


def _download_text_from_github(ref_no):
    ref_prefix = _get_ref_prefix(ref_no)
    github_text_url = '%s/%s.txt' % (GITHUB_URL, ref_prefix)
    if www.exists(github_text_url):
        all_text = www.read(github_text_url)
        log.debug('%s: Downloaded from GitHub.', ref_no)
        return all_text
    log.debug('%s: Not on GitHub.', ref_no)
    return None


def custom_dgigovlk():
    """Run custom."""
    image_urls = _get_image_urls()
    ref_to_page_to_url = group_images_by_ref_and_page(image_urls)

    data_list = []
    for ref_no, page_to_url in sorted(
        ref_to_page_to_url.items(),
        key=lambda item: item[0],
    ):
        ref_prefix = _get_ref_prefix(ref_no)
        all_text = _download_text_from_github(ref_no)
        if not all_text:
            all_text = ''
            for page_no, url in sorted(
                page_to_url.items(),
                key=lambda item: item[0],
            ):
                image_file = '/tmp/%s.jpeg' % (ref_prefix)
                www.download_binary(url, image_file)
                log.debug('%s: Downloaded image - page %d', ref_no, page_no)

                text_file = '/tmp/%s.txt' % (ref_prefix)
                text = ocr.ocr(image_file, text_file)
                log.debug('%s: OCRed text - page %d', ref_no, page_no)

                all_text += text

            all_text_file = '/tmp/%s.txt' % (ref_prefix)
            filex.write(all_text_file, all_text)
            log.debug('%s: Wrote all text', ref_no)

        data = parse_text_and_save_data(ref_no, all_text)
        data_list.append(data)
        render_data_as_markdown(data)
    return data_list


if __name__ == '__main__':
    custom_dgigovlk()