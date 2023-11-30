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
from dotenv import load_dotenv
random.seed(time.time())
os.chdir(os.path.dirname(os.path.abspath(__file__)))

JsonSource = Tracery("bot.json")

TimeBetweenTweets = 60 * 60 * 0.5 # 30 minutes. 60 seconds * 60 minutes * 0.5 hours

load_dotenv(".env")

Client = tweepy.Client(
    consumer_key= os.environ["consumer_key"],
    consumer_secret= os.environ["consumer_secret"],
    access_token= os.environ["access_token"],
    access_token_secret= os.environ["access_token_secret"],
    bearer_token= os.environ["bearer_token"]
)

auth = tweepy.OAuth1UserHandler(
    consumer_key= os.environ["consumer_key"],
    consumer_secret= os.environ["consumer_secret"],
    access_token= os.environ["access_token"],
    access_token_secret= os.environ["access_token_secret"]
)

api = tweepy.API(auth, wait_on_rate_limit=True)

try:
    api.verify_credentials()
    print("Authentication OK")
except:
    print("Error during authentication")

try:
    requestsVer = requests.__version__
    requestsCurrentVersion = requests.get("https://pypi.org/pypi/requests/json").json()["info"]["version"]
    if requestsVer != requestsCurrentVersion:
        print("You should update requests. Try running 'pip install requests --upgrade' in your terminal.")
except:
    print("Couldn't check for requests update. Please check manually with 'pip show requests'.")
    pass

global mediaIDs, mediaList

ENVIROMENT = {}

mediaIDs = []
mediaList = []

def ResetLists():
    global mediaIDs, mediaList
    mediaIDs = []
    mediaList = []
    ENVIROMENT = {}

def GenerateTweet():
    ResetLists()
    tweet = JsonSource.GetMainRule()

    for img in re.findall(r"{img \S+}", tweet):
        # remove {img \S+}
        print("Found image: " + img)
        tweet = tweet.replace(img, "")
        # remove {img}
        img = img.replace("{img ", "").replace("}", "").strip()
        # add to mediaList
        mediaList.append(img)
        
    for video in re.findall(r"{vid \S+}", tweet):
        # remove {vid \S+}
        tweet = tweet.replace(video, "")
        # remove {vid}
        video = video.replace("{vid ", "").replace("}", "").strip()
        # add to mediaList
        mediaList.append(video)
        

    for num in re.findall(r"{rand \d+, \d+}", tweet):
        num = num.replace("{rand ", "").replace("}", "").strip()
        num1, num2 = num.split(",")
        tweet = tweet.replace("{rand " + num + "}", str(random.randint(int(num1), int(num2))))

    # arg 1: rule, arg 2: amount to generate from JsonSource, e.g. {StoreVariable, random thank you!, 3, bool}
    for store in re.findall(r"{StoreVariable, [a-zA-Z0-9 ]+!, \d+, \w+}", tweet):
        bs = store
        store = store.replace("{StoreVariable, ", "").replace("}", "").strip()
        rule, amount, boolean = store.split(", ")
        if rule not in ENVIROMENT:
            ENVIROMENT[rule] = []
        for i in range(int(amount)):
            ENVIROMENT[rule].append(JsonSource.GetRule(f"#{rule}#", isStored=True, isStoredBoolean=(boolean.lower() == "true")))
            
        tweet = tweet.replace(bs, "")
            
        #print("Stored " + str(amount) + " " + rule + "s", ENVIROMENT)

    # GetVariable, arg 1: rule, arg 2: index of variable, e.g. {GetVariable, thank you!, 0}
    for get in re.findall(r"{GetVariable, [a-zA-Z0-9 ]+!, \d+}", tweet):
        bg = get
        get = get.replace("{GetVariable, ", "").replace("}", "").strip()
        rule, index = get.split(", ")
        tweet = tweet.replace(bg, ENVIROMENT[rule][int(index)])

        #print("Got " + rule + " at index " + index, ENVIROMENT)

    for media in mediaList:
        mediaIDs.append(UploadMedia(media))

    if len(mediaIDs) > 0:
        Client.create_tweet(text=tweet, media_ids=mediaIDs)
    else:
        Client.create_tweet(text=tweet)

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