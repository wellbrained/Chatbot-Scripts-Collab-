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
ScriptName = "Slots Game"
Website = "https://www.brains-world.eu"
Description = "Slots Game"
Creator = "Brain"
Version = "1.1.2"

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
			"onUserCooldown": "$user the command is still on user cooldown for $cd seconds!"
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
	global emotes, settings, user, ScriptName

	if data.IsChatMessage():
		if (data.GetParam(0).lower() == settings["command"]
			and Parent.HasPermission(data.User, settings["permission"], "")
			and settings["costs"] <= Parent.GetPoints(data.User)):

			tempResponseString = ""
			user = data.User
			cd = ""

			if settings["useCooldown"] and (Parent.IsOnCooldown(ScriptName, settings["command"]) or Parent.IsOnUserCooldown(ScriptName, settings["command"], user)):
				if Parent.GetCooldownDuration(ScriptName, settings["command"]) > Parent.GetUserCooldownDuration(ScriptName, settings["command"], user):
					cd = Parent.GetCooldownDuration(ScriptName, settings["command"])
					tempResponseString = settings["onCooldown"]
				else:
					cd = Parent.GetUserCooldownDuration(ScriptName, settings["command"], user)
					tempResponseString = settings["onUserCooldown"]
				tempResponseString = tempResponseString.replace("$cd", str(cd))
			else:
				Parent.RemovePoints(user, settings["costs"])

				random.shuffle(emotes)
				slot1 = random.choice(emotes)
				slot2 = random.choice(emotes)
				slot3 = random.choice(emotes)
				slots = [slot1, slot2, slot3]

				emotesString = " ".join(slots)
				reward = ""

				if slots.count(slot1) == 3:
					if slot1 == settings["superEmote"]:
						tempResponseString = (settings["responseSuperJackpot"])
						Parent.AddPoints(user, int(settings["rewardSuperJackpot"]))
						reward = settings["rewardSuperJackpot"]
					else:
						tempResponseString = settings["responseJackpot"]
						Parent.AddPoints(user, int(settings["rewardJackpot"]))
						reward = settings["rewardJackpot"]
				elif (slot1 == slot2 or slot2 == slot3):
					tempResponseString = settings["responseWon"]
					Parent.AddPoints(user, int(settings["rewardTwoSame"]))
					reward = settings["rewardTwoSame"]
				elif (slot1 == slot3):
					tempResponseString = settings["responseReroll"]
					Parent.AddPoints(user, int(settings["costs"]))
					reward = settings["costs"]
				else:
					tempResponseString = settings["responseLost"]
					reward = settings["costs"]

				tempResponseString = tempResponseString.replace("$slots", " " + emotesString + " ")
				tempResponseString = tempResponseString.replace("$reward", str(reward))

			tempResponseString = tempResponseString.replace("$user", user)
			tempResponseString = tempResponseString.replace("$currency", Parent.GetCurrencyName())

			Parent.AddUserCooldown(ScriptName, settings["command"], user, settings["userCooldown"])
			Parent.AddCooldown(ScriptName, settings["command"], settings["cooldown"])

			Parent.SendTwitchMessage(tempResponseString)
	return

#---------------------------------------
# Reload Settings on Save
#---------------------------------------
def ReloadSettings(jsonData):
	global responses, settings, configFile, emotes

	Init()

	twitchEmotes = set()
	# Grab the list of available Twitch emotes
	jsonData = json.loads(Parent.GetRequest("https://twitchemotes.com/api_cache/v3/global.json", {}))
	if jsonData["status"] == 200:
		twitchEmotes.update(set(json.loads(jsonData["response"]).keys()))

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

	invalidEmotes = []
	for emote in emotes:
		if emote not in twitchEmotes:
			invalidEmotes.append(emote)
	invalidEmotesString = ", ".join(invalidEmotes)

	if len(invalidEmotes) > 0:
		MessageBox = ctypes.windll.user32.MessageBoxW
		MessageBox(0, "Invalid Emotes: " + str(invalidEmotesString), u"Invalid Emote", 0)

	return

#---------------------------------------
#	[Required] Tick Function
#---------------------------------------
def Tick():
	return
