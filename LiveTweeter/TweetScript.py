import base64
import requests # pip install requests
from requests_oauthlib import OAuth1 # pip install requests_oauthlib
import sys
import zlib, json
import collections
import os

path = os.path.dirname(__file__)
# with open(os.path.join(path, "temp.json")) as f:
#     a = json.load(f)
#     print(a["user"]["screen_name"])

def decodeBlueprint(blueprintString):
    version_byte = blueprintString[0]
    decoded = base64.b64decode(blueprintString[1:])    
    # json_str = zlib.decompress(decoded) # python 2 version
    json_str = zlib.decompress(decoded).decode() # python 3 version
    data = json.loads(json_str, object_pairs_hook=collections.OrderedDict)
    return data

def encodeBlueprint(data, level=6):
    json_str = json.dumps(data)
    encoded = zlib.compress(json_str.encode(), level)
    blueprintString = base64.b64encode(encoded)
    return "0" + blueprintString


if __name__ == "__main__":
    encodedTweetData = "".join(sys.argv[1:])
    tweetData = decodeBlueprint(encodedTweetData)

    postUrl = "https://api.twitter.com/1.1/statuses/update.json"
    auth = OAuth1(
        tweetData["consumer_key"].strip(),
        tweetData["consumer_secret"].strip(), 
        tweetData["access_token"].strip(),
        tweetData["access_token_secret"].strip())
    status = tweetData["tweetText"]
    r = requests.post(postUrl, auth=auth, data={"status":status})
    # with open(os.path.join(path, "tempTweetScriptOutput.json"), mode="w") as f:
    #     json.dump(r.json(), f, indent=4)
    if r.status_code == 200:
        print(encodeBlueprint(r.json()))
    else:
        # print(r.text)
        pass

    # sys.stdout.write("This is a test\n")
    # sys.stdout.flush()
    sys.exit(0)










