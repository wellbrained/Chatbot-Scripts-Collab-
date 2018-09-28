#---------------------------------------
#	Import Libraries
#---------------------------------------
import clr
import sys
import json
import os
import random
import ctypes
import codecs

#---------------------------------------
#	[Required]	Script Information
#---------------------------------------
ScriptName = "Game - Slots"
Website = "http://www.brains-world.eu"
Description = "Slotmachine game for Twitch chat"
Creator = "Brain"
Version = "1.2.1"

#---------------------------------------
#	Set Variables
#---------------------------------------
configFile = "SlotsConfig.json"
settings = {}
emotes = []
slot1 = ""
slot2 = ""
slot3 = ""
user = ""
responses = []

def ScriptToggled(state):
	return

#---------------------------------------
#	[Required] Intialize Data (Only called on Load)
#---------------------------------------
def Init():
	global responses, settings, configFile, emotes

	path = os.path.dirname(__file__)
	try:
		with codecs.open(os.path.join(path, configFile), encoding='utf-8-sig', mode='r') as file:
			settings = json.load(file, encoding='utf-8-sig')
	except:
		settings = {
			"command": "!slots",
			"permission": "Everyone",
			"costs": 50,
			"rewardTwoSame": 75,
			"rewardJackpot": 250,
			"rewardSuperJackpot": 750,
			"emoteList": "Kappa, LUL, NotLikeThis, WutFace, MingLee, FeelsBadMan",
			"superEmote": " KappaPride",
			"responseLost": "$user pulls the lever and .... [$slots] You lost $reward $currency LUL ",
			"responseWon": "$user pulls the lever and waits for the roll .... [$slots] Even a small win is a win.. ",
			"responseReroll": "$user pulls the lever and waits for the roll .... [$slots] You at least got your points back?!",
			"responseJackpot": "$user pulls the lever and waits for the roll .... [$slots] Jackpot, well done Sir!",
			"responseSuperJackpot": "$user pulls the lever and waits for the roll .... [$slots] SUPER JACKPOT! YOU ARE THE MVP :D",
			"useCooldown": True,
			"cooldown": 60,
			"onCooldown": "$user, the command is still on cooldown for $cd seconds!",
			"userCooldown": 60,
			"onUserCooldown": "$user the command is still on user cooldown for $cd seconds!",
			"responseNotEnoughPoints": "It seems $user has not enough $currency to play the game.",
			"seperator": "",
			"checkTwitchEmotes": True,
			"checkBTTVEmotes": True,
			"checkFFZEmotes": True,
			"ignoreEmoteCheck": False
		}

	emotes = settings["emoteList"].replace(" ","").split(",")
	emotes.append(settings["superEmote"].replace(" ",""))
	emotes = list(set(emotes))

	responses.extend([settings["rewardTwoSame"], settings["rewardJackpot"], settings["rewardSuperJackpot"]])
	try:
		for i in responses:
			int(i)
	except:
		MessageBox = ctypes.windll.user32.MessageBoxW
		MessageBox(0, u"Invalid values", u"Slots Script failed to load. The rewards are not numbers.", 0)
	return


