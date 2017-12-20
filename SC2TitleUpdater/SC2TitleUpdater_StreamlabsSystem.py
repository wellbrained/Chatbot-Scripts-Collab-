"""
###############
(c) Copyright
###############
Brain - www.twitch.tv/wellbrained
Burny - www.twitch.tv/burnysc2
All rights reserved. You may edit the files for personal use only.
"""

#---------------------------------------
#	Import Libraries
#---------------------------------------
import sys
import datetime
import json
import time
import os
from collections import defaultdict
import threading
import clr
import codecs


#---------------------------------------
#	[Required]	Script Information
#---------------------------------------
ScriptName = "SCII - Title Updater"
Website = "https://www.brains-world.eu"
Description = "Update your Streamtitle for every StarCraft II Mode and create custom text files."
Creator = "Brain & Burny"
Version = "1.0.2"

#---------------------------------------
#	Set Variables
#---------------------------------------
debuggingMode = True
configFile = "SC2TitleUpdaterConfig.json"
enabledTitleUpdater = False
enabledOverlayUpdater = False
enabledMatchHistoryUpdater = False

titleUpdate = {
	"channel": "",
	"clientId": "",
	"oauth": "",
	"inGameIds": [],
	"rankedFtwUrl": "",

	"titleInGameAsPlayer": "",
	"titleInGameAsCaster": "",
	"titleInGameAsOther": "",
	"titleInMenu": "",
	"titleIn1v1Replay": "",

	"overlayText1ByUser": "",
	"overlayText2ByUser": "",

	"overlayText11": "",
	"overlayText12": "",
	"overlayText13": "",

	"overlayText21": "",
	"overlayText22": "",
	"overlayText23": "",

	"overlayText1Written": "",
	"overlayText2Written": "",

	"overlayText11Written": "",
	"overlayText21Written": "",

	"overlayText1path": "..\..\Files\SC2TitleUpdater_OverlayText1.txt",
	"overlayText2path": "..\..\Files\SC2TitleUpdater_OverlayText2.txt",
	"overlayText11path": "..\..\Files\SC2TitleUpdater_OverlayText3.txt",
	"overlayText21path": "..\..\Files\SC2TitleUpdater_OverlayText4.txt",

	"gameUrl": "http://localhost:6119/game",
	"uiUrl": "http://localhost:6119/ui",

	"mmr": "0",
	"titleLast": "",
	"titleCurrent": "",

	"gameResponse": {},
	"uiResponse": {},
	"sc2ApiResponseDone": 0,
	"updatedGameApiData": 0,

	"updateInterval": 5,
	"mmrUpdateInterval": 300,

	"timeSinceLastUpdate": time.time(),
	"timeSinceLastMMRupdate": 0,
	"latestApiUpdateTimestamp": 0,
}
apiData = defaultdict(lambda: "")
settings = {}
variables = {
	"$matchup$": "",
	"$gamemins$": "",
	"$gamesecs$": "",
	"$race1$": "",
	"$race2$": "",
	"$player1$": "",
	"$player2$": "",
	"$mymmr$": "",
}

#---------------------------------------
#	[Required] Intialize Data (Only called on Load)
#---------------------------------------
def Init():
	global titleUpdate, settings

	path = os.path.dirname(__file__)
	with codecs.open(os.path.join(path, configFile), encoding='utf-8-sig', mode='r') as file:
		settings = json.load(file, encoding='utf-8-sig')
	settings["inGameIds"] = []
	settings["inGameIds"].append(settings["bnetUsername1"].lower())
	settings["inGameIds"].append(settings["bnetUsername2"].lower())
	settings["inGameIds"].append(settings["bnetUsername3"].lower())
	settings["inGameIds"].append(settings["bnetUsername4"].lower())
	settings["inGameIds"].append(settings["bnetUsername5"].lower())
	settings["channel"] = Parent.GetChannelName()
	GetMmrFromRankedFtw2()
	return

#---------------------------------------
# Reload Settings on Save
#---------------------------------------
def ReloadSettings(jsonData):
	Init()
	return

