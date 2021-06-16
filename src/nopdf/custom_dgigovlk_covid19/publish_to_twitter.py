"""Publish to Twitter."""
import json
import tweepy

from nopdf.custom_dgigovlk_covid19.CONSTANTS import GITHUB_URL
from nopdf.custom_dgigovlk_covid19.common import _get_ref_prefix, log
from nopdf.custom_dgigovlk_covid19.render_summary_as_markdown \
    import _get_details_lines


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
    details_link = '%s/%s.md' % (GITHUB_URL, ref_prefix)

    tweet_text = '''Press release no. {ref_no}
{datetime}

{details_text}

#COVID19SL #SriLanka #lka
{details_link}
'''.format(
        ref_no=ref_no,
        datetime=data['datetime'],
        details_text=details_text,
        details_link=details_link,
    )
    log.debug('%s: Tweeting: %s', ref_no, tweet_text)
