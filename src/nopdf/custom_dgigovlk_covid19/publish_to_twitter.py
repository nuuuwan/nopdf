"""Publish to Twitter."""
import os
import random
import time

import tweepy

from nopdf.custom_dgigovlk_covid19.CONSTANTS import GITHUB_TOOL_URL
from nopdf.custom_dgigovlk_covid19.common import _get_ref_prefix, log
from nopdf.custom_dgigovlk_covid19.render_summary_as_markdown \
    import _get_details_lines


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
    twtr_api_key,
    twtr_api_secret_key,
    twtr_access_token,
    twtr_access_token_secret,
):
    """Publish to Twitter."""
    ref_no = data['ref_no']

    auth = tweepy.OAuthHandler(twtr_api_key, twtr_api_secret_key)
    auth.set_access_token(twtr_access_token, twtr_access_token_secret)
    api = tweepy.API(auth)

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

    images = _get_images(data)
    if not images:
        log.info('%s: No images. Not tweeting')
        return

    media_ids = []
    for image in images:
        res = api.media_upload(image)
        media_id = res.media_id
        media_ids.append(media_id)
        log.info('%s: Uploaded image to twitter as %s', ref_no, media_id)

    log.info('%s: Tweeting: %s', ref_no, tweet_text)
    api.update_status(tweet_text, media_ids=media_ids)
    time.sleep(random.random() * 5)
