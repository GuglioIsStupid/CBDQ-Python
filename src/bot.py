"""
CheapBotsDoneQuick-like python bot for Twitter

Why? Because of the recent suspension of CBDQ API Access, I am making a script that can 
simulate the same behavior as the CBDQ bots. This script is obviously a very wip.
JSON schemas are exactly the same as the CBDQ bots, so you can just copy and paste the
JSON files from the CBDQ bots into the same directory as this script and a few script
changes and you're good to go.

- GuglioIsStupid - 2023
"""
import os, json, tweepy, time, random, requests, re, sys
import PIL.Image as Image
from PIL import ImageFile
from PIL import ImageDraw
from PIL import ImageFont

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

cur_version = "1.0.6"
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
api = tweepy.API(auth, wait_on_rate_limit=True)

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
numList = []

grayscale = False
imgToGray = ""

global uppercase
global lowercase

uppercase = False
lowercase = False

def divide_string(string, DivisonAmount:int = 3):
    length = len(string)
    # change the value to change the amount of divisons you want
   
    if length % DivisonAmount == 0:
        return [string[i:i+length//3] for i in range(0, length, length//3)]
    elif length % DivisonAmount == 1:
        return [string[:length//3+1], string[length//3+1//3*2], string[length//3+1//3*2+1:]]
    else:
        return [string[:length//3+2], string[length//3+2:length//3*2+2], string[length//3*2+2:]]
        

def resetLists():
    blahList.clear()
    mediaIDs.clear()
    imgList.clear()
    otherList.clear()
    videoList.clear()
    numList.clear()

def generateTweet():
    tweet = random.choice(botjson["origin"])
    resetLists()

    # get all the #blah# in the tweet,can also be given as a lowercase, uppercase, numbers, special characters, spaces, etc
    for blah in re.findall(r"#[a-zA-Z0-9]+#", tweet):
        blahList.append(blah)

    # check if {grayscale} is anywhere in the tweet
    '''
    if "{grayscale}" in tweet:
        grayscale = True
        tweet = tweet.replace("{grayscale}", "")
    else:
        grayscale = False
    '''
    grayscale = False
    imgToGray = ""
    global uppercase, lowercase

    lowercase = False # sets all the text to lowercase
    uppercase = False # sets all the text to uppercase

    for lowercase_ in re.findall(r"{lowercase}", tweet):
        lowercase = True
        tweet = tweet.replace(lowercase_, "")

    for uppercase_ in re.findall(r"{uppercase}", tweet):
        uppercase = True
        tweet = tweet.replace(uppercase_, "")

    # replace the #blah# with a random word from the blah array
    for blah in blahList:
        choice = random.choice(botjson[blah[1:-1]])
        
        while choice in otherList:
            choice = random.choice(botjson[blah[1:-1]])

        otherList.append(choice)

        print(tweet, blah, choice)
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

    # {grayscale, imgNum/all}, can be a number or all
    for grayscale_ in re.findall(r"{grayscale, \S+}", tweet):
        
        grayscale = True
        imgToGray = str(grayscale_.split(", ")[1].replace("}", ""))
        tweet = tweet.replace(grayscale_, "")

    # get all the {img link} in the tweet, stop at the first }, else its gonna try to do {{img link'}} and fail
    for img in re.findall(r"{img [^}]+}", tweet):
        imgList.append(img)
        # remove it from the tweet
        tweet = tweet.replace(img, "")

    # get all the {vid link} in the tweet
    for vid in re.findall(r"{vid \S+}", tweet):
        videoList.append(vid)
        # remove it from the tweet
        tweet = tweet.replace(vid, "")

    # {rand 1, 10} will give a random number between 1 and 10
    for num in re.findall(r"{rand \d+, \d+}", tweet):
        # generate a random number between the two numbers
        min_num = int(num.split(", ")[0].split("{rand ")[1])
        max_num = int(num.split(", ")[1].split("}")[0])
        num_n = random.randint(min_num, max_num)
        numList.append(num_n)
        # replace the {rand 1, 10} with the random number
        tweet = tweet.replace(num, str(num_n), 1)

    # {grayscale, 'str lol'} # needs to have spaces, special characters, etc
    for divide_ in re.findall(r"{divide, [\S\s]+}", tweet):
        # remove the '' from the strin
        divided_ = divide_.replace("'", "")
        divided_ = divided_.replace("{divide, ", "")
        divided_ = divided_.replace("}", "")
        divided_ = divide_string(divided_)
        dividedConcat = ""
        for divided in divided_:
            # if its not the last item in the list, add a space
            if divided != divided_[-1]:
                dividedConcat += divided + ", "
            else:
                dividedConcat += divided

        print(dividedConcat)

        tweet = tweet.replace(divide_, dividedConcat)

    curImg = 0
    # {text image, font, size, placement, text} (placement is a string, either top, middle, or bottom)
    # use PIL to add text to the image
    # everything after placement is the text
    for text in re.findall(r"{text \S+, \S+, \S+, \S+, '[\S\s]+'}", tweet):
        curImg += 1
        # get the text
        text_ = text.split("{text ")[1].split("}")[0]
        # get the image
        image = text_.split(", ")[0]
        # get the font
        font = text_.split(", ")[1]
        # get the font size
        size = int(text_.split(", ")[2])
        # get the placement
        placement = text_.split(", ")[3]
        # get the text
        text_2 = text_.split(", ")[4].replace("'", "")
        # download the image
        r = requests.get(image, allow_redirects=True)
        try:
            try:
                open("temp.png", "wb").write(r.content)
            except:
                image = "temp.png"
                open("temp.png", "wb").write(r.content)
        except:
            image = "unknown.png"
            open("unknown.png", "wb").write(r.content)
        # open the image
        img = Image.open("temp.png")

        # if grayscale is true, convert the image to grayscale
        if grayscale:
            if str(imgToGray) == "all":
                print("all")
                img = img.convert("L")
            elif str(imgToGray) == str(curImg):
                print("len")
                img = img.convert("L")

        # get the width and height
        width, height = img.size
        # create a draw object
        draw = ImageDraw.Draw(img)
        # get the font
        font = ImageFont.truetype(font, size)
        # get the width and height of the text
        w, h = draw.textsize(text_2, font=font)
        # get the x and y coordinates
        if placement == "top":
            x = (width - w) / 2
            y = 0
        elif placement == "bottom":
            x = (width - w) / 2
            y = height - h
        elif placement == "topleft":
            x = 0
            y = 0
        elif placement == "topright":
            x = width - w
            y = 0
        elif placement == "bottomleft":
            x = 0
            y = height - h
        elif placement == "bottomright":
            x = width - w
            y = height - h
        else:
            x = (width - w) / 2
            y = (height - h) / 2
        # draw the text
        draw.text((x, y), text_2, font=font)
        # save the image
        img.save("temp.png")
        # upload the image to twitter
        try:
            media = api.media_upload("temp.png")
        except:
            media = api.media_upload("unknown.png")
        # add the media id to the mediaIDs list
        mediaIDs.append(media.media_id_string)
        # remove the {text image, font, size, placement, 'text'} from the tweet
        tweet = tweet.replace(text, "")

    curImg = 0
        
    for img in imgList:
        curImg += 1
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

        # if grayscale is true, convert the image to grayscale
        if grayscale:
            if str(imgToGray) == "all":
                img_ = Image.open(image_name)
                img_ = img_.convert("L")
                img_.save(image_name)
            elif str(imgToGray) == str(curImg):
                img_ = Image.open(image_name)
                img_ = img_.convert("L")
                img_.save(image_name)

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
now = 0
while True:
    timer = time.time()
    
    #print(f"Time since last tweet: {timer - (now or 0)}")
    if timer - (now or 0) >= time_between_tweets:
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
        if lowercase:
            tweet = tweet.lower()
        elif uppercase:
            tweet = tweet.upper()
        # tweet the tweet
        try:
            try:
                if len(mediaIDs) == 0:
                    Client.create_tweet(text=tweet)
                else:
                    Client.create_tweet(text=tweet, media_ids=mediaIDs)

                print(f"Tweeted: {tweet}")
            except:
                tweet = generateTweet() # try again
                try:
                    Client.create_tweet(text=tweet, media_ids=mediaIDs)
                    print(f"Tweeted: {tweet}")
                except:
                    print(f"Tweet failed: {tweet}")
                    # print the error
                    print(sys.exc_info()[0])
                    
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
        now = time.time()
    else:
        time.sleep(1)