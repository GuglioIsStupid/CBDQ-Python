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

# Verify Credentials
try:
    print("Authentication OK")
except:
    print("Error during authentication")
    sys.exit()

# Get the current time
now = datetime.datetime.now()

# The time between every new tweet
# This is in seconds, so 3600 is 1 hour
# You can change this to whatever you want, but I recommend keeping it at 3600
time_between_tweets = 3600

# read bot.json
botjson = open("bot.json", "r")
botjson = json.load(botjson)

"""
Json format:
{
    "origin":[
        "#Character# is testing the bot!",
        "#Character# and #Character# are both testing the bot!"
    ],
    "Character":[
        "Goku{img media_id}"
    ]
}
"""

while True:
    # get a random tweet from the origin array
    tweet = random.choice(botjson["origin"])

    # get all the characters in the tweet
    characters = re.findall(r"#(.*?)#", tweet)

    # replace all the characters with a random character from the json
    for character in characters:
        tweet = tweet.replace(f"#{character}#", random.choice(botjson[character]))

    # get all the images in the tweet
    images = re.findall(r"{img (.*?)}", tweet)
    mediaIDs = []

    for image in images:
        print(image)
        # get the media ID from the tweet
        tweet.replace(f"{{img {image}}}", "")

    # Since you can't upload images to twitter with API v2, use media ID's instead of links
    # get the tweet length
    tweet_length = len(tweet)

    # tweet the tweet
    try:
        Client.create_tweet(text=tweet, media_ids=[16_1211797899316740096])
        print(f"Tweeted: {tweet}")
    except:
        print(f"Tweet failed: {tweet}")

    # delete the images
    for image in images:
        #os.remove(image)
        pass

    # wait for the time between tweets
    time.sleep(time_between_tweets)

