from tracery import Tracery
import sys

try:
    import requests
except:
    print("You need to install requests. Try running 'pip install requests' in your terminal.")
    sys.exit(1)

try:
    import tweepy
except:
    print("You need to install tweepy. Try running 'pip install tweepy' in your terminal.")
    sys.exit(1)

import os, sys, time, re, random
random.seed(time.time())
os.chdir(os.path.dirname(os.path.abspath(__file__)))

JsonSource = Tracery("bot.json")

TimeBetweenTweets = 60 * 60 * 0.5 # 30 minutes. 60 seconds * 60 minutes * 0.5 hours

env = {
    "consumer_key": "",
    "consumer_secret": "",
    "access_token": "",
    "access_token_secret": "",
    "bearer_token": ""
}

with open(".env", "r") as f:
    for line in f.readlines():
        if line.startswith("#"):
            continue
        key, value = line.split("=")
        env[key.strip()] = value.strip()

Client = tweepy.Client(
    consumer_key=env["consumer_key"],
    consumer_secret=env["consumer_secret"],
    access_token=env["access_token"],
    access_token_secret=env["access_token_secret"],
    bearer_token=env["bearer_token"]
)

auth = tweepy.OAuth1UserHandler(
    env["consumer_key"],
    env["consumer_secret"],
    env["access_token"],
    env["access_token_secret"]
)

api = tweepy.API(auth, wait_on_rate_limit=True)

try:
    api.verify_credentials()
    print("Authentication OK")
except:
    print("Error during authentication")
    sys.exit(1)

try:
    requestsVer = requests.__version__
    requestsCurrentVersion = requests.get("https://pypi.org/pypi/requests/json").json()["info"]["version"]
    if requestsVer != requestsCurrentVersion:
        print("You should update requests. Try running 'pip install requests --upgrade' in your terminal.")
except:
    print("Couldn't check for requests update. Please check manually with 'pip show requests'.")
    pass

global mediaIDs, mediaList

mediaIDs = []
mediaList = []

def ResetLists():
    global mediaIDs, mediaList
    mediaIDs = []
    mediaList = []

def GenerateTweet():
    ResetLists()
    tweet = JsonSource.GetMainRule()

    for img in re.findall(r"{img \S+}", tweet):
        img = img.replace("{img ", "").replace("}", "").strip()
        tweet = tweet.replace("{img " + img + "}", "")
        if img not in mediaIDs:
            mediaList.append(img)

    for video in re.findall(r"{vid \S+}", tweet):
        video = video.replace("{vid ", "").replace("}", "").strip()
        tweet = tweet.replace("{vid " + video + "}", "")
        if video not in mediaIDs:
            mediaList.append(video)

    for num in re.findall(r"{rand \d+, \d+}", tweet):
        num = num.replace("{rand ", "").replace("}", "").strip()
        num1, num2 = num.split(",")
        tweet = tweet.replace("{rand " + num + "}", str(random.randint(int(num1), int(num2))))

    for media in mediaList:
        mediaIDs.append(UploadMedia(media))

    """ if len(mediaIDs) > 0:
        Client.create_tweet(text=tweet, media_ids=mediaIDs)
    else:
        Client.create_tweet(text=tweet) """

    print("Tweeted: " + tweet)


def UploadMedia(media):
    # remove media if exists
    if os.path.exists("media"):
        os.remove("media")
    # download media
    try:
        r = requests.get(media, allow_redirects=True)
        open("media", "wb").write(r.content)
    except:
        # upload unknown.png 
        open("media", "wb").write(open("unknown.png", "rb").read())
    media = api.media_upload("media")
    return media.media_id

now = 0

if __name__ == "__main__":
    while True:
        if time.time() - (now or 0) >= TimeBetweenTweets:
            GenerateTweet()
            now = time.time()
        else:
            time.sleep(1)