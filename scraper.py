#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import codecs
from twitter import *
from tweet import Tweet
from twitter_config import *

twitter = Twitter(auth=OAuth(twitter_auth['access_token'],
                             twitter_auth['access_secret'],
                             twitter_auth['consumer_key'],
                             twitter_auth['consumer_secret']))


def get_latest_tweets(user, count=200):
    results = twitter.statuses.user_timeline(screen_name=user, exclude_replies=True, count=count)
    return [Tweet(status["id"],
                  status["text"],
                  status["created_at"],
                  status["entities"]["hashtags"],
                  status["retweet_count"],
                  status["favorite_count"],
                  status["user"]["name"],
                  status["user"]["location"]) for status in results]


def get_tweets_by_max_id(user, max_id):
    results = twitter.statuses.user_timeline(screen_name=user, exclude_replies=True, count=200, max_id=max_id)
    return [Tweet(status["id"],
                  status["text"],
                  status["created_at"],
                  status["entities"]["hashtags"],
                  status["retweet_count"],
                  status["favorite_count"],
                  status["user"]["name"],
                  status["user"]["location"]) for status in results]


def get_all_tweets(user):
    tweets = get_latest_tweets(user)
    max_id = tweets[-1].id - 1
    while True:
        results = get_tweets_by_max_id(user, max_id)
        if not results:
            break
        max_id = results[-1].id - 1
        tweets += results
    with open("./out/%s.json" % user, "w") as f:
        json.dump([ob.__dict__ for ob in tweets], codecs.getwriter('utf-8')(f), ensure_ascii=False)

if __name__ == '__main__':
    for u in USERS:
        get_all_tweets(u)

