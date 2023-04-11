"""
CheapBotsDoneQuick-like python bot for Twitter

Why? Because of the recent suspension of CBDQ API Access, I am making a script that can 
simulate the same behavior as the CBDQ bots. This script is obviously a very wip.
JSON schemas are exactly the same as the CBDQ bots, so you can just copy and paste the
JSON files from the CBDQ bots into the same directory as this script and a few script
changes and you're good to go.

- GuglioIsStupid - 2023
"""
import os, json, tweepy, time, datetime, random, requests, re, sys

# Twitter API Keys
# You will need to include your OWN Twitter API keys in a .env file in the same directory 
# as this script. You can get your own Twitter API keys at https://developer.twitter.com/

# get the API keys from the cred.json file
# check if the cred.json file exists
if os.path.exists("cred.json"):
    credjson = open("cred.json", "r")
    credjson = json.load(credjson)
    consumer_key = credjson["consumer_key"]
    consumer_secret = credjson["consumer_secret"]
    access_token = credjson["access_token"]
    access_token_secret = credjson["access_token_secret"]
    bearer_token = credjson["bearer_token"]
    print("Using cred.json file for API keys")
else:
    consumer_key = os.getenv("consumer_key")
    consumer_secret = os.getenv("consumer_secret")
    access_token = os.getenv("access_token")
    access_token_secret = os.getenv("access_token_secret")
    bearer_token = os.getenv("bearer_token")
    print("Using .env file for API keys")

cur_version = "1.0.5"
# if any of the keys are missing, get them from the .env file
if consumer_key == "":
    consumer_key = os.getenv("consumer_key")
if consumer_secret == "":
    consumer_secret = os.getenv("consumer_secret")
if access_token == "":
    access_token = os.getenv("access_token")
if access_token_secret == "":
    access_token_secret = os.getenv("access_token_secret")
if bearer_token == "":
    bearer_token = os.getenv("bearer_token")

# Use twitter api V2
Client = tweepy.Client(bearer_token=bearer_token, 
                       consumer_key=consumer_key, 
                       consumer_secret=consumer_secret, 
                       access_token=access_token, 
                       access_token_secret=access_token_secret
)
auth = tweepy.OAuth1UserHandler(consumer_key,
                                consumer_secret,
                                access_token,
                                access_token_secret
)
# for media upload
api = tweepy.API(auth)

# Verify Credentials
try:
    api.verify_credentials()
    print("Authentication OK")
except:
    print("Error during authentication")
    sys.exit()

# The time between every new tweet
# This is in seconds, so 3600 is 1 hour
# Default is 30 minutes
# You can change this to whatever you want, but I recommend keeping it at 30-60 minutes
time_between_tweets = 1800

# read bot.json
botjson = open("bot.json", "r", encoding="utf-8")
botjson = json.load(botjson)

global blahList
global mediaIDs
global imgList
global otherList
global videoList
blahList = []
mediaIDs = []
imgList = []
otherList = []
videoList = []

def resetLists():
    blahList.clear()
    mediaIDs.clear()
    imgList.clear()
    otherList.clear()
    videoList.clear()

