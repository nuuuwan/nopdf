"""Publish to Twitter."""
import os

from utils import twitter

from nopdf.custom_dgigovlk_covid19.common import _get_ref_prefix, log
from nopdf.custom_dgigovlk_covid19.CONSTANTS import GITHUB_TOOL_URL
from nopdf.custom_dgigovlk_covid19.render_summary_as_markdown import \
    _get_details_lines


def _get_images(data):
    ref_no = data['ref_no']
    page_nos = data['page_nos']
    ref_prefix = _get_ref_prefix(ref_no)
    images = []
    for page_no in page_nos:
        page_file_name = '/tmp/%s.page%s.jpeg' % (ref_prefix, page_no)
        if os.path.exists(page_file_name):
            images.append(page_file_name)
    return images


def publish_to_twitter(
    data,
):
    """Publish to Twitter."""
    ref_no = data['ref_no']

    details_lines = _get_details_lines(data)
    details_text = '\n'.join(details_lines)
    ref_prefix = _get_ref_prefix(ref_no)
    details_link = '%s/%s.md' % (GITHUB_TOOL_URL, ref_prefix)

    tweet_text = '''#COVID19SL Press Release {ref_no} ({datetime}) by @infodprtsl

{details_text}

#SriLanka #lka
{details_link}
'''.format(
        ref_no=ref_no,
        datetime=data['datetime'],
        details_text=details_text,
        details_link=details_link,
    )

    status_image_files = _get_images(data)
    if not status_image_files:
        log.info('%s: No images. Not tweeting', ref_no)
        return

    twtr = twitter.Twitter.from_args()
    twtr.tweet(
        tweet_text=tweet_text,
        status_image_files=status_image_files,
        update_user_profile=True,
    )
