# -*- encoding: utf-8 -*-
import codecs
import json
import re
from math import sin, radians, sqrt, cos, atan2


class TweetIn:
    def __repr__(self):
        return ("id: %s" % self.id).encode("utf-8")

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

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True)


class Location:
    def __repr__(self):
        return ("Id: %d, County: %s, Name: %s \n" % (self.id, self.county, self.name)).encode("utf-8")

    def __init__(self, _id, county, name, latitude, longitude):
        self.id = _id
        self.county = county
        self.name = name
        self.latitude = latitude
        self.longitude = longitude


class TweetOut:
    def __repr__(self):
        return self.id

    def __init__(self, _id, text, created_at, hashtags, retweet_count, favorite_count, username, user_location, location):
        self.id = _id
        self.text = text
        self.created_at = created_at
        self.hashtags = hashtags
        self.retweet_count = retweet_count
        self.favorite_count = favorite_count
        self.username = username
        self.user_location = user_location
        self.location = location


locationMap = {}  # name : location object
locationMapDefault = {}  # name : location object (default, not filtered)
tweets = []
location_for_user = (0, 0)
name_for_location = ""
max_distance = 120000
user = "politiOpsSTPD"


# haversine distance
def calculate_distance(point1, point2):
    r = 6371e3  # Earth's radius metres
    phi = radians(point1[0])
    phi2 = radians(point2[0])
    delta_phi = radians(point2[0] - point1[0])  # Delta latitude
    delta_lambda = radians(point2[1] - point1[1])  # Delta longitude
    l = sin(delta_phi / 2) * sin(delta_phi / 2)
    lt = cos(phi) * cos(phi2) * sin(delta_lambda / 2) * sin(delta_lambda / 2)
    a = l + lt
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return r * c


def generate_default_map(filename):
    with codecs.open(filename, mode='r', encoding='utf8') as f:
        for line in f:
            sep = line.split(";")
            loc = Location(int(sep[0].strip()), sep[1].strip(), sep[2].strip(), float(sep[3].strip()), float(sep[4].strip()))
            locationMapDefault[loc.name] = loc


def generate_map(filename):
    with codecs.open(filename, mode='r', encoding='utf8') as f:
        for line in f:
            sep = line.split(";")
            loc = Location(int(sep[0].strip()), sep[1].strip(), sep[2].strip(), float(sep[3].strip()), float(sep[4].strip()))
            new_point = (loc.latitude, loc.longitude)
            new_distance = calculate_distance(new_point, location_for_user)
            if new_distance > max_distance:
                continue
            if loc.name in locationMap:
                # already exists
                old_loc = locationMap[loc.name]
                old_point = (old_loc.latitude, old_loc.longitude)
                old_distance = calculate_distance(old_point, location_for_user)
                if new_distance < old_distance:
                    locationMap[loc.name] = loc
            else:
                locationMap[loc.name] = loc


def object_decoder(obj):
    return TweetIn(obj['id'], obj['text'], obj['created_at'],
                   obj['hashtags'], obj['retweet_count'], obj['favorite_count'], obj['username'], obj['user_location'])


def load_tweets(filename):
    with open(filename, 'r') as json_file:
        json_data = json.load(json_file)
        for j in json_data:
            obj = object_decoder(j)
            tweets.append(obj)


def load_user_location(filename):
    with open(filename, 'r') as json_file:
        json_data = json.load(json_file)
        obj = object_decoder(json_data[0])
        return re.sub('[!@#$.,;:]', '', obj.user_location.split(" ")[0])


def check_tweet_for_location(tweet):
    words = tweet.text.split(" ")
    for word in words:
        word = re.sub('[!@#$.,;:]', '', word)
        if word in locationMap:
            tweet.location = locationMap[word]
            break
    else:
        tweet.location = locationMap[name_for_location]


def serialize_nested(obj):
    return obj.__dict__


def save_tweets():
    with open("tweetswithloc/%s.json" % user, "w") as f:
        json.dump([ob.__dict__ for ob in tweets], codecs.getwriter('utf-8')(f), ensure_ascii=False, default=serialize_nested)

USERS = [
    "OPSostfinnmark",
    "PolitiVestfinnm",
    "polititroms",
    "politiMHPD",
    "Saltenpolitiet",
    "HelgelandOPS",
    "politiOpsSTPD",
    "politiNTrondops",
    "Opssunnmore",
    "PolitiNoRoOps",
    "Hordalandpoliti",
    "politietsognfj",
    "Rogalandops",
    "HaugSunnOps",
    "opsnbuskerud",
    "politiopssbusk",
    "PolitiVestfold",
    "polititelemark",
    "oslopolitiops",
    "politietoslo",
    "ABpolitiops",
    "opsenfollo",
    "RomerikePoliti",
    "PolitiOstfldOPS",
    "politietostfold",
    "OPSGudbrandsdal",
    "politihedmark",
    "HedmarkOPS",
    "PolitiVestoppla"
]

class DefLoc:
    def __init__(self, name, lati, longi):
        self.name = name
        self.lati = lati
        self.longi = longi

defaultLocations = {
    "PolitiVestfinnm": DefLoc(u"Alta", 69.968869, 23.271628),
    "polititroms": DefLoc(u"Tromsø", 69.655747, 18.958503),
    "politiMHPD": DefLoc(u"Harstad", 68.802139, 16.541056),
    "HelgelandOPS": DefLoc(u"Mo i Rana", 66.312778, 14.142786),
    "Hordalandpoliti": DefLoc(u"Bergen", 60.398258, 5.329072),
    "politietsognfj": DefLoc(u"Førde", 61.453717, 5.849684),
    "Rogalandops": DefLoc(u"Stavanger", 58.973473, 5.733923),
    "politiopssbusk": DefLoc(u"Drammen", 59.749054, 10.204468),
    "PolitiVestfold": DefLoc(u"Tønsberg", 59.270361, 10.406768),
    "politietoslo": DefLoc(u"Oslo", 59.934863, 10.749391),
    "ABpolitiops": DefLoc(u"Sandvika", 59.896173, 10.527056),
    "PolitiOstfldOPS": DefLoc(u"Fredrikstad", 59.230846, 10.937062),
    "politietostfold": DefLoc(u"Fredrikstad", 59.230846, 10.937062),
    "PolitiVestoppla": DefLoc(u"Gjøvik", 60.796595, 10.690735)
}


if __name__ == '__main__':
    print("Starting process")
    locationFileName = "locations3.csv"
    generate_default_map(locationFileName)
    print("Done generating default map")
    for u in USERS:
        print("Length of last round (%s): %d" % (user, len(tweets)))
        tweets = []
        user = u
        name_for_location = load_user_location("tweets/%s.json" % user)
        if name_for_location not in locationMapDefault:
            if user not in defaultLocations:
                print("ERROOOOOOR")
                continue
            userLoc = defaultLocations[user]
            name_for_location = userLoc.name
            location_for_user = (userLoc.lati, userLoc.longi)
        else:
            l = locationMapDefault[name_for_location]
            location_for_user = (l.latitude, l.longitude)
        generate_map(locationFileName)
        load_tweets("tweets/%s.json" % user)
        for t in tweets:
            check_tweet_for_location(t)
        save_tweets()
        print("Done with: %s" % u)
