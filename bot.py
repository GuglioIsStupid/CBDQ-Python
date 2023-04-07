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
# You can change this to whatever you want, but I recommend keeping it at 3600
time_between_tweets = 3600

# read bot.json
botjson = open("bot.json", "r", encoding="utf-8")
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
    now = datetime.datetime.now()
    # get a random tweet from the origin array
    tweet = random.choice(botjson["origin"])
    charList = []

    # get all the characters in the tweet
    characters = re.findall(r"#(.*?)#", tweet)
    print(len(characters))
    

    # replace all the characters with a random character from the json
    for character in characters:
        # get a random character from the json that isn't already in the tweet
        char = random.choice(botjson[character])
        print(char)
        while char in charList:
            char = random.choice(botjson[character])
            print(char)
        charList.append(char)

        # replace the character in the tweet
        tweet = tweet.replace(f"#{character}#", char)
    #break # for testing
    # get all the images in the tweet
    images = re.findall(r"{img (.*?)}", tweet)
    mediaIDs = []

    for image in images:
        # download the image with requests
        r = requests.get(image)
        # get the image name
        image_name = image.split("/")[-1]
        print(image_name)
        # write the image to a file
        try:
            with open(image_name, "wb") as f:
                f.write(r.content)
        except:
            # name it temp.png
            image_name = "temp.png"
            with open(image_name, "wb") as f:
                f.write(r.content)
        
        # upload the image to twitter
        media = api.media_upload(image_name)
        mediaIDs.append(media.media_id)

        # replace the image link with nothing
        tweet = tweet.replace(f"{{img {image}}}", "")

    # Since you can't upload images to twitter with API v2, use media ID's instead of links
    # get the tweet length
    tweet_length = len(tweet)

    # tweet the tweet
    try:
        Client.create_tweet(text=tweet, media_ids=mediaIDs)
        print(f"Tweeted: {tweet}")
    except:
        print(f"Tweet failed: {tweet}")
        # print the error
        print(sys.exc_info()[0])

    # delete the images
    for image in images:
        #os.remove(image)
        pass

    # wait for the time between tweets
    time.sleep(time_between_tweets)