#---------------------------------------
#	[Required] Execute Data / Process Messages
#---------------------------------------
def Execute(data):
	global emotes, settings, userId, username, ScriptName

	if data.IsChatMessage() and data.GetParam(0).lower() == settings["command"] and Parent.HasPermission(data.User, settings["permission"], ""):
		tempResponseString = ""
		userId = data.User			
		username = data.UserName
		cd = ""

		# Check if the User has enough points
		if settings["costs"] > Parent.GetPoints(userId):
			tempResponseString = settings["responseNotEnoughPoints"]
		# Check if there is a cooldown active 
		elif settings["useCooldown"] and (Parent.IsOnCooldown(ScriptName, settings["command"]) or Parent.IsOnUserCooldown(ScriptName, settings["command"], userId)):
			if Parent.GetCooldownDuration(ScriptName, settings["command"]) > Parent.GetUserCooldownDuration(ScriptName, settings["command"], userId):
				cd = Parent.GetCooldownDuration(ScriptName, settings["command"])
				tempResponseString = settings["onCooldown"]
			else:
				cd = Parent.GetUserCooldownDuration(ScriptName, settings["command"], userId)
				tempResponseString = settings["onUserCooldown"]
			tempResponseString = tempResponseString.replace("$cd", str(cd))
		else:
			Parent.RemovePoints(userId, username, settings["costs"])

			random.shuffle(emotes)
			slot1 = random.choice(emotes)
			slot2 = random.choice(emotes)
			slot3 = random.choice(emotes)
			slots = [slot1, slot2, slot3]

			if len(settings["seperator"]) == 0:
				emotesString = " ".join(slots)
			else:
				emoteSeperator = " " + settings["seperator"] + " "
				emotesString = emoteSeperator.join(slots)
			reward = ""

			if slots.count(slot1) == 3:
				if slot1 == settings["superEmote"]:
					tempResponseString = (settings["responseSuperJackpot"])
					Parent.AddPoints(userId, username, int(settings["rewardSuperJackpot"]))
					reward = settings["rewardSuperJackpot"]
				else:
					tempResponseString = settings["responseJackpot"]
					Parent.AddPoints(userId, username, int(settings["rewardJackpot"]))
					reward = settings["rewardJackpot"]
			elif (slot1 == slot2 or slot2 == slot3):
				tempResponseString = settings["responseWon"]
				Parent.AddPoints(userId, username, int(settings["rewardTwoSame"]))
				reward = settings["rewardTwoSame"]
			elif (slot1 == slot3):
				tempResponseString = settings["responseReroll"]
				Parent.AddPoints(userId, username, int(settings["rewardTwoSeperated"]))
				reward = settings["rewardTwoSeperated"]
			else:
				tempResponseString = settings["responseLost"]
				reward = settings["costs"]

			tempResponseString = tempResponseString.replace("$slots", " " + emotesString + " ")
			tempResponseString = tempResponseString.replace("$reward", str(reward))

			Parent.AddUserCooldown(ScriptName, settings["command"], userId, settings["userCooldown"])
			Parent.AddCooldown(ScriptName, settings["command"], settings["cooldown"])

		tempResponseString = tempResponseString.replace("$cost", str(settings["costs"]))
		tempResponseString = tempResponseString.replace("$user", username)
		tempResponseString = tempResponseString.replace("$currency", Parent.GetCurrencyName())

		Parent.SendStreamMessage(tempResponseString)
	return

#---------------------------------------
# Reload Settings on Save
#---------------------------------------
def ReloadSettings(jsonData):
	global responses, settings, configFile, emotes

	Init()

	twitchEmotes = set()

	if settings["ignoreEmoteCheck"]: 
		return

	if settings["checkTwitchEmotes"]:
		# Grab the list of available Twitch emotes
		jsonData = json.loads(Parent.GetRequest("https://twitchemotes.com/api_cache/v3/global.json", {}))
		if jsonData["status"] == 200:
			twitchEmotes.update(set(json.loads(jsonData["response"]).keys()))

		# Grab the list of available Twitch emotes of the users channel
		jsonData = json.loads(Parent.GetRequest("https://decapi.me/twitch/subscriber_emotes/" + Parent.GetChannelName(), {}))
		if jsonData["status"] == 200:
			tempEmoteNames = jsonData["response"].split(" ")
			if tempEmoteNames[0] != "This": #channel has no sub button or sub button + no emotes
				twitchEmotes.update(set(tempEmoteNames))

	if settings["checkBTTVEmotes"]:
		# Grab the list of available BetterTwitchTV emotes on the users channel
		jsonData = json.loads(Parent.GetRequest("https://api.betterttv.net/2/channels/" + Parent.GetChannelName(), {}))
		if jsonData["status"] == 200:
			for emote in json.loads(jsonData["response"])["emotes"]:
				twitchEmotes.add(emote['code'])

		# Grab the list of available global BetterTwitchTV emotes
		jsonData = json.loads(Parent.GetRequest("https://api.betterttv.net/2/emotes", {}))
		if jsonData["status"] == 200:
			for emote in json.loads(jsonData["response"])["emotes"]:
				twitchEmotes.add(emote['code'])

	if settings["checkFFZEmotes"]:
		# Grab the list of available FFZ emotes	on user channel
		jsonData = json.loads(Parent.GetRequest("https://decapi.me/ffz/emotes/" + Parent.GetChannelName(), {}))
		if jsonData["status"] == 200:
			tempEmoteNames = jsonData["response"].split(" ")
			if tempEmoteNames[0] != "Not": #channel has no emotes
				twitchEmotes.update(set(tempEmoteNames))

	invalidEmotes = []
	for emote in emotes:
		if emote not in twitchEmotes:
			invalidEmotes.append(emote)
	invalidEmotesString = ", ".join(invalidEmotes)

	if len(invalidEmotes) > 0:
		MessageBox = ctypes.windll.user32.MessageBoxW
		MessageBox(0, "Invalid Emotes: " + str(invalidEmotesString), u"Invalid Emote", 0)

	return

def OpenReadMe():
    location = os.path.join(os.path.dirname(__file__), "README.txt")
    os.startfile(location)
    return

#---------------------------------------
#	[Required] Tick Function
#---------------------------------------
def Tick():
	return