#---------------------------------------
#	[Required] Tick Function
#---------------------------------------
def Tick():
	global titleUpdate, variables

	t1 = time.time()
	if t1 - titleUpdate["timeSinceLastMMRupdate"] > titleUpdate["mmrUpdateInterval"]:
		titleUpdate["timeSinceLastMMRupdate"] = t1
		threading.Thread(target=GetMmrFromRankedFtw2, args=()).start()

	if t1 - titleUpdate["timeSinceLastUpdate"] > titleUpdate["updateInterval"]:
		titleUpdate["timeSinceLastUpdate"] = t1
		response = GetSc2ApiResponse()
		if response:
			threading.Thread(target=UpdateTwitchTitle, args=()).start()
	return

def GetSc2ApiResponse():
	global titleUpdate
	try:
		gameResponse = json.loads(json.loads(Parent.GetRequest(titleUpdate["gameUrl"], {}))['response'])
		uiResponse = json.loads(json.loads(Parent.GetRequest(titleUpdate["uiUrl"], {}))['response'])

		time1 = time.time()
		if titleUpdate["latestApiUpdateTimestamp"] < time1:
			titleUpdate["latestApiUpdateTimestamp"] = time1
			if ProcessClientApiData(gameResponse, uiResponse):
				return True
	except Exception as e:
		print("Unknown error while attempting to get SC2API response", e)
	return False

def ProcessClientApiData(gameResponse, uiResponse):
	global apiData, titleUpdate, settings, variables
	try:
		if len(gameResponse["players"]) == 2:
			apiData["player1Race"] = gameResponse["players"][0]["race"][0].upper()
			apiData["player2Race"] = gameResponse["players"][1]["race"][0].upper()
			apiData["player1Name"] = gameResponse["players"][0]["name"]
			apiData["player2Name"] = gameResponse["players"][1]["name"]
			apiData["player1Result"] = gameResponse["players"][0]["result"].lower()
			apiData["player2Result"] = gameResponse["players"][1]["result"].lower()
			apiData["ingameMins"], apiData["ingameSecs"] = divmod(int(gameResponse["displayTime"]), 60)

			if apiData["player1Name"].lower() in settings["inGameIds"]:
				apiData["streamerIsInValid1v1Game"] = True
			elif apiData["player2Name"].lower() in settings["inGameIds"]:
				apiData["player1Race"], apiData["player2Race"] = apiData["player2Race"], apiData["player1Race"]
				apiData["player1Name"], apiData["player2Name"] = apiData["player2Name"], apiData["player1Name"]
				apiData["player1Result"], apiData["player2Result"] = apiData["player2Result"], apiData["player1Result"]
				apiData["streamerIsInValid1v1Game"] = True
			else:
				apiData["streamerIsInValid1v1Game"] = False

			apiData["matchup"] = apiData["player1Race"] + "v" + apiData["player2Race"]

			tempMmr = variables["$mymmr$"]
			variables = {
				"$matchup$": apiData["matchup"],
				"$gamemins$": str(apiData["ingameMins"]),
				"$gamesecs$": str(apiData["ingameSecs"]),
				"$race1$": apiData["player1Race"],
				"$race2$": apiData["player2Race"],
				"$player1$": apiData["player1Name"],
				"$player2$": apiData["player2Name"],
				"$mymmr$": tempMmr,
			}

		if uiResponse["activeScreens"] == []:
			if len(gameResponse["players"]) == 2:
				if gameResponse["isReplay"]:
					apiData["inStarcraftLocation"] = "1v1Replay"
					titleUpdate["titleCurrent"] = ReplaceVariables(settings["titleIn1v1Replay"])
				else:
					if apiData["streamerIsInValid1v1Game"]:
						apiData["inStarcraftLocation"] = "1v1AsPlayer"
						titleUpdate["titleCurrent"] = ReplaceVariables(settings["titleInGameAsPlayer"])
					else:
						apiData["inStarcraftLocation"] = "1v1AsCaster"
						titleUpdate["titleCurrent"] = ReplaceVariables(settings["titleInGameAsCaster"])
			else:
				apiData["inStarcraftLocation"] = "other"
				titleUpdate["titleCurrent"] = ReplaceVariables(settings["titleInGameAsOther"])
		else:
			apiData["inStarcraftLocation"] = "menu"
			titleUpdate["titleCurrent"] = ReplaceVariables(settings["titleInMenu"])
		return True

	except Exception as e:
		print("Unknown error while attempting to collect data from SC2 API:", e)
	return False

def ReplaceVariables(string):
	global variables
	for variable, text in variables.items():
		string = string.replace(variable, str(text))
	return string

