#---------------------------------------
#    Import Libraries
#---------------------------------------
import json
import os
import time
import clr
import codecs
import sys, base64, zlib, collections


#---------------------------------------
#    [Required]    Script Information
#---------------------------------------
ScriptName = "LiveTweeter"
Website = "https://burnysc2.github.io"
Description = "Tweet when going live"
Creator = "Burny & Brain"
Version = "1.0.1"

configFile = "settings.json"
settings = {
    "successfullyLoaded": False
}
tweetData = {}
scriptData = {
    "timestampLiveSince": 0,
    "timestampOfflineSince": 0,
    "timestampTweetSent": 0,
    "tweetTimestamp": 0,
    "tweetAmountRemaining": 0,
    "twitchMsg": ""
}

def Init():
    global settings, tweetData

    path = os.path.dirname(__file__)
    try:
        with codecs.open(os.path.join(path, configFile), encoding='utf-8-sig', mode='r') as file:
            settings = json.load(file, encoding='utf-8-sig')
        settings["successfullyLoaded"] = True
    except:
        return

    tweetData = {
        "pathPython": settings["txtPathPython"].strip(),
        "pathScript": os.path.join(path, "TweetScript.py"),
        "pathTweetMessage": os.path.join(path, "tweetMessage.txt"),
        "consumer_key": settings["txtConsumerKey"].strip(),
        "consumer_secret": settings["txtConsumerSecret"].strip(),
        "access_token": settings["txtAccessToken"].strip(),
        "access_token_secret": settings["txtAccessTokenSecret"].strip(),
    }
    
    if os.path.isfile(tweetData["pathTweetMessage"]):
        with open(tweetData["pathTweetMessage"], mode="r") as f:
            tweetData["tweetText"] = f.read().decode().rstrip("\n")
    else:
        with open(tweetData["pathTweetMessage"], mode="w+") as f:
            f.write("Title: $title\nGame: $game\nMessage: $message\n\n$url")
        tweetData["tweetText"] = "Title: $title\nGame: $game\nMessage: $message\n\n$url"

#---------------------------------------
#    [Required] Execute Data / Process Messages
#---------------------------------------
def Execute(data):
    return

#---------------------------------------
# Reload Settings on Save
#---------------------------------------
def ReloadSettings(jsonData):
    Init()
    return

#---------------------------------------
#    [Required] Tick Function
#---------------------------------------
def Tick():
    global scriptData

    if settings["successfullyLoaded"] and settings["cbTweetWhenGoingLive"]:
        if Parent.IsLive():
            if settings["cbPostMsgMultipleTimes"]:
                if scriptData["tweetAmountRemaining"] > 0 and time.time() - scriptData["tweetTimestamp"] > settings["sliderRTInterval"] * 60 and scriptData["twitchMsg"] != "":
                    scriptData["tweetAmountRemaining"] -= 1
                    scriptData["tweetTimestamp"] = time.time()
                    Parent.SendTwitchMessage(scriptData["twitchMsg"])

            if settings["cbTweetWhenGoingLive"] and time.time() - scriptData["timestampOfflineSince"] > settings["sliderNewTweetAfterBreak"] * 60:
                sendTweet()
            scriptData["timestampOfflineSince"] = time.time()
        else:
            scriptData["timestampLiveSince"] = time.time()
            scriptData["tweetAmountRemaining"] = 0
    return


def ScriptToggled(state):
    return

def btnOpenReadme():
    location = os.path.join(os.path.dirname(__file__), "README.txt")
    if os.path.isfile(location):
        os.startfile(location)
    return

def btnOpenTweetMessageFile():
    global tweetData
    location = os.path.join(os.path.dirname(__file__), "tweetMessage.txt")
    if os.path.isfile(location):
        os.startfile(location)
    return

def btnSendTweet():
    sendTweet()
    return

def sendTweet():
    global tweetData, scriptData, settings
    path = os.path.dirname(__file__)

    if settings["successfullyLoaded"]:
        if os.path.isfile(tweetData["pathTweetMessage"]):
            with open(tweetData["pathTweetMessage"], mode="r") as f:
                tweetData["tweetText"] = f.read().decode().rstrip("\n")

            if tweetData["tweetText"] != "Default Test Tweet":
                scriptData["timestampTweetSent"] = time.time()
                scriptData["timestampOfflineSince"] = time.time()
                
                # Replace $message with textfield 'Message for Tweet'
                tweetData["tweetText"] = tweetData["tweetText"].replace("$message", settings["txtTweetContent"])
                # Replace $url with the twitch channel
                tweetData["tweetText"] = tweetData["tweetText"].replace("$url", "https://www.twitch.tv/" + Parent.GetChannelName())
                # Replace $title with current set title on twitch
                jsonData = json.loads(Parent.GetRequest("https://decapi.me/twitch/title/" + Parent.GetChannelName(), {}))
                if jsonData["status"] == 200:
                    tweetData["tweetText"] = tweetData["tweetText"].replace("$title", jsonData["response"])
                # Replace $game with current set game on twitch
                jsonData = json.loads(Parent.GetRequest("https://decapi.me/twitch/game/" + Parent.GetChannelName(), {}))
                if jsonData["status"] == 200:
                    tweetData["tweetText"] = tweetData["tweetText"].replace("$game", jsonData["response"])
                

                tweetData["tweetText"] = tweetData["tweetText"][:280]
                Parent.Log("Tweeter", "Sending Tweet!")

                encodedData = encodeBlueprint(tweetData)
                encodedResponse = os.popen("cmd /C \"\"{}\" \"{}\" \"{}\"\"".format(tweetData["pathPython"], tweetData["pathScript"], encodedData)).read()
                try:
                    response = decodeBlueprint(encodedResponse)
                    
                    if settings["cbPostTweetInChat"]:
                        tweetUrl = "https://twitter.com/{}/status/{}".format(response["user"]["screen_name"], response["id_str"])
                        string = settings["txtTweetLinkInChat"].replace("$tweetUrl", tweetUrl)
                        scriptData["twitchMsg"] = string[:490]
                        scriptData["tweetTimestamp"] = time.time()
                        scriptData["tweetAmountRemaining"] = settings["sliderRTAmount"]
                        Parent.SendTwitchMessage(string[:490])
                except Exception as e:
                    Parent.Log("TweeterScript", "Error: {}".format(e))
                    pass
            else:
                pass
        else:
            pass

def decodeBlueprint(blueprintString):
    version_byte = blueprintString[0]
    decoded = base64.b64decode(blueprintString[1:])    
    json_str = zlib.decompress(decoded).decode()
    data = json.loads(json_str, object_pairs_hook=collections.OrderedDict)
    return data

def encodeBlueprint(data, level=6):
    json_str = json.dumps(data)
    encoded = zlib.compress(json_str.encode(), level)
    blueprintString = base64.b64encode(encoded)
    return "0" + blueprintString

def OpenTwitterApp():
	os.startfile("https://apps.twitter.com/app/new")


def ExecuteCmd():
    global settings
    os.system("{} -m pip install requests requests_oauthlib".format(settings['txtPathPython']))