def generateTweet():
    tweet = random.choice(botjson["origin"])
    resetLists()

    # get all the #blah# in the tweet,can also be given as a lowercase
    for blah in re.findall(r"#[a-zA-Z0-9]+#", tweet):
        blahList.append(blah)

    # replace the #blah# with a random word from the blah array
    for blah in blahList:
        choice = random.choice(botjson[blah[1:-1]])
        
        while choice in otherList:
            choice = random.choice(botjson[blah[1:-1]])
        otherList.append(choice)

        tweet = tweet.replace(blah, choice, 1)
        # check if theres another #blah# in the tweet, can be character, item, etc
        if re.findall(r"#[a-zA-Z0-9]+#", tweet):
            for blah in re.findall(r"#[a-zA-Z0-9]+#", tweet):
                choice = random.choice(botjson[blah[1:-1]])
                
                while choice in otherList:
                    choice = random.choice(botjson[blah[1:-1]])
                otherList.append(choice)

                tweet = tweet.replace(blah, choice, 1)
        #print(f"Replaced {blah} with {choice}")

    # get all the {img link} in the tweet
    for img in re.findall(r"{img \S+}", tweet):
        imgList.append(img)
        # remove it from the tweet
        tweet = tweet.replace(img, "")

    # get all the {vid link} in the tweet
    for vid in re.findall(r"{vid \S+}", tweet):
        videoList.append(vid)
        # remove it from the tweet
        tweet = tweet.replace(vid, "")

    for img in imgList:
        # download the image w/ requests
        image = img.split("{img ")[1]
        image = image.split("}")[0]
        image_name = image.split("/")[-1]
        # sometimes the image link can have a query string, so we need to remove it
        if "?" in image_name:
            image_name = image_name.split("?")[0]

        r = requests.get(image, allow_redirects=True)
        try:
            try:
                open(image_name, "wb").write(r.content)
            except:
                image_name = "temp.png"
                open("temp.png", "wb").write(r.content)
        except:
            image_name = "unknown.png"

        # upload the image to twitter
        try:
            media = api.media_upload(image_name)
        except:
            image_name = "unknown.png"
            media = api.media_upload(image_name)
        print(f"Uploaded image: {image_name}")
        mediaIDs.append(media.media_id)

        # replace the {img link} with nothing
        tweet = tweet.replace(img, "")

    for vid in videoList:
        # download the video w/ requests
        video = vid.split("{vid ")[1]
        video = video.split("}")[0]
        video_name = video.split("/")[-1]
        # sometimes the video link can have a query string, so we need to remove it
        if "?" in video_name:
            video_name = video_name.split("?")[0]
        r = requests.get(video, allow_redirects=True)
        try:
            try:
                open(video_name, "wb").write(r.content)
            except:
                video_name = "temp.mp4"
                open("temp.mp4", "wb").write(r.content)
        except:
            video_name = "unknown.mp4"

        # upload the video to twitter
        media = api.media_upload(video_name)
        print(f"Uploaded video: {video_name}")
        mediaIDs.append(media.media_id)

        # replace the {vid link} with nothing
        tweet = tweet.replace(vid, "")

    return tweet

while True:
    try:
        # Check github version for every tweet
        r = requests.get("https://raw.githubusercontent.com/GuglioIsStupid/CBDQ-Python/master/version.txt")
        if r.status_code == 200:
            version = r.text
            if version != cur_version:
                print(f"New version available: {version}")
                print("Download it at https://github.com/GuglioIsStupid/CBDQ-Python")
    except:
        print("Couldn't get version from github")

    # get a random tweet from the origin array
    tweet = generateTweet()

    # tweet the tweet
    try:
        try:
            if len(mediaIDs) == 0:
                Client.create_tweet(text=tweet)
            else:
                Client.create_tweet(text=tweet, media_ids=mediaIDs)
        except:
            # keep generating tweets until it works
            while True:
                tweet = generateTweet()
                try:
                    Client.create_tweet(text=tweet, media_ids=mediaIDs)
                    break
                except:
                    # if error is <tweepy.errors.BadRequest>
                    # print possible error
                    print("Error: ", sys.exc_info()[0])
                    if sys.exc_info()[0] == tweepy.errors.BadRequest:
                        print("""
Possible error!
    1. Tweet is too long
    2. Tweet is a duplicate
    3. API key is invalid
                        """)
                        pass
                    elif sys.exc_info()[0] == tweepy.errors.Forbidden:
                        print("""
Possible error!
    1. API key is invalid
                        """)
                        sys.exit()
        print(f"Tweeted: {tweet}")
    except:
        print(f"Tweet failed: {tweet}")
        # print the error
        print(sys.exc_info()[0])

    # delete the images
    for image in imgList:
        image = image.split("{img ")[1]
        image = image.split("}")[0]
        image_name = image.split("/")[-1]
        # sometimes the image link can have a query string, so we need to remove it
        if "?" in image_name:
            image_name = image_name.split("?")[0]
        try:
            os.remove(image_name)
        except:
            try:
                os.remove("temp.png")
            except:
                print("Couldn't delete image; it probably doesn't exist")

    # delete the videos
    for video in videoList:
        video = video.split("{vid ")[1]
        video = video.split("}")[0]
        video_name = video.split("/")[-1]
        # sometimes the video link can have a query string, so we need to remove it
        if "?" in video_name:
            video_name = video_name.split("?")[0]
        try:
            os.remove(video_name)
        except:
            try:
                os.remove("temp.mp4")
            except:
                print("Couldn't delete video; it probably doesn't exist")

    # wait for the time between tweets
    time.sleep(time_between_tweets)