def UpdateTwitchTitle():
	global titleUpdate, settings, apiData

	if settings["enabledTitleUpdater"] and titleUpdate["titleLast"] != titleUpdate["titleCurrent"]:
		try:
			titleUpdate["titleLast"] = titleUpdate["titleCurrent"]
			print("Debug: trying to update title to:", titleUpdate["titleLast"])

			headers = {
				"Accept": "application/vnd.twitchtv.v5+json",
				"Client-ID": settings["clientID"],
				"Authorization": "OAuth {}".format(settings["oauth"])
			}
			r = Parent.GetRequest("https://api.twitch.tv/kraken/user", headers)
			pr = json.loads(r)
			if pr["status"] == 200: # if true -> successful
				prm = json.loads(pr["response"])
				streamerId = prm["_id"]
				payload = {
					"channel": {
						"status": titleUpdate["titleLast"],
						"game": "StarCraft II"
					}
				}
				r = Parent.PutRequest("https://api.twitch.tv/kraken/channels/" + streamerId, headers, payload, True)
				pr = json.loads(r)
				if pr["status"] == 200: #if true -> successful
					pass
					#Parent.SendTwitchMessage("Successfully updated channel status and game.")

		except Exception as e:
			print("Unknown error while attempting to update twitch title:", e)

	if settings["enabledOverlayUpdater"]:
		path = os.path.dirname(__file__)
		try:
			if titleUpdate["overlayText1Written"] != ReplaceVariables(settings["overlayText1"]):
				titleUpdate["overlayText1Written"] = ReplaceVariables(settings["overlayText1"])
				print("Debug: trying to write overlay file 1:", titleUpdate["overlayText1Written"])
				with codecs.open(os.path.join(path, titleUpdate["overlayText1path"]), encoding='utf-8-sig', mode='w+') as file:
					file.write(titleUpdate["overlayText1Written"])
					
			if titleUpdate["overlayText2Written"] != ReplaceVariables(settings["overlayText2"]):
				titleUpdate["overlayText2Written"] = ReplaceVariables(settings["overlayText2"])
				print("Debug: trying to write overlay file 2:", titleUpdate["overlayText2Written"])
				with codecs.open(os.path.join(path, titleUpdate["overlayText2path"]), encoding='utf-8-sig', mode='w+') as file:
					file.write(titleUpdate["overlayText2Written"])

			if (titleUpdate["overlayText11Written"] != ReplaceVariables(settings["overlayText11"])
				and apiData["inStarcraftLocation"] == "menu"):
				titleUpdate["overlayText11Written"] = ReplaceVariables(settings["overlayText11"])
				print("Debug: trying to write overlay file 3:", titleUpdate["overlayText11Written"])
				with codecs.open(os.path.join(path, titleUpdate["overlayText11path"]), encoding='utf-8-sig', mode='w+') as file:
					file.write(titleUpdate["overlayText11Written"])					
			elif (titleUpdate["overlayText11Written"] != ReplaceVariables(settings["overlayText12"])
				and apiData["inStarcraftLocation"] == "1v1AsPlayer"):
				titleUpdate["overlayText11Written"] = ReplaceVariables(settings["overlayText12"])
				with codecs.open(os.path.join(path, titleUpdate["overlayText11path"]), encoding='utf-8-sig', mode='w+') as file:
					file.write(titleUpdate["overlayText11Written"])
			elif (titleUpdate["overlayText11Written"] != ReplaceVariables(settings["overlayText13"])
				and apiData["inStarcraftLocation"] == "1v1AsCaster"):
				titleUpdate["overlayText11Written"] = ReplaceVariables(settings["overlayText13"])
				with codecs.open(os.path.join(path, titleUpdate["overlayText11path"]), encoding='utf-8-sig', mode='w+') as file:
					file.write(titleUpdate["overlayText11Written"])

			if (titleUpdate["overlayText21Written"] != ReplaceVariables(settings["overlayText21"])
				and apiData["inStarcraftLocation"] == "menu"):
				titleUpdate["overlayText21Written"] = ReplaceVariables(settings["overlayText21Written"])
				print("Debug: trying to write overlay file 3:", titleUpdate["overlayText11Written"])
				with codecs.open(os.path.join(path, titleUpdate["overlayText21path"]), encoding='utf-8-sig', mode='w+') as file:
					file.write(titleUpdate["overlayText21Written"])

			elif (titleUpdate["overlayText21Written"] != ReplaceVariables(settings["overlayText22"])
				and apiData["inStarcraftLocation"] == "1v1AsPlayer"):
				titleUpdate["overlayText21Written"] = ReplaceVariables(settings["overlayText22"])
				with codecs.open(os.path.join(path, titleUpdate["overlayText21path"]), encoding='utf-8-sig', mode='w+') as file:
					file.write(titleUpdate["overlayText21Written"])

			elif (titleUpdate["overlayText21Written"] != ReplaceVariables(settings["overlayText23"])
				and apiData["inStarcraftLocation"] == "1v1AsCaster"):
				titleUpdate["overlayText21Written"] = ReplaceVariables(settings["overlayText23"])
				with codecs.open(os.path.join(path, titleUpdate["overlayText21path"]), encoding='utf-8-sig', mode='w+') as file:
					file.write(titleUpdate["overlayText21Written"])
		except:
			print("No permission to write file in path:", os.path.dirname(os.path.join(path, titleUpdate["overlayText1path"])))
	return

