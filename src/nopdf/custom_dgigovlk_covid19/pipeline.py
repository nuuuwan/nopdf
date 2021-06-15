"""CustomDgigovlk."""
import os
import re
import logging
import datetime

from utils import filex, www, timex, jsonx
from gig import ents

from nopdf import scrape, ocr
from nopdf.custom_dgigovlk_covid19.render_markdown import render_markdown
from nopdf.custom_dgigovlk_covid19.parse_text import parse_text

URL = 'https://www.dgi.gov.lk/news/press-releases-sri-lanka/covid-19-documents'
GITHUB_URL = 'https://raw.githubusercontent.com/nuuuwan/nopdf_data/main'
REGEX_MEDIA_URL = r'.+/(?P<date>\d{4}\.\d{2}\.\d{2})/.+' \
    + r'(?P<ref_no>\d{3}).+-page-(?P<page_no>\d{3}).+'


def _get_press_releases(url_list):

    def _is_press_release(url):
        return any([
            'Press_Release' in url,
            'PR_' in url,
        ])

    return list(filter(_is_press_release, url_list))


def custom_dgigovlk(
    force_source_redownload=False,
):
    """Run custom."""
    # get press release image urls
    media_url_list = scrape.scrape(URL)
    press_release_url_list = _get_press_releases(media_url_list)

    # group images by ref and page
    ref_to_page_to_url = {}
    for url in press_release_url_list:
        result = re.search(REGEX_MEDIA_URL, url)
        if not result:
            logging.error('Invalid URL format: %s', url)
            continue

        info = result.groupdict()
        ref_no = info['ref_no']
        page_no = info['page_no']

        if ref_no not in ref_to_page_to_url:
            ref_to_page_to_url[ref_no] = {}
        ref_to_page_to_url[ref_no][page_no] = url

    data_list = []
    for ref_no, page_to_url in sorted(
        ref_to_page_to_url.items(),
        key=lambda item: item[0],
    ):
        ref_name_all = 'nopdf.dgigovlk.ref%s' % (
            ref_no,
        )
        all_text_file = '/tmp/%s.txt' % (ref_name_all)
        github_text_url = '%s/%s.txt' % (GITHUB_URL, ref_name_all)

        if not os.path.exists(all_text_file):
            if not force_source_redownload \
                    and www.exists(github_text_url):
                all_text = www.read(github_text_url)
                logging.debug('%s exists.', github_text_url)
            else:
                all_text = ''
                for page_no, url in sorted(
                    page_to_url.items(),
                    key=lambda item: item[0],
                ):
                    ref_name = 'nopdf.dgigovlk.ref%s.page%s' % (
                        ref_no,
                        page_no,
                    )
                    image_file = '/tmp/%s.jpeg' % (ref_name)
                    if not os.path.exists(image_file):
                        www.download_binary(url, image_file)

                    text_file = '/tmp/%s.txt' % (ref_name)
                    if not os.path.exists(text_file):
                        text = ocr.ocr(image_file, text_file)
                    else:
                        text = filex.read(text_file)

                    all_text += text
                filex.write(all_text_file, all_text)
        else:
            all_text = filex.read(all_text_file)

        data_file = '/tmp/%s.json' % (ref_name_all)
        data = parse_text(ref_no, all_text)
        jsonx.write(data_file, data)
        data_list.append(data)
        render_markdown(data)

    logging.info('Found %d press releases.', len(data_list))
    return data_list


if __name__ == '__main__':
    custom_dgigovlk(
        force_source_redownload=False,
    )
