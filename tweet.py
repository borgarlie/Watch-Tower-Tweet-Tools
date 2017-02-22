class Tweet:
    def __repr__(self):
        return self.id

    def __init__(self, _id, text, created_at, hashtags, retweet_count, favorite_count, username, user_location):
        self.id = _id
        self.text = text
        self.created_at = created_at
        self.hashtags = hashtags
        self.retweet_count = retweet_count
        self.favorite_count = favorite_count
        self.username = username
        self.user_location = user_location
        self.location = (None, None)