def GetMmrFromRankedFtw():
	global variables, settings
	t0 = time.time()
	rankedFtwUrl = settings["rankedFtwUrl"]

	try:
		if rankedFtwUrl == "":
			return

		teamId = rankedFtwUrl.split("=")[-1]
		request = json.loads(Parent.GetRequest(rankedFtwUrl, {}))["response"]

		print("running getting mmr function")
		contentList = request.split("\n")

		integers = [str(x) for x in range(10)]
		grabNextNumber = False
		thisTeam = False
		mmr = ""

		for line in contentList: #loop over the content website
			if "team/"+teamId in line: #once we find this string in line, then we have the team found
				thisTeam = True
			if thisTeam and '<img class="race"' in line: #after this line the mmr is displayed
				grabNextNumber = True
			if grabNextNumber and '<td class="number">' in line: #mmr is displayed in this line, so parse it!
				for i in line: #there are only integers in this line
					if i in integers:
						mmr += i
				variables["$mymmr$"] = mmr
				print("Successfully obtained mmr:", str(mmr))
				# Parent.SendTwitchMessage("time required: {}".format(time.time() - t0))
				return mmr
	

	except Exception as e:
		print("Error while grabbing MMR from rankedftw.com:", e)

	return "-1"

def GetMmrFromRankedFtw2():
	import re
	global variables, settings
	t0 = time.time()
	rankedFtwUrl = settings["rankedFtwUrl"]
	request = json.loads(Parent.GetRequest(rankedFtwUrl, {}))["response"]

	teamId = rankedFtwUrl.split("=")[-1]

	# Pattern for fetching MMR
	pattern = re.compile(r"""<tr onclick="window\.location='\/team\/""" + str(teamId) + r"""\/';".*?>.*?<td class="player">.*?<\/td><td class="number">([0-9]+)<\/td>(:?<td class="number">[0-9\.%]+\S*?<\/td>){6}<\/tr>""")

	# Normalize response - it simplifies the regex pattern for MMR fetching
	request = re.sub(r'[\n\t]+|\s{2,}', '', request).lower()

	match = pattern.search(request)

	mmr = match.group(1) if match else ''
	variables["$mymmr$"] = mmr
	# Parent.SendTwitchMessage("time required: {}".format(time.time() - t0))

#---------------------------------------
#	[Required] Execute Data / Process Messages
#---------------------------------------
def Execute(data):
	return

def Unload():
	global titleUpdate
	path = os.path.dirname(__file__)
	for file in ["overlayText1path", "overlayText2path", "overlayText11path", "overlayText21path"]:
		with codecs.open(os.path.join(path, titleUpdate[file]), encoding='utf-8-sig', mode='w+') as file:
			file.write(" ")
	return


def OpenClientIDLink():
	os.startfile("https://www.twitch.tv/kraken/oauth2/clients/new")

def OpenOauthLink():
	os.startfile("https://api.twitch.tv/kraken/oauth2/authorize?response_type=token&client_id=" + settings["clientID"] + "&redirect_uri=http://localhost&scope=channel_editor&scope=user_read+channel_editor")

def Debug(message):
	if debuggingMode:
		Parent.Log("TitleUpd", message)
