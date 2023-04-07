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
credjson = open("cred.json", "r")
credjson = json.load(credjson)
consumer_key = credjson["consumer_key"]
consumer_secret = credjson["consumer_secret"]
access_token = credjson["access_token"]
access_token_secret = credjson["access_token_secret"]
bearer_token = credjson["bearer_token"]

# Use twitter api V2
Client = tweepy.Client(bearer_token=bearer_token, 
                       consumer_key=consumer_key, 
                       consumer_secret=consumer_secret, 
                       access_token=access_token, 
                       access_token_secret=access_token_secret
)
auth = tweepy.OAuth1UserHandler(
    consumer_key,
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

# Get the current time
now = datetime.datetime.now()

# The time between every new tweet
# This is in seconds, so 3600 is 1 hour
# Default is 30 minutes
# You can change this to whatever you want, but I recommend keeping it at 30 minutes
time_between_tweets = 1800

# read bot.json
botjson = open("bot.json", "r", encoding="utf-8")
botjson = json.load(botjson)

while True:
    now = datetime.datetime.now()

    # get a random tweet from the origin array
    tweet = random.choice(botjson["origin"])
    blahList = []
    mediaIDs = []
    imgList = []
    otherList = []

    # get all the #blah# in the tweet,can also be given as a lowercase
    for blah in re.findall(r"#[a-zA-Z]+#", tweet):
        blahList.append(blah)

    # replace the #blah# with a random word from the blah array
    for blah in blahList:
        choice = random.choice(botjson[blah[1:-1]])
        otherList.append(choice)
        while choice in otherList:
            choice = random.choice(botjson[blah[1:-1]])

        tweet = tweet.replace(blah, choice, 1)
        # check if theres another #blah# in the tweet, can be character, item, etc
        if re.search(r"#[a-zA-Z]+#", tweet):
            for blah in re.findall(r"#[a-zA-Z]+#", tweet):
                choice = random.choice(botjson[blah[1:-1]])
                otherList.append(choice)
                while choice in otherList:
                    choice = random.choice(botjson[blah[1:-1]])

                tweet = tweet.replace(blah, choice, 1)
        #print(f"Replaced {blah} with {choice}")

    # get all the {img link} in the tweet
    for img in re.findall(r"{img \S+}", tweet):
        imgList.append(img)
        # remove it from the tweet
        tweet = tweet.replace(img, "")

    for img in imgList:
        # download the image w/ requests
        image = img.split("{img ")[1]
        image = image.split("}")[0]
        image_name = image.split("/")[-1]
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
        media = api.media_upload(image_name)
        print(f"Uploaded image: {image_name}")
        mediaIDs.append(media.media_id)

        # replace the {img link} with nothing
        tweet = tweet.replace(img, "")

    # tweet the tweet
    try:
        Client.create_tweet(text=tweet, media_ids=mediaIDs)
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
        try:
            os.remove(image_name)
        except:
            try:
                os.remove("temp.png")
            except:
                print("Couldn't delete image; it probably doesn't exist")

    # wait for the time between tweets
    time.sleep(time_between_tweets)

