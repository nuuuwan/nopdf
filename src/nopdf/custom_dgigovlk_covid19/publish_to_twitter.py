"""Publish to Twitter."""
import json
import tweepy


def publish_to_twitter(
    data,
    twtr_api_key,
    twtr_api_secret_key,
    twtr_access_token,
    twtr_access_token_secret,
):
    """Publish to Twitter."""
    auth = tweepy.OAuthHandler(api_key, api_secret_key)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    print(api.update_status(json.dumps(data)))
